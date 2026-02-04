"""各步骤的 Prompt 模板"""

WORKFLOW_CONTEXT = """
你正在执行「基于 Cursor CLI 的自动化需求处理闭环流程」。必须遵守以下规则：
- 任意阶段出现不确定内容，必须写入 uncertain/ 目录
- 测试是强制阶段，不得跳过
- 功能未测试不视为完成
- 测试失败必须分析原因、修复、重试
"""


def step1_normalize(file_path: str, content_preview: str) -> str:
    """Step 1: 原始文档读取与规范化"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：文档规范化

1. 读取文件：{file_path}
2. 若文件不是 .md 格式，将内容转换为标准 Markdown
3. 输出标准化 Markdown 文档到 outputs/ 目录，命名为：{_base_name(file_path)}-normalized.md

当前文件内容预览（前 500 字符）：
---
{content_preview[:500]}
---
"""


def step2_complete(file_path: str, req_doc_path: str) -> str:
    """Step 2: 需求文档补全与完善"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：需求补全

基于项目背景和已规范化的需求文档 {req_doc_path}，补全需求文档，包括：
- 目标描述
- 功能范围
- 非功能性需求
- 约束条件

不确定内容必须写入 uncertain/{_base_name(file_path)}-uncertain.md

输出完善后的需求文档到 outputs/{_base_name(file_path)}-requirements.md
"""


def step3_outline(req_doc_path: str, base_name: str) -> str:
    """Step 3: 概要设计"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：概要设计

基于需求文档 {req_doc_path}，输出概要设计文档，包括：
- 系统整体架构
- 模块划分
- 核心流程说明
- 技术选型（如适用）

不确定点追加到 uncertain/ 目录。

输出到 outputs/{base_name}-outline-design.md
"""


def step4_detail(outline_path: str, req_path: str, base_name: str) -> str:
    """Step 4: 详细设计"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：详细设计

基于需求 {req_path} 和概要设计 {outline_path}，输出详细设计文档，包括：
- 模块内部设计
- 数据结构
- 接口定义
- 核心逻辑说明

输出到 outputs/{base_name}-detail-design.md
"""


def step5_implement(detail_path: str, req_path: str) -> str:
    """Step 5: 基于 Plan 的代码实现"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：代码实现（使用 Plan 模式）

基于需求 {req_path} 和详细设计 {detail_path}：
1. 拆解实现步骤
2. 按计划逐步生成和修改代码
3. 完成代码实现

请使用 Plan 方式：先设计实现步骤，再逐步编码。
"""


def step6_test_design(req_path: str, detail_path: str, base_name: str) -> str:
    """Step 6: 测试设计"""
    return f"""
{WORKFLOW_CONTEXT}

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


def step7_test_impl(test_design_path: str) -> str:
    """Step 7: 测试代码实现"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：测试代码实现

基于测试设计 {test_design_path} 和当前项目代码：
1. 拆解测试实现步骤
2. 自动生成单元测试、集成测试（如适用）
3. 测试代码存放在 tests/ 目录，与被测模块强关联命名
"""


def step8_build_test() -> str:
    """Step 8: 编译、运行、测试"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：编译、运行、测试

1. 执行项目编译
2. 运行项目
3. 执行测试（强制）

若出现编译失败、运行失败或测试失败：
- 使用 Ask 能力分析错误原因
- 获取修复建议
- 修改代码或测试
- 重新执行本步骤

循环直至编译成功、运行成功、测试全部通过，或确认无法继续解决。
"""


def step9_validate(req_path: str) -> str:
    """Step 9: 单需求完成度校验"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：完成度校验

检查：
- 功能是否实现 100%
- 核心逻辑是否有测试覆盖
- 是否存在未验证的关键路径

若未达到 100%，判断是否可继续实现：
- 是 → 回到 Step 5 或 Step 7
- 否 → 记录原因到 uncertain/

输出当前需求最终完成状态说明到 outputs/
"""


def step10_project_check() -> str:
    """Step 10: 项目整体检查"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：项目整体完成度与全量测试检查

基于项目代码、所有需求文档、设计文档、测试代码，评估：
- 是否存在未覆盖需求
- 是否存在模块间未联通实现
- 是否存在无测试保护的核心模块

输出评估报告到 outputs/project-completion-report.md
"""


def step11_project_fix() -> str:
    """Step 11: 项目级补充实现"""
    return f"""
{WORKFLOW_CONTEXT}

## 任务：项目级补充实现与测试

对可继续实现的部分：
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
