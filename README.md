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
pipx install git+https://gitee.com/your-org/codingplan.git

# 或使用 pip + venv
python3 -m venv .venv && source .venv/bin/activate
pip install git+https://gitee.com/your-org/codingplan.git
```

### 方式二：本地开发安装

```bash
cd codingplan
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
```

### 方式三：curl 一键安装

```bash
curl -fsSL https://raw.githubusercontent.com/your-org/codingplan/main/install.sh | bash
```

安装后若 `codingplan` 命令不可用，请将 `~/.local/bin` 加入 PATH：

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### 方式四：Homebrew（需自建 Tap）

1. 创建 Homebrew Tap 仓库 `homebrew-codingplan`
2. 将 `Formula/codingplan.rb` 放入 `Formula/` 目录
3. 更新 formula 中的 `url` 和 `sha256`（发布 tag 后）
4. 用户安装：
   ```bash
   brew tap your-org/codingplan
   brew install codingplan
   ```

## 使用

```bash
# 处理指定目录下所有需求文件
codingplan ./requirements

# 从上次中断处继续
codingplan ./requirements --resume

# 仅处理单个文件
codingplan ./requirements -f feature-a.md
```

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
