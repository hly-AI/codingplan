"""运行日志：记录各步骤开始/结束、耗时、成功/失败"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

_logger: Optional[logging.Logger] = None


def setup_logger(project_root: Path) -> logging.Logger:
    """初始化日志，写入 .codingplan/logs/codingplan.log"""
    global _logger
    if _logger is not None:
        return _logger

    log_dir = project_root / ".codingplan" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "codingplan.log"

    logger = logging.getLogger("codingplan")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    )
    logger.addHandler(fh)

    _logger = logger
    return logger


def get_logger(project_root: Optional[Path] = None) -> Optional[logging.Logger]:
    """获取已初始化的 logger（若未初始化则返回 None）"""
    if _logger is not None:
        return _logger
    if project_root and (project_root / ".codingplan").exists():
        return setup_logger(project_root)
    return None


def log_step_start(logger: logging.Logger, file_name: str, step: int, step_name: str) -> None:
    """记录步骤开始"""
    logger.info(f"[{file_name}] Step {step}: {step_name} 开始")


def log_step_end(
    logger: logging.Logger,
    file_name: str,
    step: int,
    step_name: str,
    success: bool,
    duration_sec: float,
) -> None:
    """记录步骤结束"""
    status = "成功" if success else "失败"
    logger.info(f"[{file_name}] Step {step}: {step_name} 结束 | {status} | 耗时 {duration_sec:.1f}s")


def log_workflow_start(logger: logging.Logger, req_dir: str, file_count: int) -> None:
    """记录工作流开始"""
    logger.info(f"=== 工作流开始 | 需求目录: {req_dir} | 文件数: {file_count} ===")


def log_workflow_end(
    logger: logging.Logger,
    success: bool,
    duration_sec: float,
    files_done: int,
    error_msg: Optional[str] = None,
) -> None:
    """记录工作流结束"""
    status = "成功" if success else "失败"
    msg = f"=== 工作流结束 | {status} | 耗时 {duration_sec:.1f}s | 完成 {files_done} 个文件 ==="
    if error_msg:
        msg += f" | 错误: {error_msg}"
    logger.info(msg)


def get_step_timeout_seconds() -> int:
    """从环境变量读取单步超时（秒），默认 3600（1 小时）"""
    try:
        s = os.environ.get("CODINGPLAN_STEP_TIMEOUT", "3600")
        return max(60, int(s))
    except (ValueError, TypeError):
        return 3600
