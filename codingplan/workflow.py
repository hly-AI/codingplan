"""工作流编排器"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from .agent import run_agent, run_plan, run_ask, check_agent_installed
from . import figma as figma_mod
from . import notify
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
    ui_dir: Optional[Path] = None,
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

    # 提取 Figma 设计信息（需求文件、同目录 .figma.md、UI 设计目录）
    req_dir = req_file.parent
    figma_info = figma_mod.extract_from_req_dir(req_dir, req_file, ui_dir=ui_dir)

    # Step 1: 文档规范化
    if start_step <= 1:
        content = req_file.read_text(encoding="utf-8", errors="replace")
        # 移除 null 字节，避免 subprocess 报 "ValueError: embedded null byte"（PDF 等可能包含）
        content = content.replace("\x00", "")
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
        # 补全后可能新增 Figma 信息，重新提取
        if req_path.exists():
            merged = figma_mod.extract_from_file(req_path)
            for link in merged.links:
                if link not in figma_info.links:
                    figma_info.links.append(link)
            if merged.interaction_desc:
                figma_info.interaction_desc = (figma_info.interaction_desc + "\n\n" + merged.interaction_desc).strip()

    # Step 3: 概要设计
    if start_step <= 3:
        req_input = req_path if req_path.exists() else normalized_path
        prompt = prompts.step3_outline(str(req_input), base_name, scope=scope, hint=hint, figma=figma_info)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 4: 详细设计
    if start_step <= 4:
        ol_input = outline_path if outline_path.exists() else dirs["outputs"] / f"{base_name}-outline-design.md"
        prompt = prompts.step4_detail(str(ol_input), str(req_path), base_name, scope=scope, hint=hint, figma=figma_info)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 5: 代码实现（Plan 模式）
    if start_step <= 5:
        detail_input = detail_path if detail_path.exists() else dirs["outputs"] / f"{base_name}-detail-design.md"
        prompt = prompts.step5_implement(str(detail_input), str(req_path), scope=scope, hint=hint, figma=figma_info)
        result = run_plan(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 6: 测试设计
    if start_step <= 6:
        prompt = prompts.step6_test_design(str(req_path), str(detail_path), base_name, scope=scope, hint=hint, figma=figma_info)
        result = run_agent(prompt, cwd=project_root)
        if result.returncode != 0:
            return False

    # Step 7: 测试实现
    if start_step <= 7:
        td_input = test_design_path if test_design_path.exists() else dirs["outputs"] / f"{base_name}-test-design.md"
        prompt = prompts.step7_test_impl(str(td_input), scope=scope, hint=hint, figma=figma_info)
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


def _format_duration(start_time: datetime) -> str:
    """返回耗时字符串"""
    end_time = datetime.now()
    delta = end_time - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}小时{minutes}分{seconds}秒"
    if minutes > 0:
        return f"{minutes}分{seconds}秒"
    return f"{seconds}秒"


def _print_duration(start_time: datetime) -> str:
    """打印耗时统计，返回耗时字符串"""
    duration_str = _format_duration(start_time)
    end_time = datetime.now()
    print(f"\n结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')} | 总耗时: {duration_str}")
    return duration_str


def process_project_check(project_root: Path, dirs: dict, scope: Optional[str] = None, hint: Optional[str] = None) -> bool:
    """Step 10 & 11: 项目整体检查与补充"""
    prompt = prompts.step10_project_check(scope=scope, hint=hint)
    result = run_agent(prompt, cwd=project_root)
    if result.returncode != 0:
        return False

    prompt = prompts.step11_project_fix(scope=scope, hint=hint)
    result = run_agent(prompt, cwd=project_root)
    return result.returncode == 0


def _has_unfinished_state(state_file: Path, req_dir: Path) -> bool:
    """检测是否存在未完成的状态（同需求目录）"""
    if not state_file.exists():
        return False
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False
    if data.get("completed"):
        return False
    saved_req_dir = data.get("req_dir")
    if saved_req_dir != str(req_dir):
        return False
    return bool(data.get("current_file") or data.get("files_done"))


def run_workflow(
    project_root: Path,
    req_dir: Path,
    ui_dir: Optional[Path] = None,
    resume: bool = False,
    fresh: bool = False,
    single_file: Optional[str] = None,
    scope: Optional[str] = None,
    hint: Optional[str] = None,
    notify_emails: Optional[list[str]] = None,
) -> int:
    """
    运行完整工作流

    Returns:
        0 成功，1 失败
    """
    if not check_agent_installed():
        print("错误: 未检测到 Cursor Agent。请先安装: curl https://cursor.com/install -fsS | bash")
        return 1

    start_time = datetime.now()
    print(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    dirs = get_output_dirs(project_root)
    state_file = project_root / ".codingplan" / "state.json"
    state = WorkflowState(state_file)

    # 自动续传：未传 --fresh 且存在未完成状态时，自动从中断处继续
    if not fresh and _has_unfinished_state(state_file, req_dir):
        resume = True
        print("检测到上次未完成，自动从中断处继续（使用 --fresh 可强制重新开始）")

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
    state.data["req_dir"] = str(req_dir)
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

    # 续传时跳过已完成文件
    if resume:
        files_done_names = {Path(p).name for p in state.data.get("files_done", [])}
        files = [f for f in files if f.name not in files_done_names]
        if files:
            print(f"续传: 跳过 {len(files_done_names)} 个已完成，剩余 {len(files)} 个待处理")

    notify_emails = notify_emails or []
    files_done: list[str] = []

    if scope:
        print(f"实现范围限制: 仅限 {scope}/ 目录")
    if ui_dir and ui_dir.exists():
        print(f"UI 设计目录: {ui_dir}")
    if hint:
        print(f"额外提醒: {hint}")
    if notify_emails:
        print(f"完成后将通知: {', '.join(notify_emails)}")
    print(f"共 {len(files)} 个需求文件待处理")
    for i, req_file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 处理: {req_file.name}")
        success = process_single_file(req_file, project_root, dirs, scope=scope, hint=hint, ui_dir=ui_dir)
        if not success:
            duration_str = _print_duration(start_time)
            print(f"处理失败: {req_file.name}")
            state.data["current_file"] = str(req_file)
            state.save()
            if notify_emails:
                notify.send_workflow_complete(
                    notify_emails,
                    success=False,
                    project_path=str(project_root),
                    files_processed=[str(f) for f in files_done],
                    duration_str=duration_str,
                    error_msg=f"处理失败: {req_file.name}",
                )
            return 1
        files_done.append(req_file.name)
        state.data.setdefault("files_done", []).append(str(req_file))
        state.save()

    # 全部需求完成后，执行项目级检查
    print("\n执行项目整体完成度与测试检查...")
    if not process_project_check(project_root, dirs, scope=scope, hint=hint):
        duration_str = _print_duration(start_time)
        print("项目级检查或补充未完全成功")
        if notify_emails:
            notify.send_workflow_complete(
                notify_emails,
                success=False,
                project_path=str(project_root),
                files_processed=[str(f) for f in files_done],
                duration_str=duration_str,
                error_msg="项目级检查或补充未完全成功",
            )
        return 1

    duration_str = _print_duration(start_time)
    print("\n所有需求处理完成。")
    state.data["completed"] = True
    state.data["current_file"] = None
    state.save()
    if notify_emails:
        notify.send_workflow_complete(
            notify_emails,
            success=True,
            project_path=str(project_root),
            files_processed=[str(f) for f in files_done],
            duration_str=duration_str,
        )
    return 0
