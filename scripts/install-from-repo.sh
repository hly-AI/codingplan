#!/bin/bash
# 本地开发安装（对应 README 方式二）
# 在项目根目录执行: ./scripts/install-from-repo.sh
# 或: bash scripts/install-from-repo.sh

set -e
cd "$(dirname "$0")/.."

echo "CodingPlan 本地开发安装"
echo "========================"

# 创建 venv（避免 externally-managed-environment）
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境 .venv ..."
    python3 -m venv .venv
fi

echo "安装 editable 包..."
.venv/bin/pip install -e . -q

echo ""
echo "安装完成! 使用方式:"
echo "  source .venv/bin/activate   # 激活环境"
echo "  codingplan <需求目录>"
echo ""
echo "或直接: .venv/bin/codingplan <需求目录>"
