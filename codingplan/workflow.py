"""工作流编排器"""

import json
from pathlib import Path
from typing import Optional

from .agent import run_agent, run_plan, run_ask, check_agent_installed
from .config import get_output_dirs, REQUIREMENT_EXTENSIONS, STEPS
from . import prompts


class WorkflowState:
    """工作流状态（用于断点续传）"""
    def __init__(self, state_file: Path):
        self.state_file = state_file
        self.data: dict = {}

    def load(self):
        if self.state_file.exists():
            with open(self.state_file, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"current_file": None, "current_step": 0, "files_done": []}

    def save(self):
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_output_path(self, base: str, suffix: str) -> Path:
        return self.state_file.parent / "outputs" / f"{base}{suffix}"


def collect_requirement_files(req_dir: Path) -> list[Path]:
    """收集需求目录下的所有需求文件（按名称排序）"""
    files = []
    for ext in REQUIREMENT_EXTENSIONS:
        files.extend(req_dir.glob(f"*{ext}"))
    return sorted(files, key=lambda p: p.name)


def process_single_file(
    req_file: Path,
    project_root: Path,
    dirs: dict,
    resume_from_step: Optional[int] = None,
    scope: Optional[str] = None,
    hint: Optional[str] = None,
) -> bool:
    """
    处理单个需求文件的完整流程

    Returns:
        True 表示成功完成，False 表示失败或中断
    """
    base_name = req_file.stem
    normalized_path = dirs["outputs"] / f"{base_name}-normalized.md"
    req_path = dirs["outputs"] / f"{base_name}-requirements.md"
    outline_path = dirs["outputs"] / f"{base_name}-outline-design.md"
    detail_path = dirs["outputs"] / f"{base_name}-detail-design.md"
    test_design_path = dirs["outputs"] / f"{base_name}-test-design.md"

    start_step = resume_from_step or 1

    # Step 1: 文档规范化
    if start_step <= 1:
        content = req_file.read_text(encoding="utf-8", errors="replace")
        prompt = prompts.step1_normalize(str(req_file), content, hint=hint)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False
        if not normalized_path.exists():
            # Agent 可能用了不同命名，尝试查找
            for f in dirs["outputs"].glob(f"{base_name}*.md"):
                if "normalized" in f.name or f.name == f"{base_name}.md":
                    break

    # Step 2: 需求补全
    if start_step <= 2:
        req_input = normalized_path if normalized_path.exists() else req_file
        prompt = prompts.step2_complete(str(req_file), str(req_input), hint=hint)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 3: 概要设计
    if start_step <= 3:
        req_input = req_path if req_path.exists() else normalized_path
        prompt = prompts.step3_outline(str(req_input), base_name, scope=scope, hint=hint)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 4: 详细设计
    if start_step <= 4:
        ol_input = outline_path if outline_path.exists() else dirs["outputs"] / f"{base_name}-outline-design.md"
        prompt = prompts.step4_detail(str(ol_input), str(req_path), base_name, scope=scope, hint=hint)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 5: 代码实现（Plan 模式）
    if start_step <= 5:
        detail_input = detail_path if detail_path.exists() else dirs["outputs"] / f"{base_name}-detail-design.md"
        prompt = prompts.step5_implement(str(detail_input), str(req_path), scope=scope, hint=hint)
        result = run_plan(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 6: 测试设计
    if start_step <= 6:
        prompt = prompts.step6_test_design(str(req_path), str(detail_path), base_name, scope=scope, hint=hint)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 7: 测试实现
    if start_step <= 7:
        td_input = test_design_path if test_design_path.exists() else dirs["outputs"] / f"{base_name}-test-design.md"
        prompt = prompts.step7_test_impl(str(td_input), scope=scope, hint=hint)
        result = run_plan(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 8: 编译、运行、测试（循环直至成功）
    if start_step <= 8:
        max_retries = 5
        for attempt in range(max_retries):
            prompt = prompts.step8_build_test(scope=scope, hint=hint)
            result = run_agent(prompt, cwd=project_root)
            if result.returncode == 0:
                break
            # 失败时用 Ask 分析
            ask_prompt = f"""
编译/运行/测试失败。请分析失败原因并给出修复建议。
当前是第 {attempt + 1} 次重试。
"""
            run_ask(ask_prompt, cwd=project_root)
        else:
            return False

    # Step 9: 完成度校验
    if start_step <= 9:
        prompt = prompts.step9_validate(str(req_path), scope=scope, hint=hint)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    return True


def process_project_check(project_root: Path, dirs: dict, scope: Optional[str] = None, hint: Optional[str] = None) -> bool:
    """Step 10 & 11: 项目整体检查与补充"""
    prompt = prompts.step10_project_check(scope=scope, hint=hint)
    result = run_agent(prompt, cwd=project_root)
    if result.returncode != 0:
        return False

    prompt = prompts.step11_project_fix(scope=scope, hint=hint)
    result = run_agent(prompt, cwd=project_root)
    return result.returncode == 0


def run_workflow(
    project_root: Path,
    req_dir: Path,
    resume: bool = False,
    single_file: Optional[str] = None,
    scope: Optional[str] = None,
    hint: Optional[str] = None,
) -> int:
    """
    运行完整工作流

    Returns:
        0 成功，1 失败
    """
    if not check_agent_installed():
        print("错误: 未检测到 Cursor Agent。请先安装: curl https://cursor.com/install -fsS | bash")
        return 1

    dirs = get_output_dirs(project_root)
    state_file = project_root / ".codingplan" / "state.json"
    state = WorkflowState(state_file)
    if resume:
        state.load()
        # 恢复时沿用上次的 scope、hint（若本次未指定）
        if scope is None and state.data.get("scope"):
            scope = state.data["scope"]
        if hint is None and state.data.get("hint"):
            hint = state.data["hint"]
    if scope:
        state.data["scope"] = scope
    if hint:
        state.data["hint"] = hint
    if scope or hint:
        state.save()

    files = collect_requirement_files(req_dir)
    if not files:
        print(f"未在 {req_dir} 中找到需求文件（支持: {', '.join(REQUIREMENT_EXTENSIONS)}）")
        return 1

    if single_file:
        files = [f for f in files if f.name == single_file or f.stem == single_file]
        if not files:
            print(f"未找到文件: {single_file}")
            return 1

    if scope:
        print(f"实现范围限制: 仅限 {scope}/ 目录")
    if hint:
        print(f"额外提醒: {hint}")
    print(f"共 {len(files)} 个需求文件待处理")
    for i, req_file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 处理: {req_file.name}")
        success = process_single_file(req_file, project_root, dirs, scope=scope, hint=hint)
        if not success:
            print(f"处理失败: {req_file.name}")
            state.data["current_file"] = str(req_file)
            state.save()
            return 1
        state.data.setdefault("files_done", []).append(str(req_file))
        state.save()

    # 全部需求完成后，执行项目级检查
    print("\n执行项目整体完成度与测试检查...")
    if not process_project_check(project_root, dirs, scope=scope, hint=hint):
        print("项目级检查或补充未完全成功")
        return 1

    print("\n所有需求处理完成。")
    return 0
