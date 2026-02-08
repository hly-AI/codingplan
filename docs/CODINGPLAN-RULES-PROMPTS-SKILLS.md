# CodingPlan 与 Rules、Prompts、Skills 的关系

本文档说明 CodingPlan 如何通过 rules、prompts 等机制处理其他项目。

**延伸阅读**：[AGENTS.md、CLAUDE.md、Rules、Prompts、Skills 的区别、关系与协作](AGENTS-CLAUDE-RULES-PROMPTS-SKILLS.md) —— 详细说明五类配置的区别、关系及在软件开发中的协作方式。

---

## 1. Rules（规则）

### 使用方式

- **注入到目标项目**：执行 `codingplan init` 时，会在**目标项目**（你要处理的项目）中创建：
  - `AGENTS.md`：工作流规则（含多端、安全、代码质量、UI、测试、API、错误处理约定）
  - `.cursor/rules/codingplan-workflow.mdc`：Cursor 工作流规则
  - `.cursor/rules/multi-platform.mdc`：多端/多平台规则
  - `.cursor/rules/security.mdc`：安全与隐私规则
  - `.cursor/rules/code-quality.mdc`：代码质量规则
  - `.cursor/rules/ui-implementation.mdc`：UI 实现规则
  - `.cursor/rules/testing.mdc`：测试规则
  - `.cursor/rules/api-design.mdc`：API 设计规则
  - `.cursor/rules/error-handling.mdc`：错误处理与日志规则
  - `.cursor/rules/database.mdc`：数据库规则（涉及数据库时适用）
  - `CLAUDE.md`：项目上下文模板（项目背景、技术栈、编码规范等）

- **在目标项目中生效**：执行 `codingplan ./requirements` 时，工作目录是**目标项目**，调用 Cursor Agent 时，Agent 会读取该项目的 `.cursor/rules`、`AGENTS.md`、`CLAUDE.md` 等规则。

### 总结

规则是「注入到被处理的项目里」的，而不是在 CodingPlan 自身仓库中集中管理。

---

## 2. Prompts（提示词）

### 使用方式

- **由 CodingPlan 维护**：`codingplan/prompts.py` 中定义了各步骤的 prompt 模板。
- **传给 Cursor Agent**：每次调用 `agent -p <prompt>` 时，都会传入对应步骤的 prompt。
- **内含工作流规则**：每个 prompt 都包含 `WORKFLOW_CONTEXT`（如不确定内容写 `uncertain/`、测试不可跳过等），相当于在 prompt 里再次强调规则。

### 总结

规则既通过 Cursor 规则文件生效，也通过 prompts 里的 `WORKFLOW_CONTEXT` 双重约束。

---

## 3. Skills（技能）

### 使用方式

- **未显式使用**：CodingPlan 代码中**没有**读取或配置 Cursor Skills。
- Skills 是 Cursor 的全局能力，若用户环境中有（如 `.cursor/skills/` 下的技能），Agent 在目标项目中运行时可能会用到。

### 推荐 Skills

CodingPlan 项目提供以下 Skills，位于 `.cursor/skills/`，可提升各步骤产出质量：

| Skill | 适用步骤 | 说明 |
|-------|----------|------|
| `codingplan-test-design` | Step 6 测试设计 | 测试设计文档结构、用例格式、边界/异常场景 |
| `codingplan-requirement` | Step 2 需求补全 | 需求文档结构、功能范围、验收标准 |
| `codingplan-detail-design` | Step 4 详细设计 | 详细设计结构、模块、接口、数据结构 |
| `codingplan-outline` | Step 3 概要设计 | 概要设计文档结构、架构与流程；可与 hld-mermaid-diagrams 配合 |
| `codingplan-implement` | Step 5 代码实现 | 实现检查清单、Plan 模式步骤、实现顺序 |
| `codingplan-test-impl` | Step 7 测试实现 | 测试代码结构、命名、Mock 原则、检查清单 |

**额外推荐**（需另行安装）：`hld-mermaid-diagrams` 可提升 Step 3 概要设计的 Mermaid 图表质量。

### 使用 Skills

- **存放位置**：Skills 位于 CodingPlan 仓库 `.cursor/skills/` 下，作为源文件。
- **处理其他项目时**：`codingplan ./requirements` 的工作目录是目标项目，Agent 读取目标项目的 `.cursor/skills/` 或全局 `~/.cursor/skills/`。因此需将六个 skill 目录复制到目标项目的 `.cursor/skills/`，或复制到 `~/.cursor/skills/`（对本机所有项目生效）。

---

## 4. 其他建议设置

除 Rules、Prompts、Skills 外，以下配置可提升 Agent 效果：

### 4.1 前置条件（必须）

| 项目 | 说明 |
|------|------|
| **Cursor CLI** | 安装：`curl https://cursor.com/install -fsS \| bash` |
| **Cursor 账号** | CLI 需已登录认证 |

### 4.2 项目级配置（建议）

| 项目 | 说明 |
|------|------|
| **CLAUDE.md** | 项目根目录放置，Agent 会读取。可写项目背景、技术栈、编码规范等。`codingplan init` 会创建模板，填写后供 Agent 参考。 |
| **其他 .cursor/rules** | 可增加项目专属规则，与 init 创建的 9 个规则文件一并生效。 |

### 4.3 可选配置

| 项目 | 说明 |
|------|------|
| **.codingplan/email.conf** | 邮件通知。`codingplan init` 会创建模板，填写 SMTP 和收件人后，完成时可发送通知。 |
| **uidesign/** | UI 设计目录。若有 Figma 链接与交互说明，可放在此目录（或 `-u` 指定），Agent 会参照实现 UI。 |
| **Figma MCP** | 需求涉及 UI 时，在 Cursor 中启用 Figma MCP，Agent 可获取设计稿。 |
| **Skills** | CodingPlan 提供 6 个 Skills（test-design、requirement、detail-design、outline、implement、test-impl）；推荐额外安装 `hld-mermaid-diagrams` 提升概要设计图表。 |

### 4.4 项目结构约定

| 目录 | 说明 |
|------|------|
| `uncertain/` | 会自动创建，存放不确定内容 |
| `outputs/` | 会自动创建，存放需求、设计等产出 |
| `tests/` | 会自动创建，存放测试代码 |
| 需求目录 | 如 `./requirements`，放 `.md`、`.txt` 等需求文件 |

---

## 总结表

| 能力    | 使用方式                                                                 |
|---------|--------------------------------------------------------------------------|
| **Rules** | 通过 `codingplan init` 写入目标项目的 `AGENTS.md`、`.cursor/rules/`     |
| **Prompts** | 由 `prompts.py` 生成，作为 `agent -p <prompt>` 的参数传入                 |
| **Skills** | 项目提供 6 个 Skills；推荐 hld-mermaid-diagrams；Agent 按需自动应用 |

---

## 整体流程

CodingPlan 的设计是：**在目标项目里注入规则** + **调用 Cursor Agent 时附带步骤化的 prompts**，从而驱动「需求 → 设计 → 实现 → 测试」的自动化闭环。
