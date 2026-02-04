#!/bin/bash
# PyPI 发布脚本
# 用法: ./scripts/publish-pypi.sh
# 自动使用 venv 避免 externally-managed-environment 错误

set -e
cd "$(dirname "$0")/.."

echo "=== CodingPlan PyPI 发布 ==="

# 检查 Python
if ! command -v python3 &>/dev/null; then
    echo "错误: 需要 python3"
    exit 1
fi

# 使用项目 venv 或创建临时 venv
VENV_DIR=".venv-publish"
if [ ! -d "$VENV_DIR" ]; then
    echo "创建发布用虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip install -q build twine

# 清理
rm -rf dist/ build/ *.egg-info codingplan.egg-info 2>/dev/null || true

# 构建
echo "构建中..."
python -m build

# 上传
echo "上传到 PyPI..."
twine upload dist/*

echo ""
echo "发布完成! 用户可执行: pip install codingplan"
