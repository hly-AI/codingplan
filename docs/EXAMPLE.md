# CodingPlan 示例项目

本文档说明如何快速运行一个 CodingPlan 示例，验证环境与流程。

---

## 1. 目录结构

示例项目建议结构：

```
my-project/
├── requirements/           # 需求目录
│   └── hello-world.md     # 示例需求
├── uidesign/              # 可选：UI 设计（Figma 链接、交互说明）
├── AGENTS.md              # codingplan init 创建
├── CLAUDE.md              # codingplan init 创建
├── .cursor/rules/         # codingplan init 创建
└── .codingplan/           # 状态与日志
```

---

## 2. 示例需求

在 `requirements/hello-world.md` 中写入：

```markdown
# Hello World 功能

## 背景
需要一个简单的命令行工具，输出 "Hello, World!"。

## 实现方式
- 技术栈：Python 3
- 入口：`python main.py` 或 `./main.py`
- 输出到 stdout

## 验收
- 执行后输出 "Hello, World!"
- 无报错
```

---

## 3. 运行步骤

### 3.1 初始化（首次）

```bash
cd my-project
codingplan init
```

会创建 AGENTS.md、CLAUDE.md、.cursor/rules/ 等。编辑 CLAUDE.md 填写项目背景与技术栈（若示例为 Python，可写「Python 3 命令行工具」）。

### 3.2 处理需求

```bash
codingplan ./requirements
```

或仅处理单个文件：

```bash
codingplan ./requirements -f hello-world.md
```

### 3.3 观察输出

- 终端会显示：`[1/1] 处理: hello-world.md`，以及各步骤进度 `Step 1/9: 文档规范化...` 等
- 运行日志：`.codingplan/logs/codingplan.log`
- 产出目录：`outputs/`（需求、设计文档）、`tests/`（测试）

### 3.4 续传与超时

```bash
# 中断后继续
codingplan ./requirements -r

# 单步超时 2 小时（默认 1 小时）
codingplan ./requirements -t 7200
# 或：CODINGPLAN_STEP_TIMEOUT=7200 codingplan ./requirements
```

---

## 4. 预期产出

| 路径 | 说明 |
|------|------|
| `outputs/hello-world-normalized.md` | 规范化需求 |
| `outputs/hello-world-requirements.md` | 补全后需求 |
| `outputs/hello-world-outline-design.md` | 概要设计 |
| `outputs/hello-world-detail-design.md` | 详细设计 |
| `outputs/hello-world-test-design.md` | 测试设计 |
| `tests/` | 测试代码 |
| 项目根目录下的 `main.py` 等 | 实现代码（由 Agent 按设计生成） |

---

## 5. 最小可运行示例（本仓库）

CodingPlan 仓库内提供 `uidesign/` 作为 UI 设计目录示例。若要完整跑一遍：

1. 在项目根创建 `requirements/hello.md`，内容参考上文
2. 执行 `codingplan init`（若未执行过）
3. 执行 `codingplan ./requirements -f hello.md`
4. 查看 `outputs/` 与 `tests/`

---

## 6. 故障排查

若步骤失败，参见 [故障排查文档](TROUBLESHOOTING.md)。
