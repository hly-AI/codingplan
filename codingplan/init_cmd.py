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

当执行 CodingPlan 自动化需求处理时，Agent 必须遵守以下规则：

## 强制规则

- ✅ 任意阶段出现不确定内容，必须写入 `uncertain/` 目录
- ✅ 测试是强制阶段，不得跳过
- ✅ 功能未测试不视为完成
- ✅ 测试失败必须进入 Ask → 修复 → 重试
- ✅ 每个需求文件必须形成完整闭环
- ✅ 所有需求完成后必须进行项目级整体与测试检查

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
"""

CURSOR_RULE_TEMPLATE = """---
description: CodingPlan 自动化需求处理工作流规则
globs: 
alwaysApply: false
---

# CodingPlan 工作流

当用户或 CodingPlan 工具触发需求处理时：

1. 不确定内容一律写入 `uncertain/`
2. 测试不可跳过，功能未测试不视为完成
3. 产出文档按约定命名放入 `outputs/`
4. 测试代码放入 `tests/` 并与被测模块关联命名
"""

CLAUDE_MD_TEMPLATE = """# 项目上下文

> 由 codingplan init 创建。请填写项目背景、技术栈、编码规范等，供 Cursor Agent 在需求处理时参考。
> Cursor CLI 会读取本文件作为 Agent 的持久上下文。
> 撰写指南：https://claude.com/blog/using-claude-md-files

## 项目概述

（简要描述项目用途、核心功能、目标用户）

## 技术栈

（语言、框架、数据库、构建工具、第三方依赖等）

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
    - .cursor/rules/codingplan-workflow.mdc - Cursor 规则（若不存在）
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
    cursor_rule = root / ".cursor" / "rules" / "codingplan-workflow.mdc"
    if cursor_rule.exists():
        print(f"已存在: {cursor_rule}")
    else:
        cursor_rule.parent.mkdir(parents=True, exist_ok=True)
        cursor_rule.write_text(CURSOR_RULE_TEMPLATE, encoding="utf-8")
        created.append(str(cursor_rule))

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
