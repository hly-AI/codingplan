#!/bin/bash
# CodingPlan 安装脚本
# 用法: curl -fsSL https://gitee.com/project_hub_1/codingplan/raw/main/install.sh | bash

set -e

INSTALL_DIR="${CODINGPLAN_INSTALL_DIR:-$HOME/.local/share/codingplan}"
BIN_DIR="${CODINGPLAN_BIN_DIR:-$HOME/.local/bin}"
REPO_URL="${CODINGPLAN_REPO_URL:-https://github.com/hly-AI/codingplan.git}"

echo "CodingPlan 安装程序"
echo "===================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要 Python 3.8+。请先安装 Python。"
    exit 1
fi

# 检查 Cursor Agent
if ! command -v agent &> /dev/null; then
    echo "警告: 未检测到 Cursor Agent。请先安装:"
    echo "  curl https://cursor.com/install -fsS | bash"
    echo ""
    read -p "是否继续安装 CodingPlan? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 克隆或更新
if [ -d "$INSTALL_DIR" ]; then
    echo "更新现有安装..."
    cd "$INSTALL_DIR"
    git pull 2>/dev/null || true
else
    echo "克隆仓库..."
    mkdir -p "$(dirname "$INSTALL_DIR")"
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# 安装（使用 venv 避免 externally-managed-environment）
echo "安装 Python 包..."
VENV="$INSTALL_DIR/.venv"
if [ ! -d "$VENV" ]; then
    python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -e . -q

# 创建可执行脚本（确保 codingplan 命令可用）
mkdir -p "$BIN_DIR"
SCRIPT="$BIN_DIR/codingplan"
cat > "$SCRIPT" << WRAPPER
#!/bin/bash
exec "$INSTALL_DIR/.venv/bin/python" -m codingplan.cli "\$@"
WRAPPER
chmod +x "$SCRIPT"

# 检查 PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "请将以下内容添加到 ~/.bashrc 或 ~/.zshrc:"
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
    echo ""
fi

echo ""
echo "安装完成! 使用方式:"
echo "  codingplan <需求目录>"
echo ""
echo "示例:"
echo "  codingplan ./requirements"
echo "  codingplan ./docs/reqs --resume"
echo ""
