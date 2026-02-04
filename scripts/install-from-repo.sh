#!/bin/bash
# 从当前仓库本地安装（开发用）
# 在项目根目录执行: ./scripts/install-from-repo.sh

set -e
cd "$(dirname "$0")/.."
pip3 install -e .
echo "已安装 codingplan。使用: codingplan <需求目录>"
