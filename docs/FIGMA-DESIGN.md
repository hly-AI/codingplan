# Figma 设计集成说明

需求涉及 APP、Web、H5 等 UI 时，可在需求文件中填写 **Figma 链接** 和 **交互说明**，工具会自动提取并注入到设计、实现阶段的 prompt 中，引导 Agent 按设计稿实现。

## 1. 在需求文件中填写

### 方式一：正文中直接写链接

```markdown
# 需求标题

本需求 UI 设计稿：https://www.figma.com/design/xxxxx/xxx?node-id=123-456
```

### 方式二：使用「Figma 设计」或「交互说明」章节

```markdown
# 需求标题

...需求正文...

## Figma 设计

链接: https://www.figma.com/design/xxxxx/project-name?node-id=123-456

交互说明: 
- 点击列表项进入详情页
- 支持下拉刷新、上拉加载更多
- 卡片长按显示操作菜单
```

### 方式三：分开写

```markdown
## 设计

- 主色 #1976D2，圆角 8px
- 设计稿：https://www.figma.com/file/xxxxx

## 交互说明

1. 首页 Tab 切换
2. 搜索框聚焦时展开
3. 空状态展示引导图
```

## 2. 使用 UI 设计目录（推荐）

默认在项目根目录下使用 `uidesign/` 存放 UI 设计文件，也可通过 `-u` 指定其他目录：

```bash
codingplan ./requirements -u uidesign    # 默认
codingplan ./requirements -u designs    # 指定 designs 目录
codingplan ./requirements -u ""         # 不使用 UI 设计目录
```

目录结构示例：

```
project/
├── requirements/
│   ├── feature-login.md
│   └── feature-list.md
└── uidesign/                    # 默认 UI 设计目录
    ├── feature-login.md         # 与 requirements/feature-login.md 对应
    └── feature-list.figma.md
```

`uidesign/feature-login.md` 内容示例：

```markdown
## Figma 设计
链接: https://www.figma.com/design/xxx/login-page

## 交互说明
- 账号密码输入框，支持明文切换
- 登录按钮 loading 态
- 忘记密码跳转
```

## 3. 使用需求目录下的 .figma.md（可选）

若需求文档很长，也可在同目录放 `.figma.md`：

```
requirements/
├── feature-login.md
├── feature-login.figma.md   # 与 feature-login.md 对应
└── feature-list.md
```

`feature-login.figma.md` 内容示例：

```markdown
## Figma 设计

链接: https://www.figma.com/design/xxx/login-page

## 交互说明

- 账号密码输入框，支持明文切换
- 登录按钮 loading 态
- 忘记密码跳转
```

## 4. 支持的链接格式

- `https://www.figma.com/design/xxx`
- `https://www.figma.com/file/xxx?node-id=123-456`
- `https://figma.com/proto/xxx`

## 5. 工作原理

1. 工具会从需求文件（及同名 `.figma.md`）中解析 Figma URL 和交互说明
2. 在概要设计、详细设计、代码实现、测试设计等阶段，将这些信息注入 prompt
3. Agent 会被告知使用 Figma MCP 或直接访问链接获取设计稿，并按交互说明实现

## 6. 前置条件

- Cursor 已配置 **Figma MCP**（可选，便于自动读取设计稿）
- 或 Agent 可手动访问 Figma 链接查看设计

## 7. 无 Figma 时

若不填写 Figma 链接和交互说明，工具按原流程执行，不注入设计相关内容。
