# 邮件通知功能说明

## 1. 功能概述

**未配置则不发送**。仅在同时满足「已配置 SMTP」且「已指定收件人」时，才会在任务完成后发送邮件。

CodingPlan 在任务**完成**（无论成功或失败）后，可向指定邮箱发送一封结果通知邮件，内容包括：

- 状态（成功 / 失败）
- 项目路径
- 已处理的需求文件列表
- 总耗时
- 失败时的错误信息

## 2. 配置方式概览

支持**配置文件**和**环境变量**两种方式，优先级：**环境变量 > 配置文件**。

| 方式 | 适用场景 |
|------|----------|
| **配置文件** | 推荐给他人使用，一次配置持久生效 |
| **环境变量** | CI/脚本、临时覆盖配置 |

## 3. 配置文件（推荐）

### 3.1 配置文件位置（按优先级）

| 位置 | 说明 |
|------|------|
| `.codingplan/email.conf` | 项目根目录，仅对当前项目生效 |
| `~/.config/codingplan/email.conf` | 用户级，对本机所有项目生效 |
| `~/.codingplan/email.conf` | 用户级备用路径 |

### 3.2 配置文件格式

复制示例文件并编辑：

```bash
# 项目级：在项目根目录
mkdir -p .codingplan
# 从仓库示例复制（若使用本项目开发安装）
cp .codingplan/email.conf.example .codingplan/email.conf
# 编辑 .codingplan/email.conf，填写真实值

# 或用户级（对本机所有项目生效）
mkdir -p ~/.config/codingplan
# 创建 ~/.config/codingplan/email.conf，内容同上
```

`email.conf` 内容示例：

```ini
[smtp]
# 发件邮箱 SMTP 配置
host = smtp.qq.com
port = 587
user = your@qq.com
password = 你的授权码
# from = your@qq.com
# use_tls = 1

[notify]
# 默认收件人，多个用逗号分隔（可选，也可用 -e 参数覆盖）
emails = notify@example.com, another@example.com
```

**注意**：`.codingplan/email.conf` 含密码，请加入 `.gitignore`，不要提交到仓库。

### 3.3 配置后使用

配置好后，直接运行即可发送邮件，无需每次加 `-e`：

```bash
codingplan ./requirements
```

若在 `[notify] emails` 中配置了默认收件人，会自动发送；也可用 `-e` 覆盖或追加。

---

## 4. 环境变量

环境变量会**覆盖**配置文件中的同名项。变量列表：

| 环境变量 | 必填 | 说明 | 示例 |
|----------|------|------|------|
| `CODINGPLAN_SMTP_HOST` | ✅ | SMTP 服务器地址 | `smtp.qq.com` |
| `CODINGPLAN_SMTP_PORT` | ✅ | SMTP 端口（587=STARTTLS，465=SSL） | `587` |
| `CODINGPLAN_SMTP_USER` | ✅ | 发件邮箱（登录用户名） | `my@qq.com` |
| `CODINGPLAN_SMTP_PASSWORD` | ✅ | 邮箱密码或 SMTP 授权码 | `abcdefghijklmnop` |
| `CODINGPLAN_SMTP_FROM` | ❌ | 发件人显示（默认同 USER） | `CodingPlan <my@qq.com>` |
| `CODINGPLAN_SMTP_TLS` | ❌ | 是否使用 STARTTLS（默认 1） | `1` 或 `0` |

### 4.1 临时设置（仅当前终端有效）

```bash
export CODINGPLAN_SMTP_HOST=smtp.qq.com
export CODINGPLAN_SMTP_PORT=587
export CODINGPLAN_SMTP_USER=your@qq.com
export CODINGPLAN_SMTP_PASSWORD=你的授权码

codingplan ./requirements -e notify@example.com
```

### 4.2 写入 Shell 配置文件（持久生效）

在 `~/.zshrc`（zsh）或 `~/.bashrc`（bash）末尾添加：

```bash
# CodingPlan 邮件通知配置
export CODINGPLAN_SMTP_HOST=smtp.qq.com
export CODINGPLAN_SMTP_PORT=587
export CODINGPLAN_SMTP_USER=your@qq.com
export CODINGPLAN_SMTP_PASSWORD=你的授权码
```

保存后执行 `source ~/.zshrc` 或 `source ~/.bashrc`，之后每次打开终端都生效。

### 4.3 项目内 .env 文件（需手动加载）

在项目根目录创建 `.env`：

```bash
# .env（不要提交到 Git）
CODINGPLAN_SMTP_HOST=smtp.qq.com
CODINGPLAN_SMTP_PORT=587
CODINGPLAN_SMTP_USER=your@qq.com
CODINGPLAN_SMTP_PASSWORD=你的授权码
```

运行前加载：

```bash
set -a
source .env
set +a
codingplan ./requirements -e notify@example.com
```

或使用工具：`export $(grep -v '^#' .env | xargs)` 或 `dotenv run codingplan ./requirements -e x@x.com`。

---

## 5. 各邮箱服务商具体配置

### 5.1 QQ 邮箱

1. 登录 [QQ 邮箱](https://mail.qq.com) → 设置 → 账户 → POP3/IMAP/SMTP
2. 开启「POP3/SMTP 服务」或「IMAP/SMTP 服务」
3. 生成**授权码**（16 位），用授权码作为密码，而非 QQ 登录密码

```bash
export CODINGPLAN_SMTP_HOST=smtp.qq.com
export CODINGPLAN_SMTP_PORT=587
export CODINGPLAN_SMTP_USER=你的QQ号@qq.com
export CODINGPLAN_SMTP_PASSWORD=刚才生成的16位授权码
export CODINGPLAN_SMTP_TLS=1
```

### 5.2 163 网易邮箱

1. 登录 [163 邮箱](https://mail.163.com) → 设置 → POP3/SMTP/IMAP
2. 开启「SMTP 服务」，按提示设置授权密码

```bash
export CODINGPLAN_SMTP_HOST=smtp.163.com
export CODINGPLAN_SMTP_PORT=587
export CODINGPLAN_SMTP_USER=your@163.com
export CODINGPLAN_SMTP_PASSWORD=授权密码
export CODINGPLAN_SMTP_TLS=1
```

或使用 SSL 465 端口：

```bash
export CODINGPLAN_SMTP_HOST=smtp.163.com
export CODINGPLAN_SMTP_PORT=465
export CODINGPLAN_SMTP_USER=your@163.com
export CODINGPLAN_SMTP_PASSWORD=授权密码
export CODINGPLAN_SMTP_TLS=0
```

### 5.3 Gmail

1. 开启 Google 账户「两步验证」
2. 在 [应用专用密码](https://myaccount.google.com/apppasswords) 生成 SMTP 专用密码

```bash
export CODINGPLAN_SMTP_HOST=smtp.gmail.com
export CODINGPLAN_SMTP_PORT=587
export CODINGPLAN_SMTP_USER=your@gmail.com
export CODINGPLAN_SMTP_PASSWORD=应用专用密码
export CODINGPLAN_SMTP_TLS=1
```

### 5.4 腾讯企业邮箱

```bash
export CODINGPLAN_SMTP_HOST=smtp.exmail.qq.com
export CODINGPLAN_SMTP_PORT=587
export CODINGPLAN_SMTP_USER=your@company.com
export CODINGPLAN_SMTP_PASSWORD=邮箱密码或授权码
export CODINGPLAN_SMTP_TLS=1
```

### 5.5 Outlook / Microsoft 365

```bash
export CODINGPLAN_SMTP_HOST=smtp.office365.com
export CODINGPLAN_SMTP_PORT=587
export CODINGPLAN_SMTP_USER=your@outlook.com
export CODINGPLAN_SMTP_PASSWORD=账户密码
export CODINGPLAN_SMTP_TLS=1
```

---

## 6. 使用方式

### 6.1 指定收件人

通过 `-e` 或 `--notify-email` 指定收件邮箱，可多次使用：

```bash
# 单个收件人
codingplan ./requirements -e user@example.com

# 多个收件人
codingplan ./requirements -e a@example.com -e b@example.com
```

### 6.2 发送时机

**会发送**（需已配置 SMTP + 收件人）：
| 场景 | 是否发送 |
|------|----------|
| 全部需求处理成功 | ✅ 发送（状态：成功） |
| 某需求处理失败 | ✅ 发送（状态：失败，含错误信息） |
| 项目级检查失败 | ✅ 发送（状态：失败） |

**不发送**（满足任一条件即跳过）：
| 场景 | 说明 |
|------|------|
| 未指定收件人 | 未使用 `-e` 且配置文件中无 `[notify] emails` |
| 未配置 SMTP | 无配置文件且未设置 `CODINGPLAN_SMTP_*` 环境变量 |

---

## 7. 邮件内容示例

### 7.1 成功时

```
主题: [CodingPlan] 需求处理成功 - /path/to/your/project

正文:
状态: 成功
项目路径: /path/to/your/project
处理文件数: 3
耗时: 15分32秒

已处理文件:
  - req-a.md
  - req-b.md
  - req-c.md
```

### 7.2 失败时

```
主题: [CodingPlan] 需求处理失败 - /path/to/your/project

正文:
状态: 失败
项目路径: /path/to/your/project
处理文件数: 2
耗时: 8分12秒

已处理文件:
  - req-a.md
  - req-b.md

错误信息:
处理失败: req-c.md
```

---

## 8. 代码中的实现位置

| 文件 | 说明 |
|------|------|
| `codingplan/notify.py` | 邮件发送逻辑，从配置文件/环境变量读取 SMTP 配置 |
| `codingplan/workflow.py` | 工作流结束时调用 `notify.send_workflow_complete()` |
| `codingplan/cli.py` | 解析 `-e/--notify-email` 参数并传给 `run_workflow()` |

---

## 9. 故障排查

### 9.1 提示「未配置 SMTP，跳过邮件通知」

说明 SMTP 未配置。检查顺序：

1. **配置文件**：是否存在 `.codingplan/email.conf` 或 `~/.config/codingplan/email.conf`，且 `[smtp]` 中填写了 `host`、`user`、`password`
2. **环境变量**：`echo $CODINGPLAN_SMTP_HOST`、`echo $CODINGPLAN_SMTP_USER`

### 9.2 提示「邮件发送失败: ...」

- **Authentication failed**：用户名或密码错误，QQ/163 等需使用**授权码**而非登录密码
- **Connection refused**：端口或防火墙问题，尝试换 465 或 587
- **SSL/TLS error**：尝试设置 `CODINGPLAN_SMTP_TLS=0`（465 端口）或 `CODINGPLAN_SMTP_TLS=1`（587 端口）

### 9.3 收不到邮件

- 检查垃圾邮件
- 确认收件人邮箱地址正确
- 确认 SMTP 服务已在邮箱设置中开启
