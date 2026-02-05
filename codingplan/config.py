"""配置与常量定义"""

import os
from pathlib import Path

# 输出目录约定
DIR_UNCERTAIN = "uncertain"
DIR_OUTPUTS = "outputs"
DIR_TESTS = "tests"
DIR_UI_DESIGN = "uidesign"  # 默认 UI 设计目录（Figma 链接与交互说明）

# 支持的需求文件扩展名
REQUIREMENT_EXTENSIONS = {".md", ".txt", ".docx", ".pdf"}

# Cursor Agent 命令（需已安装 Cursor CLI）
AGENT_CMD = "agent"

# 工作流步骤
STEPS = [
    "normalize",      # Step 1: 文档规范化
    "complete",       # Step 2: 需求补全
    "outline",        # Step 3: 概要设计
    "detail",         # Step 4: 详细设计
    "implement",      # Step 5: 代码实现
    "test_design",    # Step 6: 测试设计
    "test_impl",      # Step 7: 测试实现
    "build_test",     # Step 8: 编译运行测试
    "validate",       # Step 9: 完成度校验
    "project_check",  # Step 10: 项目整体检查（仅全部需求完成后）
    "project_fix",    # Step 11: 项目级补充（仅全部需求完成后）
]


def get_output_dirs(project_root: Path) -> dict:
    """获取或创建输出目录"""
    dirs = {
        "uncertain": project_root / DIR_UNCERTAIN,
        "outputs": project_root / DIR_OUTPUTS,
        "tests": project_root / DIR_TESTS,
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs
