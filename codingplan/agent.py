"""Cursor Agent CLI 封装"""

import subprocess
import sys
from pathlib import Path
from typing import Optional


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
    mode: str = "agent",
    force: bool = True,
    output_format: str = "text",
) -> subprocess.CompletedProcess:
    """
    调用 Cursor Agent 执行任务

    Args:
        prompt: 任务描述
        cwd: 工作目录（项目根目录）
        mode: agent | plan | ask
        force: 是否允许直接修改文件（非交互模式必需）
        output_format: text | json | stream-json

    Returns:
        subprocess.CompletedProcess
    """
    cmd = [
        "agent",
        "-p", prompt,
        "--mode", mode,
        "--output-format", output_format,
    ]
    if force:
        cmd.append("--force")

    return subprocess.run(
        cmd,
        cwd=cwd or Path.cwd(),
        capture_output=False,  # 直接输出到终端，便于用户观察
        text=True,
    )


def run_plan(prompt: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """使用 Plan 模式执行（先规划再实现）"""
    return run_agent(prompt, cwd=cwd, mode="plan")


def run_ask(prompt: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """使用 Ask 模式执行（只读分析，不修改文件）"""
    return run_agent(prompt, cwd=cwd, mode="ask", force=False)


def run_implement(prompt: str, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """使用 Agent 模式执行（可修改文件）"""
    return run_agent(prompt, cwd=cwd, mode="agent")
