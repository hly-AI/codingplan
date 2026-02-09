"""Cursor Agent CLI 封装"""

import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

from .logger import get_step_timeout_seconds


def check_agent_installed() -> bool:
    """检查 Cursor Agent 是否已安装"""
    try:
        result = subprocess.run(
            ["agent", "--version"],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def run_agent(
    prompt: str,
    cwd: Optional[Path] = None,
    mode: str = "plan",
    force: bool = True,
    output_format: str = "text",
    timeout: Optional[int] = None,
) -> subprocess.CompletedProcess:
    """
    调用 Cursor Agent 执行任务

    Args:
        prompt: 任务描述
        cwd: 工作目录（项目根目录）
        mode: plan | ask（Cursor CLI 仅支持此两种模式，plan 可修改文件，ask 只读）
        force: 是否允许直接修改文件（非交互模式必需）
        output_format: text | json | stream-json
        timeout: 超时秒数，None 时使用环境变量 CODINGPLAN_STEP_TIMEOUT（默认 3600）

    Returns:
        subprocess.CompletedProcess
    """
    # 移除 null 字节，否则 subprocess 在 Unix 上会报 ValueError: embedded null byte
    # （PDF 等二进制文件 read_text 时可能产生 null）
    prompt_safe = prompt.replace("\x00", "")

    cmd = [
        "agent",
        "-p", prompt_safe,
        "--mode", mode,
        "--output-format", output_format,
    ]
    if force:
        cmd.append("--force")

    timeout_sec = timeout if timeout is not None else get_step_timeout_seconds()
    try:
        return subprocess.run(
            cmd,
            cwd=cwd or Path.cwd(),
            capture_output=False,  # 直接输出到终端，便于用户观察
            text=True,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired:
        print(f"\n[超时] 本步骤已运行超过 {timeout_sec} 秒，已终止。"
              f" 可通过环境变量 CODINGPLAN_STEP_TIMEOUT 调整（秒）")
        return SimpleNamespace(returncode=124)


def run_plan(prompt: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """使用 Plan 模式执行（先规划再实现）"""
    return run_agent(prompt, cwd=cwd, mode="plan")


def run_ask(prompt: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """使用 Ask 模式执行（只读分析，不修改文件）"""
    return run_agent(prompt, cwd=cwd, mode="ask", force=False)


def run_implement(prompt: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """使用 Plan 模式执行（可修改文件）"""
    return run_agent(prompt, cwd=cwd, mode="plan")
