"""CodingPlan init 命令：生成配置文件"""

from pathlib import Path
from typing import Optional

EMAIL_CONF_TEMPLATE = """# CodingPlan 邮件通知配置
# 请将下方占位符替换为实际值后保存

[smtp]
# 发件邮箱 SMTP 配置（QQ 邮箱需在设置中开启 SMTP 并生成授权码）
host = smtp.qq.com
port = 587
user = 请填写发件邮箱@qq.com
password = 请填写授权码
# from = 发件邮箱@qq.com
# use_tls = 1

[notify]
# 默认收件人，多个用逗号分隔（也可用 -e 参数指定）
emails = 请填写收件人@example.com
"""

AGENTS_MD_TEMPLATE = """# CodingPlan 工作流规则

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
"""

CURSOR_RULE_TEMPLATE = """---
description: CodingPlan 自动化需求处理工作流规则；当用户或 CodingPlan 工具触发需求处理时适用
globs: 
alwaysApply: false
---

# CodingPlan 工作流

当用户或 CodingPlan 工具触发需求处理时：

1. 不确定内容一律写入 `uncertain/`
2. 测试不可跳过，功能未测试不视为完成
3. 产出文档按约定命名放入 `outputs/`
4. 测试代码放入 `tests/` 并与被测模块关联命名
5. 若指定 `--scope`，仅限在 scope 目录内实现
6. Git 推送若遇网络错误，可忽略
"""

MULTI_PLATFORM_RULE_TEMPLATE = """---
description: 当需求涉及多端（后端、管理后台、官网、App、小程序等）时适用；多端实现与检查规则
globs: 
alwaysApply: false
---

# 多端/多平台规则

当需求涉及多端时，设计与实现需覆盖所有相关端，不得遗漏。

常见项目类型：后端/API、管理后台、官网、App（iOS/Android/鸿蒙；Flutter/Swift/Kotlin/KMP）、Uniapp/小程序等。
"""

SECURITY_RULE_TEMPLATE = """---
description: 安全与隐私规则；实现时防止敏感信息泄露、做好输入校验
globs: 
alwaysApply: false
---

# 安全与隐私规则

- 不硬编码密钥、密码、API token、私钥等敏感信息；使用环境变量或配置中心
- 对外部输入做校验与转义，防止注入（SQL、XSS、命令等）
- 日志、错误信息中不输出敏感数据（密码、token、完整用户信息等）
- 若涉及用户数据，遵循项目隐私与合规要求
"""

CODE_QUALITY_RULE_TEMPLATE = """---
description: 代码质量规则；可读性优先、风格一致、依赖管理
globs: 
alwaysApply: false
---

# 代码质量规则

- 可读性优先于「聪明」写法；避免过度抽象
- 遵循项目既有代码风格与约定；新增代码与现有风格一致
- 不随意引入新依赖；优先使用项目已有库
- 按功能/需求拆分提交；commit message 清晰、有意义
- 变更时同步更新文档：公共 API 需注释、README 与设计文档随代码更新
"""

UI_IMPLEMENTATION_RULE_TEMPLATE = """---
description: 当需求涉及 UI（Web、App、小程序等）时适用；Figma 对照、响应式、无障碍
globs: 
alwaysApply: false
---

# UI 实现规则

- 若有 Figma 设计，严格按设计稿实现，不随意改动布局、颜色、间距
- 考虑响应式：不同屏幕尺寸、横竖屏
- 考虑无障碍：语义化标签、ARIA、键盘导航、对比度
- 若项目有国际化，文本走 i18n 配置，不硬编码
"""

TESTING_RULE_TEMPLATE = """---
description: 测试要求与规则；核心逻辑覆盖、测试类型、测试组织
globs: 
alwaysApply: false
---

# 测试规则

- 核心逻辑必须有测试覆盖；关键路径、边界条件、异常分支需验证
- 单元测试：纯逻辑、工具函数；集成测试：模块协作、外部依赖；E2E：关键用户流程
- 测试代码放在 `tests/` 目录，与被测模块关联命名；遵循项目既有测试框架与结构
- 测试应可重复运行、不依赖外部状态；使用 mock 隔离外部依赖
"""

API_DESIGN_RULE_TEMPLATE = """---
description: 当需求涉及后端/API 时适用；RESTful、版本、错误格式
globs: 
alwaysApply: false
---

# API 设计规则

- 遵循 RESTful 约定：资源用名词、HTTP 方法表达动作、合理使用状态码
- API 版本：通过路径（如 `/api/v1/`）或 Header 表达；若项目已有约定则遵循
- 统一错误响应格式：含 code、message、明细（若适用）；HTTP 状态码与业务码配合
- 分页、排序、过滤参数命名与项目既有 API 一致
"""

ERROR_HANDLING_RULE_TEMPLATE = """---
description: 错误处理与日志规则；异常处理、日志级别、敏感信息
globs: 
alwaysApply: false
---

# 错误处理与日志规则

- 异常处理：捕获具体异常类型；避免空 catch；适当向上抛出或转换
- 日志：关键操作、错误、警告需记录；级别合理（debug/info/warn/error）
- 日志与错误信息中不输出敏感数据（参见 security.mdc）
- 用户可见错误信息友好、可操作；内部错误 details 不直接暴露给前端
"""

DATABASE_RULE_TEMPLATE = """---
description: 当需求涉及数据库时适用；Schema 设计、迁移、数据兼容
globs: 
alwaysApply: false
---

# 数据库规则

- Schema 设计：合理字段类型、索引、约束；遵循项目既有命名与结构约定
- 迁移：使用版本化迁移脚本；不直接修改已有表结构造成数据丢失
- 兼容性：新增字段考虑默认值；删除或重命名字段需迁移策略
- 敏感数据：存储时加密；查询结果不直接返回敏感字段
"""

CLAUDE_MD_TEMPLATE = """# 项目上下文

> 由 codingplan init 创建。请填写项目背景、技术栈、编码规范等，供 Cursor Agent 在需求处理时参考。
> Cursor CLI 会读取本文件作为 Agent 的持久上下文。
> 撰写指南：https://claude.com/blog/using-claude-md-files

## 项目概述

（简要描述项目用途、核心功能、目标用户）

## 技术栈

（项目类型 + 技术选型，如：后端/API、管理后台、官网、App（iOS/Android/鸿蒙；Flutter/Swift/Kotlin/KMP）、Uniapp/小程序；语言、框架、数据库、构建工具等）

## 架构与目录

（整体架构说明；关键目录：src/、app/、backend/、frontend/ 等及其职责）

## 编码规范

（命名约定、代码风格、测试框架、Lint 规则等）

## 常用命令

```bash
# 启动
# 构建
# 测试
```

## 注意事项

（禁止事项、易错点、特殊约定、外部依赖说明等）

## UI 设计（若涉及）

（Figma 链接约定、交互说明、uidesign/ 目录结构等；使用 CodingPlan 处理需求时可在此说明）
"""

GITIGNORE_ENTRIES = """
# CodingPlan（由 codingplan init 添加）
.codingplan/email.conf
.codingplan/state.json
"""


def _ensure_gitignore(root: Path) -> bool:
    """确保 .gitignore 包含 CodingPlan 相关条目，若不存在则追加"""
    gitignore = root / ".gitignore"
    entries = GITIGNORE_ENTRIES.strip()
    if not gitignore.exists():
        gitignore.write_text(entries + "\n", encoding="utf-8")
        return True
    content = gitignore.read_text(encoding="utf-8", errors="replace")
    if ".codingplan/email.conf" in content:
        return False
    with open(gitignore, "a", encoding="utf-8") as f:
        f.write("\n" + entries + "\n")
    return True


def run_init(project_root: Optional[Path] = None) -> int:
    """
    在项目根目录创建 CodingPlan 相关配置

    - .codingplan/email.conf - 邮件配置模板
    - AGENTS.md - 工作流规则（若不存在）
    - .cursor/rules/codingplan-workflow.mdc - Cursor 工作流规则（若不存在）
    - .cursor/rules/multi-platform.mdc - 多端/多平台规则（若不存在）
    - .cursor/rules/security.mdc - 安全与隐私规则（若不存在）
    - .cursor/rules/code-quality.mdc - 代码质量规则（若不存在）
    - .cursor/rules/ui-implementation.mdc - UI 实现规则（若不存在）
    - .cursor/rules/testing.mdc - 测试规则（若不存在）
    - .cursor/rules/api-design.mdc - API 设计规则（若不存在）
    - .cursor/rules/error-handling.mdc - 错误处理与日志规则（若不存在）
    - .cursor/rules/database.mdc - 数据库规则（若不存在）
    - CLAUDE.md - 项目上下文（若不存在），供 Cursor Agent 读取
    - .gitignore - 追加 email.conf 等忽略项（若尚未包含）

    Returns:
        0 成功，1 失败
    """
    root = project_root or Path.cwd()
    created: list[str] = []

    # 1. 邮件配置
    conf_dir = root / ".codingplan"
    conf_file = conf_dir / "email.conf"
    if conf_file.exists():
        print(f"已存在: {conf_file}")
    else:
        conf_dir.mkdir(parents=True, exist_ok=True)
        conf_file.write_text(EMAIL_CONF_TEMPLATE, encoding="utf-8")
        created.append(str(conf_file))

    # 2. AGENTS.md
    agents_md = root / "AGENTS.md"
    if agents_md.exists():
        print(f"已存在: {agents_md}")
    else:
        agents_md.write_text(AGENTS_MD_TEMPLATE, encoding="utf-8")
        created.append(str(agents_md))

    # 3. .cursor/rules/codingplan-workflow.mdc
    rules_dir = root / ".cursor" / "rules"
    rules_dir.mkdir(parents=True, exist_ok=True)
    cursor_rule = rules_dir / "codingplan-workflow.mdc"
    if cursor_rule.exists():
        print(f"已存在: {cursor_rule}")
    else:
        cursor_rule.write_text(CURSOR_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(cursor_rule))

    # 3b. .cursor/rules/multi-platform.mdc（多端/多平台规则）
    multi_platform_rule = rules_dir / "multi-platform.mdc"
    if multi_platform_rule.exists():
        print(f"已存在: {multi_platform_rule}")
    else:
        multi_platform_rule.write_text(MULTI_PLATFORM_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(multi_platform_rule))

    # 3c. .cursor/rules/security.mdc（安全与隐私规则）
    security_rule = rules_dir / "security.mdc"
    if security_rule.exists():
        print(f"已存在: {security_rule}")
    else:
        security_rule.write_text(SECURITY_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(security_rule))

    # 3d. .cursor/rules/code-quality.mdc（代码质量规则）
    code_quality_rule = rules_dir / "code-quality.mdc"
    if code_quality_rule.exists():
        print(f"已存在: {code_quality_rule}")
    else:
        code_quality_rule.write_text(CODE_QUALITY_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(code_quality_rule))

    # 3e. .cursor/rules/ui-implementation.mdc（UI 实现规则）
    ui_impl_rule = rules_dir / "ui-implementation.mdc"
    if ui_impl_rule.exists():
        print(f"已存在: {ui_impl_rule}")
    else:
        ui_impl_rule.write_text(UI_IMPLEMENTATION_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(ui_impl_rule))

    # 3f. .cursor/rules/testing.mdc（测试规则）
    testing_rule = rules_dir / "testing.mdc"
    if testing_rule.exists():
        print(f"已存在: {testing_rule}")
    else:
        testing_rule.write_text(TESTING_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(testing_rule))

    # 3g. .cursor/rules/api-design.mdc（API 设计规则）
    api_design_rule = rules_dir / "api-design.mdc"
    if api_design_rule.exists():
        print(f"已存在: {api_design_rule}")
    else:
        api_design_rule.write_text(API_DESIGN_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(api_design_rule))

    # 3h. .cursor/rules/error-handling.mdc（错误处理与日志规则）
    error_handling_rule = rules_dir / "error-handling.mdc"
    if error_handling_rule.exists():
        print(f"已存在: {error_handling_rule}")
    else:
        error_handling_rule.write_text(ERROR_HANDLING_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(error_handling_rule))

    # 3i. .cursor/rules/database.mdc（数据库规则）
    database_rule = rules_dir / "database.mdc"
    if database_rule.exists():
        print(f"已存在: {database_rule}")
    else:
        database_rule.write_text(DATABASE_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(database_rule))

    # 4. CLAUDE.md（项目上下文，供 Cursor Agent 读取）
    claude_md = root / "CLAUDE.md"
    if claude_md.exists():
        print(f"已存在: {claude_md}")
    else:
        claude_md.write_text(CLAUDE_MD_TEMPLATE, encoding="utf-8")
        created.append(str(claude_md))

    # 5. .gitignore
    if _ensure_gitignore(root):
        created.append(".gitignore（已追加 CodingPlan 忽略项）")

    # 输出摘要
    if created:
        print("已创建/更新:")
        for p in created:
            print(f"  - {p}")
        print("")
        if str(conf_file) in created:
            print("请编辑 .codingplan/email.conf，将占位符替换为实际值（发件邮箱、授权码、收件人）")
        if str(claude_md) in created:
            print("请编辑 CLAUDE.md，填写项目背景、技术栈、编码规范等，以提升 Agent 对项目的理解")
    return 0
