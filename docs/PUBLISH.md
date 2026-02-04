# CodingPlan 发布指南

## 1. 版本与 Tag

发布前更新 `pyproject.toml` 和 `codingplan/__init__.py` 中的版本号，然后打 tag：

```bash
# 更新版本号后
git add .
git commit -m "chore: bump version to x.y.z"
git tag v0.1.0
git push origin main --tags
```

## 2. PyPI 发布

### 前置条件

- 在 [PyPI](https://pypi.org) 注册账号
- 安装构建工具：`pip install build twine`

### 发布步骤

```bash
# 清理旧构建
rm -rf dist/ build/ *.egg-info

# 构建
python -m build

# 上传（首次需输入 PyPI 用户名和密码/Token）
twine upload dist/*
```

或使用脚本：

```bash
./scripts/publish-pypi.sh
```

发布成功后，用户可：

```bash
pip install codingplan
# 或
pipx install codingplan
```

## 3. Homebrew Tap 发布

### 创建 homebrew-codingplan 仓库

1. 在 Gitee 创建仓库 `homebrew-codingplan`
2. 仓库结构：

```
homebrew-codingplan/
└── Formula/
    └── codingplan.rb
```

3. 将本项目的 `Formula/codingplan.rb` 复制到该仓库的 `Formula/` 目录

### 更新 Formula 的 url 和 sha256

发布 tag 后，获取归档并计算 sha256：

```bash
# Gitee 归档地址（将 v0.1.0 替换为实际版本）
ARCHIVE_URL="https://gitee.com/project_hub_1/codingplan/repository/archive/v0.1.0.tar.gz"

# 下载并计算 sha256
curl -sL "$ARCHIVE_URL" -o /tmp/codingplan.tar.gz
shasum -a 256 /tmp/codingplan.tar.gz
```

将输出的 sha256 填入 `codingplan.rb` 的 `sha256 ""` 中。

**注意**：Gitee 归档 URL 可能因平台不同而略有差异，若 Homebrew 下载失败，可尝试：

- `https://gitee.com/project_hub_1/codingplan/repository/archive/v0.1.0.zip`（zip 格式）
- 或将源码同步到 GitHub，使用 GitHub 的 release 归档

### 用户安装

```bash
brew tap project_hub_1/homebrew-codingplan https://gitee.com/project_hub_1/homebrew-codingplan
brew install codingplan
```

若 Tap 托管在 GitHub，则：

```bash
brew tap project_hub_1/homebrew-codingplan
brew install codingplan
```

## 4. 一键安装脚本

`install.sh` 已配置为从 Gitee 拉取，发布 tag 后无需修改。用户执行：

```bash
curl -fsSL https://gitee.com/project_hub_1/codingplan/raw/main/install.sh | bash
```
