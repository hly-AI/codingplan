---
name: codingplan-outline
description: 为 CodingPlan 概要设计步骤生成结构化概要设计文档。当执行概要设计、编写 outline-design、系统架构、模块划分、技术选型时使用。可与 hld-mermaid-diagrams 配合绘制图表。
---

# CodingPlan 概要设计

为 CodingPlan 工作流 Step 3 提供概要设计文档结构与模板。

## 文档结构

```markdown
# 概要设计：{需求名}

## 1. 设计概述
- 设计目标
- 设计原则
- 影响范围

## 2. 架构设计
- 系统整体架构
- 模块层级与依赖
- **必须包含**：组件图（Mermaid），展示模块划分

## 3. 模块划分
- 模块列表与职责
- 模块间关系
- 若指定 scope，聚焦 scope 范围内

## 4. 核心流程
- 主流程说明
- 关键数据流
- **必须包含**：时序图或流程图（Mermaid）

## 5. 技术选型
- 关键技术栈
- 选型理由（若适用）

## 6. UI 架构（若涉及 Figma）
- UI 组件层级
- 页面与组件规划

## 7. 不确定点
追加到 uncertain/
```

## 图表约定

- 架构设计 → 组件图（graph/flowchart）
- 核心流程 → 时序图或流程图
- 与 hld-mermaid-diagrams 配合可生成规范 Mermaid 图
