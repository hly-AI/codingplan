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
from .logger import (
    setup_logger,
    log_step_start,
    log_step_end,
    log_workflow_start,
    log_workflow_end,
)

# 步骤名称（用于进度输出与失败诊断）
STEP_NAMES = {
    1: "文档规范化",
    2: "需求补全",
    3: "概要设计",
    4: "详细设计",
    5: "代码实现",
    6: "测试设计",
    7: "测试实现",
    8: "编译运行测试",
    9: "完成度校验",
}


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
) -> tuple[bool, Optional[int], Optional[str]]:
    """
    处理单个需求文件的完整流程

    Returns:
        (成功, 失败步骤号, 失败步骤名)，成功时后两者为 None
    """
    base_name = req_file.stem
    file_name = req_file.name
    logger = setup_logger(project_root)
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
        step_start = datetime.now()
        log_step_start(logger, file_name, 1, STEP_NAMES[1])
        print(f"  Step 1/9: {STEP_NAMES[1]}...")
        content = req_file.read_text(encoding="utf-8", errors="replace")
        content = content.replace("\x00", "")
        prompt = prompts.step1_normalize(str(req_file), content[:1000], hint=hint)
        result = run_agent(prompt, cwd=project_root)
        log_step_end(logger, file_name, 1, STEP_NAMES[1], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 1, STEP_NAMES[1]
        if not normalized_path.exists():
            # Agent 可能用了不同命名，尝试查找
            for f in dirs["outputs"].glob(f"{base_name}*.md"):
                if "normalized" in f.name or f.name == f"{base_name}.md":
                    break

    # Step 2: 需求补全
    if start_step <= 2:
        step_start = datetime.now()
        log_step_start(logger, file_name, 2, STEP_NAMES[2])
        print(f"  Step 2/9: {STEP_NAMES[2]}...")
        req_input = normalized_path if normalized_path.exists() else req_file
        prompt = prompts.step2_complete(str(req_file), str(req_input), hint=hint)
        result = run_agent(prompt, cwd=project_root)
        log_step_end(logger, file_name, 2, STEP_NAMES[2], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 2, STEP_NAMES[2]
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
        step_start = datetime.now()
        log_step_start(logger, file_name, 3, STEP_NAMES[3])
        print(f"  Step 3/9: {STEP_NAMES[3]}...")
        req_input = req_path if req_path.exists() else normalized_path
        prompt = prompts.step3_outline(str(req_input), base_name, scope=scope, hint=hint, figma=figma_info)
        result = run_agent(prompt, cwd=project_root)
        log_step_end(logger, file_name, 3, STEP_NAMES[3], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 3, STEP_NAMES[3]

    # Step 4: 详细设计
    if start_step <= 4:
        step_start = datetime.now()
        log_step_start(logger, file_name, 4, STEP_NAMES[4])
        print(f"  Step 4/9: {STEP_NAMES[4]}...")
        ol_input = outline_path if outline_path.exists() else dirs["outputs"] / f"{base_name}-outline-design.md"
        prompt = prompts.step4_detail(str(ol_input), str(req_path), base_name, scope=scope, hint=hint, figma=figma_info)
        result = run_agent(prompt, cwd=project_root)
        log_step_end(logger, file_name, 4, STEP_NAMES[4], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 4, STEP_NAMES[4]

    # Step 5: 代码实现（Plan 模式）
    if start_step <= 5:
        step_start = datetime.now()
        log_step_start(logger, file_name, 5, STEP_NAMES[5])
        print(f"  Step 5/9: {STEP_NAMES[5]}...")
        detail_input = detail_path if detail_path.exists() else dirs["outputs"] / f"{base_name}-detail-design.md"
        prompt = prompts.step5_implement(str(detail_input), str(req_path), scope=scope, hint=hint, figma=figma_info)
        result = run_plan(prompt, cwd=project_root)
        log_step_end(logger, file_name, 5, STEP_NAMES[5], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 5, STEP_NAMES[5]

    # Step 6: 测试设计
    if start_step <= 6:
        step_start = datetime.now()
        log_step_start(logger, file_name, 6, STEP_NAMES[6])
        print(f"  Step 6/9: {STEP_NAMES[6]}...")
        prompt = prompts.step6_test_design(str(req_path), str(detail_path), base_name, scope=scope, hint=hint, figma=figma_info)
        result = run_agent(prompt, cwd=project_root)
        log_step_end(logger, file_name, 6, STEP_NAMES[6], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 6, STEP_NAMES[6]

    # Step 7: 测试实现
    if start_step <= 7:
        step_start = datetime.now()
        log_step_start(logger, file_name, 7, STEP_NAMES[7])
        print(f"  Step 7/9: {STEP_NAMES[7]}...")
        td_input = test_design_path if test_design_path.exists() else dirs["outputs"] / f"{base_name}-test-design.md"
        prompt = prompts.step7_test_impl(str(td_input), scope=scope, hint=hint)
        result = run_plan(prompt, cwd=project_root)
        log_step_end(logger, file_name, 7, STEP_NAMES[7], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 7, STEP_NAMES[7]

    # Step 8: 编译、运行、测试（循环直至成功）
    if start_step <= 8:
        step_start = datetime.now()
        log_step_start(logger, file_name, 8, STEP_NAMES[8])
        print(f"  Step 8/9: {STEP_NAMES[8]}...")
        max_retries = 5
        for attempt in range(max_retries):
            prompt = prompts.step8_build_test(scope=scope, hint=hint)
            result = run_agent(prompt, cwd=project_root)
            if result.returncode == 0:
                log_step_end(logger, file_name, 8, STEP_NAMES[8], True, (datetime.now() - step_start).total_seconds())
                break
            # 失败时用 Ask 分析
            ask_prompt = f"""
编译/运行/测试失败。请分析失败原因并给出修复建议。
当前是第 {attempt + 1} 次重试。
"""
            run_ask(ask_prompt, cwd=project_root)
        else:
            log_step_end(logger, file_name, 8, STEP_NAMES[8], False, (datetime.now() - step_start).total_seconds())
            return False, 8, STEP_NAMES[8]

    # Step 9: 完成度校验
    if start_step <= 9:
        step_start = datetime.now()
        log_step_start(logger, file_name, 9, STEP_NAMES[9])
        print(f"  Step 9/9: {STEP_NAMES[9]}...")
        prompt = prompts.step9_validate(str(req_path), base_name, scope=scope, hint=hint)
        result = run_agent(prompt, cwd=project_root)
        log_step_end(logger, file_name, 9, STEP_NAMES[9], result.returncode == 0, (datetime.now() - step_start).total_seconds())
        if result.returncode != 0:
            return False, 9, STEP_NAMES[9]

    return True, None, None


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


def _has_unfinished_state(state_file: Path, req_dir: Path) -> tuple[bool, str]:
    """
    检测是否存在未完成的状态（同需求目录）
    Returns: (是否续传, 原因说明)
    """
    if not state_file.exists():
        return False, "无状态文件"
    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False, "状态文件损坏"
    if data.get("completed"):
        return False, "上次已全部完成"
    saved_req_dir = data.get("req_dir")
    if not saved_req_dir:
        return False, "状态中无 req_dir"
    # 使用 resolved 路径比较，避免 ./docs 与 docs、相对与绝对路径差异
    try:
        saved_resolved = str(Path(saved_req_dir).resolve())
        current_resolved = str(req_dir.resolve())
        if saved_resolved != current_resolved:
            return False, f"需求目录不一致（上次: {saved_req_dir}，本次: {req_dir}）"
    except (OSError, RuntimeError):
        if saved_req_dir != str(req_dir):
            return False, f"需求目录不一致（上次: {saved_req_dir}，本次: {req_dir}）"
    if not (data.get("current_file") or data.get("files_done")):
        return False, "无未完成记录"
    return True, ""


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
    if not fresh:
        can_resume, reason = _has_unfinished_state(state_file, req_dir)
        if can_resume:
            resume = True
            print("检测到上次未完成，自动从中断处继续（使用 --fresh 可强制重新开始）")
        elif reason and state_file.exists():
            print(f"提示: 未续传（{reason}）")

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
    state.data["req_dir"] = str(req_dir.resolve())
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
    print(f"运行日志: {project_root / '.codingplan' / 'logs' / 'codingplan.log'}")
    logger = setup_logger(project_root)
    log_workflow_start(logger, str(req_dir), len(files))
    for i, req_file in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] 处理: {req_file.name}")
        success, failed_step, failed_step_name = process_single_file(req_file, project_root, dirs, scope=scope, hint=hint, ui_dir=ui_dir)
        if not success:
            duration_str = _print_duration(start_time)
            duration_sec = (datetime.now() - start_time).total_seconds()
            log_workflow_end(logger, False, duration_sec, len(files_done), f"{req_file.name} 步骤 {failed_step} {failed_step_name or ''} 失败")
            print(f"\n处理失败: {req_file.name}")
            print(f"  失败步骤: Step {failed_step} - {failed_step_name}")
            print(f"  建议: 查看上方 Agent 输出排查原因；或使用 --resume 从断点继续后手动修复")
            state.data["current_file"] = str(req_file)
            state.save()
            if notify_emails:
                notify.send_workflow_complete(
                    notify_emails,
                    success=False,
                    project_path=str(project_root),
                    files_processed=[str(f) for f in files_done],
                    duration_str=duration_str,
                    error_msg=f"处理失败: {req_file.name}（步骤 {failed_step} {failed_step_name or ''}）",
                )
            return 1
        files_done.append(req_file.name)
        state.data.setdefault("files_done", []).append(str(req_file))
        state.save()

    # 全部需求完成后，执行项目级检查
    print("\n执行项目整体完成度与测试检查...")
    if not process_project_check(project_root, dirs, scope=scope, hint=hint):
        duration_str = _print_duration(start_time)
        duration_sec = (datetime.now() - start_time).total_seconds()
        log_workflow_end(logger, False, duration_sec, len(files_done), "项目级检查或补充未完全成功")
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
    duration_sec = (datetime.now() - start_time).total_seconds()
    log_workflow_end(logger, True, duration_sec, len(files_done))
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
