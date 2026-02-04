# CodingPlan

基于 **Cursor CLI** 的自动化需求处理、代码实现与测试闭环工具。在项目目录下指定需求目录，自动完成：需求规范化 → 补全 → 概要设计 → 详细设计 → 代码实现 → 测试设计 → 测试实现 → 编译运行测试 → 完成度校验 → 项目整体检查。

## 前置条件

1. **安装 Cursor CLI**
   ```bash
   curl https://cursor.com/install -fsS | bash
   ```

2. **登录 Cursor 账号**（CLI 需已认证）

3. **在项目根目录下执行**

## 安装

### 方式一：pip / pipx 安装（推荐）

```bash
# 使用 pipx（推荐，独立环境，全局可用）
pipx install git+https://gitee.com/project_hub_1/codingplan.git

# 或从 PyPI（发布后）
pip install codingplan
# 或 pipx install codingplan

# 或使用 pip + venv
python3 -m venv .venv && source .venv/bin/activate
pip install git+https://gitee.com/project_hub_1/codingplan.git
```

### 方式二：本地开发安装

```bash
cd codingplan
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
# 或使用脚本: bash scripts/install-from-repo.sh
```

### 方式三：curl 一键安装

```bash
curl -fsSL https://gitee.com/project_hub_1/codingplan/raw/main/install.sh | bash
```

安装后若 `codingplan` 命令不可用，请将 `~/.local/bin` 加入 PATH：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 方式四：Homebrew

```bash
brew tap project_hub_1/homebrew-codingplan https://gitee.com/project_hub_1/homebrew-codingplan
brew install codingplan
# 若尚未发布 tag，可使用: brew install codingplan --HEAD
```

需先创建 [homebrew-codingplan](https://gitee.com/project_hub_1/homebrew-codingplan) 仓库并放入 Formula，详见 [发布说明](docs/PUBLISH.md)。

### 安装方式说明

| 方式 | 说明 | 状态 |
|------|------|------|
| **方式一** | pip/pipx 安装，`pyproject.toml` 已配置 | ✅ |
| **方式二** | 本地开发安装，`scripts/install-from-repo.sh` 自动创建 venv | ✅ |
| **方式三** | curl 一键安装，`install.sh` 克隆仓库并安装到 `~/.local/bin` | ✅ |
| **方式四** | Homebrew，Formula 支持 `--HEAD` 从 main 安装 | ✅ |

**后续步骤**：
- **PyPI**：执行 `./scripts/publish-pypi.sh` 发布后，可使用 `pip install codingplan`
- **Homebrew**：创建 `homebrew-codingplan` 仓库，运行 `./scripts/prepare-homebrew-tap.sh` 生成 Formula 并推送
- **Gitee**：发布 tag 后，在 Formula 中更新 `url` 和 `sha256`，以支持 `brew install codingplan`（非 `--HEAD`）

### 更新

根据你的安装方式选择对应命令：

| 安装方式 | 更新命令 |
|----------|----------|
| **pipx** | `pipx upgrade codingplan` 或 `pipx install --force git+https://gitee.com/project_hub_1/codingplan.git` |
| **pip (venv)** | `pip install --upgrade codingplan` 或 `pip install --upgrade git+https://gitee.com/project_hub_1/codingplan.git` |
| **curl 一键** | 再次执行 `curl -fsSL https://gitee.com/project_hub_1/codingplan/raw/main/install.sh \| bash`（会拉取最新并重装） |
| **本地开发** | `cd codingplan && git pull && pip install -e .` |
| **Homebrew** | `brew upgrade codingplan` 或 `brew upgrade codingplan --fetch-HEAD`（若用 `--HEAD` 安装） |

## 使用

```bash
# 处理指定目录下所有需求文件
codingplan ./requirements

# 从上次中断处继续
codingplan ./requirements --resume

# 仅处理单个文件
codingplan ./requirements -f feature-a.md

# 实现范围限制：仅在此目录内实现/修改代码（如 ugc_kmp），其他目录不修改
codingplan ./requirements -s ugc_kmp
```

### 实现范围限制（--scope / -s）

当项目为多端结构（如后端、管理后台、多个客户端）且只需实现其中一端时，可使用 `-s` 限制实现范围：

```bash
# 仅限在 ugc_kmp 目录内实现，不修改 ugc_backend、ugc_admin、ugc_flutter 等
codingplan ./requirements -s ugc_kmp
```

工具会在设计、实现、测试、编译等各阶段约束 Agent 仅修改指定目录内的代码。

### 目录约定

工具会在**当前工作目录**下创建/使用：

| 目录 | 说明 |
|------|------|
| `uncertain/` | 所有不确定、待确认内容 |
| `outputs/` | 需求、设计、测试设计等产出文档 |
| `tests/` | 自动生成的测试代码 |
| `.codingplan/` | 工作流状态（用于 --resume） |

### 支持的需求文件格式

- `.md`（Markdown）
- `.txt`
- `.docx`、`.pdf`（需 Agent 具备解析能力）

## 工作流步骤

对每个需求文件依次执行：

1. **文档规范化**：转换为标准 Markdown
2. **需求补全**：目标、功能范围、非功能需求、约束
3. **概要设计**：架构、模块、流程、技术选型
4. **详细设计**：模块设计、数据结构、接口、逻辑
5. **代码实现**：基于 Cursor Plan 拆解并实现
6. **测试设计**：测试目标、范围、场景、边界
7. **测试实现**：生成单元/集成测试代码
8. **编译运行测试**：编译 → 运行 → 测试，失败则 Ask 分析并修复
9. **完成度校验**：功能 100%、测试覆盖检查

全部需求完成后：

10. **项目整体检查**：未覆盖需求、模块联通、测试保护
11. **项目级补充**：补充实现与测试

## 强制规则

- 任意阶段出现不确定内容 → 写入 `uncertain/`
- 测试为强制阶段，不得跳过
- 功能未测试不视为完成
- 测试失败 → Ask 分析 → 修复 → 重试

## 配置

工具会读取项目中的 `.cursor/rules`、`AGENTS.md`、`CLAUDE.md` 作为 Agent 的上下文规则。建议在项目中添加与需求处理相关的规则。

## 许可证

MIT
