# CodingPlan 故障排查

本文档汇总常见问题与典型错误的解决办法。

---

## 1. 前置条件

### 未检测到 Cursor Agent

**现象**：`错误: 未检测到 Cursor Agent。请先安装: curl https://cursor.com/install -fsS | bash`

**处理**：
1. 安装 Cursor CLI：`curl https://cursor.com/install -fsS | bash`
2. 重启终端，确保 `agent` 在 PATH 中
3. 检查：`agent --version`

### 未登录 Cursor 账号

**现象**：Agent 执行时报权限或认证错误

**处理**：在 Cursor 中登录账号，或使用 `cursor auth` 完成登录。

---

## 2. 步骤失败

### 某一步骤返回非 0

**现象**：`处理失败: xxx.md`，`失败步骤: Step N - 步骤名`

**处理**：
1. 查看终端上方 Agent 输出，通常会有错误或失败原因
2. 使用 `--resume` 从断点继续，针对失败步骤手动修复后再运行
3. 查看运行日志：`.codingplan/logs/codingplan.log`，确认该步骤耗时与状态
4. 若为编译/测试失败（Step 8），Agent 会多次重试并输出 Ask 分析，可根据建议修改后重新运行

### 步骤超时

**现象**：`[超时] 本步骤已运行超过 3600 秒，已终止`

**处理**：
1. 默认单步超时 1 小时，可通过环境变量或 CLI 调整：
   - `CODINGPLAN_STEP_TIMEOUT=7200 codingplan ./reqs`（2 小时）
   - `codingplan ./reqs -t 7200`
2. 确认需求是否过于复杂，可拆分为多个小需求
3. 使用 `--resume` 从中断处继续

---

## 3. 需求与输出

### 未找到需求文件

**现象**：`未在 xxx 中找到需求文件（支持: .md, .txt, .docx, .pdf）`

**处理**：
1. 确认需求目录路径正确
2. 确认文件扩展名为 `.md`、`.txt`、`.docx` 或 `.pdf`
3. 若需处理单个文件：`codingplan ./reqs -f my-req.md`

### 输出文件命名不符预期

**现象**：Agent 生成了不同命名的文件（如 `xxx.md` 而非 `xxx-normalized.md`）

**处理**：工作流会尝试查找同前缀文件，若仍失败可手动重命名后使用 `--resume` 继续。

---

## 4. 项目与配置

### 项目级检查失败

**现象**：`项目级检查或补充未完全成功`

**处理**：
1. 查看 Agent 输出，确认是 Step 10（检查）还是 Step 11（补充）失败
2. 按建议修复后重新运行：`codingplan ./reqs -r`
3. 若仅需完成需求处理、跳过项目检查，可先注释相关逻辑（需改源码）

### 续传未生效

**现象**：希望续传但未检测到上次未完成

**处理**：
1. 确认使用同一需求目录（`req_dir`）
2. 确认 `.codingplan/state.json` 存在且未标记 `completed`
3. 使用 `--resume` 显式指定续传
4. 使用 `--fresh` 会强制重新开始，忽略状态

---

## 5. 运行日志

**位置**：`<项目根>/.codingplan/logs/codingplan.log`

**内容**：各步骤开始/结束时间、耗时、成功/失败

**作用**：排查超时、定位失败步骤、统计耗时。

---

## 6. 典型错误码

| 情况 | 说明 |
|------|------|
| `returncode=124` | 步骤超时（与 `timeout` 命令约定一致） |
| `returncode=1` | Agent 执行失败，查看终端输出 |
| `FileNotFoundError: agent` | Cursor CLI 未安装或不在 PATH |

---

## 7. 获取帮助

- 文档：`docs/` 目录
- 规则与 Skills：`AGENTS.md`、`.cursor/rules/`、`.cursor/skills/`
- 邮件通知：`docs/EMAIL-NOTIFICATION.md`
