#!/bin/bash
# 准备 Homebrew Tap 仓库内容
# 用法: ./scripts/prepare-homebrew-tap.sh
# 输出到 ../homebrew-codingplan/ 供推送到 GitHub

set -e
cd "$(dirname "$0")/.."

TAP_DIR="../homebrew-codingplan"
mkdir -p "$TAP_DIR/Formula"
cp Formula/codingplan.rb "$TAP_DIR/Formula/"

echo "已生成 Tap 内容到 $TAP_DIR"
echo ""
echo "后续步骤:"
echo "  1. 在 GitHub 创建仓库 hly-AI/homebrew-codingplan"
echo "  2. cd $TAP_DIR && git init && git add . && git commit -m 'Add codingplan formula'"
echo "  3. git remote add origin git@github.com:hly-AI/homebrew-codingplan.git"
echo "  4. git push -u origin main"
echo ""
echo "发布新版本时，更新 Formula/codingplan.rb 中的 url 和 sha256"
