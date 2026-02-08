---
name: codingplan-test-impl
description: 为 CodingPlan 测试实现步骤提供测试代码结构与实现模式。当执行测试实现、编写单元测试、集成测试、mock 外部依赖时使用。
---

# CodingPlan 测试实现

为 CodingPlan 工作流 Step 7 提供测试代码结构与实现指引。

## 测试代码结构

```
tests/
├── {模块名}_test.{ext}     # 单元测试，与被测模块同名
├── test_{模块名}.{ext}     # 或 test_ 前缀（依项目约定）
├── integration/            # 集成测试（若适用）
│   └── test_{场景}.{ext}
└── conftest.py / fixtures  # 共享 fixture（若适用）
```

## 测试命名

- 文件：`被测模块_test` 或 `test_被测模块`
- 用例：`test_场景描述` 或 `should_预期行为_when_条件`
- 表意清晰，避免 `test_1`、`test_a`

## Mock 原则

- 外部 API、DB、消息队列 → Mock
- 纯逻辑、无 I/O → 不 Mock
- 隔离被测单元，避免外部状态影响

## 实现顺序

1. 按测试设计中的用例逐个实现
2. 先通过用例（green），再考虑重构
3. 遵循项目既有测试框架（pytest、jest、JUnit 等）

## 检查清单

```
- [ ] 测试代码在 tests/ 目录
- [ ] 与被测模块关联命名
- [ ] 核心逻辑有覆盖
- [ ] 边界、异常有用例
- [ ] 外部依赖已 Mock
- [ ] 可重复运行、无顺序依赖
```
