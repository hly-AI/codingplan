# UI 设计目录

此目录用于存放 Figma 设计链接与交互说明，文件名需与需求文件对应。

例如需求文件为 `requirements/feature-login.md`，则在此目录创建 `feature-login.md` 或 `feature-login.figma.md`：

```markdown
## Figma 设计
链接: https://www.figma.com/design/xxx/xxx?node-id=123

## 交互说明
- 点击卡片进入详情
- 支持下拉刷新
```

使用方式：`codingplan ./requirements -u uidesign`（默认即为 uidesign，可省略 -u）
