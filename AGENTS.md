# CodingPlan 工作流规则

当执行 CodingPlan 自动化需求处理时，Agent 必须遵守以下规则。
项目上下文见 CLAUDE.md。

## 工作流步骤

1. 文档规范化 → 2. 需求补全 → 3. 概要设计 → 4. 详细设计 → 5. 代码实现 → 6. 测试设计 → 7. 测试实现 → 8. 编译运行测试 → 9. 完成度校验 → 10. 项目整体检查 → 11. 项目级补充

## 强制规则

- ✅ 任意阶段出现不确定内容，必须写入 `uncertain/` 目录
- ✅ 测试是强制阶段，不得跳过
- ✅ 功能未测试不视为完成
- ✅ 测试失败必须进入 Ask → 修复 → 重试
- ✅ 每个需求文件必须形成完整闭环
- ✅ 所有需求完成后必须进行项目级整体与测试检查
- ✅ 若指定 `--scope`，仅限在 scope 目录内实现和修改代码
- ✅ Git 推送若遇网络错误（Connection stalled、timeout），可忽略，本地提交已足够

## 输出目录

- `uncertain/` - 所有不确定、待确认、无法判断的问题
- `outputs/` - 各阶段正式产出文档（需求、设计、说明等）
- `tests/` - 自动生成的测试相关内容

## 文档命名约定

- `{需求名}-normalized.md` - 规范化后的需求
- `{需求名}-requirements.md` - 完善后的需求
- `{需求名}-outline-design.md` - 概要设计
- `{需求名}-detail-design.md` - 详细设计
- `{需求名}-test-design.md` - 测试设计
- `{需求名}-completion-status.md` - 完成度校验结果

## 需求文件

支持格式：`.md`、`.txt`、`.docx`、`.pdf`。若涉及 UI，可将 Figma 链接与交互说明放入 `uidesign/` 目录，文件名与需求对应。

## 多端/多平台

当需求涉及多端（后端、管理后台、官网、App、小程序等）时，设计与实现需覆盖所有相关端，不得遗漏。
常见类型：后端/API、管理后台、官网、App（iOS/Android/鸿蒙；Flutter/Swift/Kotlin/KMP）、Uniapp/小程序等。

## 安全与隐私

见 `.cursor/rules/security.mdc`：不硬编码敏感信息、输入校验、日志脱敏。

## 代码质量

见 `.cursor/rules/code-quality.mdc`：可读性优先、风格一致、依赖管理、提交规范、文档同步。

## UI 实现

见 `.cursor/rules/ui-implementation.mdc`：Figma 对照、响应式、无障碍、国际化。

## 测试

见 `.cursor/rules/testing.mdc`：核心逻辑覆盖、测试类型、测试组织。

## API 设计

见 `.cursor/rules/api-design.mdc`：RESTful、版本、错误格式（涉及后端/API 时适用）。

## 错误处理与日志

见 `.cursor/rules/error-handling.mdc`：异常处理、日志级别、敏感信息。

## 数据库

见 `.cursor/rules/database.mdc`：Schema 设计、迁移、数据兼容（涉及数据库时适用）。
