"""各步骤的 Prompt 模板"""

from typing import Optional

from .figma import FigmaInfo


def _scope_constraint(scope: Optional[str]) -> str:
    """生成 scope 限制说明"""
    if not scope:
        return ""
    return f"""
## 实现范围限制（必须遵守）

**仅限在 {scope}/ 目录内实现和修改代码**。其他目录（如 ugc_backend、ugc_admin、ugc_flutter 等）已有实现，请勿修改。
- 代码实现、测试代码、编译运行均只针对 {scope}/ 范围内
- 设计文档应聚焦 {scope}/ 的架构与实现
"""


def _hint_block(hint: Optional[str]) -> str:
    """生成额外提醒/上下文块"""
    if not hint or not hint.strip():
        return ""
    return f"""
## 额外提醒（必须遵守）

{hint.strip()}
"""


def _figma_block(figma: Optional[FigmaInfo]) -> str:
    """生成 Figma 设计块"""
    if not figma or figma.is_empty():
        return ""
    parts = []
    if figma.links:
        parts.append("**Figma 设计链接（必须参照实现 UI）：**")
        for url in figma.links:
            parts.append(f"- {url}")
        parts.append("")
    if figma.interaction_desc:
        parts.append("**交互说明（必须实现）：**")
        parts.append(figma.interaction_desc.strip())
    if not parts:
        return ""
    return f"""
## Figma 设计（必须遵守）

请使用 Figma MCP 或直接访问上述链接获取设计稿，严格按设计实现 UI，并实现下述交互。

{chr(10).join(parts)}
"""


WORKFLOW_CONTEXT = """
你正在执行「基于 Cursor CLI 的自动化需求处理闭环流程」。必须遵守以下规则：
- 任意阶段出现不确定内容，必须写入 uncertain/ 目录
- 测试是强制阶段，不得跳过
- 功能未测试不视为完成
- 测试失败必须分析原因、修复、重试
"""


def step1_normalize(file_path: str, content_preview: str, hint: Optional[str] = None) -> str:
    """Step 1: 原始文档读取与规范化"""
    return f"""
{WORKFLOW_CONTEXT}
{_hint_block(hint)}

## 任务：文档规范化

1. 读取文件：{file_path}
2. 若文件不是 .md 格式，将内容转换为标准 Markdown
3. 输出标准化 Markdown 文档到 outputs/ 目录，命名为：{_base_name(file_path)}-normalized.md

当前文件内容预览（前 500 字符）：
---
{content_preview[:500]}
---
"""


def step2_complete(file_path: str, req_doc_path: str, hint: Optional[str] = None) -> str:
    """Step 2: 需求文档补全与完善"""
    return f"""
{WORKFLOW_CONTEXT}
{_hint_block(hint)}

## 任务：需求补全

基于项目背景和已规范化的需求文档 {req_doc_path}，补全需求文档，包括：
- 目标描述
- 功能范围
- 非功能性需求
- 约束条件

不确定内容必须写入 uncertain/{_base_name(file_path)}-uncertain.md

输出完善后的需求文档到 outputs/{_base_name(file_path)}-requirements.md
"""


def step3_outline(req_doc_path: str, base_name: str, scope: Optional[str] = None, hint: Optional[str] = None, figma: Optional[FigmaInfo] = None) -> str:
    """Step 3: 概要设计"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_figma_block(figma)}
{_hint_block(hint)}

## 任务：概要设计

基于需求文档 {req_doc_path}，输出概要设计文档，包括：
- 系统整体架构（若指定 scope，聚焦该范围内的架构）
- 模块划分
- 核心流程说明
- 技术选型（如适用）
- 若有 Figma 设计，需包含 UI 架构与组件规划

不确定点追加到 uncertain/ 目录。

输出到 outputs/{base_name}-outline-design.md
"""


def step4_detail(outline_path: str, req_path: str, base_name: str, scope: Optional[str] = None, hint: Optional[str] = None, figma: Optional[FigmaInfo] = None) -> str:
    """Step 4: 详细设计"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_figma_block(figma)}
{_hint_block(hint)}

## 任务：详细设计

基于需求 {req_path} 和概要设计 {outline_path}，输出详细设计文档，包括：
- 模块内部设计
- 数据结构
- 接口定义
- 核心逻辑说明
- 若有 Figma 设计，需包含 UI 组件结构、布局、样式规范

输出到 outputs/{base_name}-detail-design.md
"""


def step5_implement(detail_path: str, req_path: str, scope: Optional[str] = None, hint: Optional[str] = None, figma: Optional[FigmaInfo] = None) -> str:
    """Step 5: 基于 Plan 的代码实现"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_figma_block(figma)}
{_hint_block(hint)}

## 任务：代码实现（使用 Plan 模式）

基于需求 {req_path} 和详细设计 {detail_path}：
1. 拆解实现步骤
2. 按计划逐步生成和修改代码
3. 完成代码实现
4. 若有 Figma 设计链接，请使用 Figma MCP 或访问链接获取设计稿，严格还原 UI 并实现交互

请使用 Plan 方式：先设计实现步骤，再逐步编码。
"""


def step6_test_design(req_path: str, detail_path: str, base_name: str, scope: Optional[str] = None, hint: Optional[str] = None, figma: Optional[FigmaInfo] = None) -> str:
    """Step 6: 测试设计"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_figma_block(figma)}
{_hint_block(hint)}

## 任务：测试设计

基于需求 {req_path}、详细设计 {detail_path} 和当前代码结构，输出测试设计文档，包括：
- 测试目标
- 测试范围
- 测试类型（单元/集成/接口/E2E）
- 核心测试场景
- 边界条件
- 异常与失败路径

无法覆盖的需求、外部依赖不明确、自动化不可行的测试点，写入 uncertain/

输出到 outputs/{base_name}-test-design.md
"""


def step7_test_impl(test_design_path: str, scope: Optional[str] = None, hint: Optional[str] = None, figma: Optional[FigmaInfo] = None) -> str:
    """Step 7: 测试代码实现"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_figma_block(figma)}
{_hint_block(hint)}

## 任务：测试代码实现

基于测试设计 {test_design_path} 和当前项目代码：
1. 拆解测试实现步骤
2. 自动生成单元测试、集成测试（如适用）
3. 测试代码存放在 tests/ 目录，与被测模块强关联命名
4. 若指定 scope，仅针对 scope 范围内的模块编写测试
"""


def step8_build_test(scope: Optional[str] = None, hint: Optional[str] = None) -> str:
    """Step 8: 编译、运行、测试"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_hint_block(hint)}

## 任务：编译、运行、测试

1. 执行项目编译（若指定 scope，仅编译 scope 范围内或相关子项目）
2. 运行项目
3. 执行测试（强制）

若出现编译失败、运行失败或测试失败：
- 使用 Ask 能力分析错误原因
- 获取修复建议
- 修改代码或测试
- 重新执行本步骤

循环直至编译成功、运行成功、测试全部通过，或确认无法继续解决。
"""


def step9_validate(req_path: str, scope: Optional[str] = None, hint: Optional[str] = None) -> str:
    """Step 9: 单需求完成度校验"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_hint_block(hint)}

## 任务：完成度校验

检查（若指定 scope，仅校验 scope 范围内的实现）：
- 功能是否实现 100%
- 核心逻辑是否有测试覆盖
- 是否存在未验证的关键路径

若未达到 100%，判断是否可继续实现：
- 是 → 回到 Step 5 或 Step 7
- 否 → 记录原因到 uncertain/

输出当前需求最终完成状态说明到 outputs/
"""


def step10_project_check(scope: Optional[str] = None, hint: Optional[str] = None) -> str:
    """Step 10: 项目整体检查"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_hint_block(hint)}

## 任务：项目整体完成度与全量测试检查

基于项目代码、所有需求文档、设计文档、测试代码，评估（若指定 scope，仅评估 scope 范围内）：
- 是否存在未覆盖需求
- 是否存在模块间未联通实现
- 是否存在无测试保护的核心模块

输出评估报告到 outputs/project-completion-report.md
"""


def step11_project_fix(scope: Optional[str] = None, hint: Optional[str] = None) -> str:
    """Step 11: 项目级补充实现"""
    return f"""
{WORKFLOW_CONTEXT}
{_scope_constraint(scope)}
{_hint_block(hint)}

## 任务：项目级补充实现与测试

对可继续实现的部分（若指定 scope，仅修改 scope 范围内的代码）：
- 使用 Plan 补充代码与测试
- 重复编译、运行、测试流程

对无法继续实现的部分：
- 明确原因
- 输出说明文档
- 不确定性写入 uncertain/
"""


def _base_name(path: str) -> str:
    """从路径提取基础名（不含扩展名）"""
    from pathlib import Path
    return Path(path).stem
