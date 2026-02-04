#!/bin/bash
# PyPI 发布脚本
# 用法: ./scripts/publish-pypi.sh
# 前置: pip install build twine

set -e
cd "$(dirname "$0")/.."

echo "=== CodingPlan PyPI 发布 ==="

# 检查工具
for cmd in python3 pip; do
    if ! command -v $cmd &>/dev/null; then
        echo "错误: 需要 $cmd"
        exit 1
    fi
done

# 安装构建依赖
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
