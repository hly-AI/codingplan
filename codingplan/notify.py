"""邮件通知模块"""

import configparser
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

# 配置文件路径（优先级：项目 > 用户）
CONFIG_PATHS = [
    Path.cwd() / ".codingplan" / "email.conf",
    Path.home() / ".config" / "codingplan" / "email.conf",
    Path.home() / ".codingplan" / "email.conf",
]


def _parse_bool(val: Optional[str]) -> bool:
    """解析布尔值"""
    if val is None:
        return True
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def _load_config_file() -> Optional[configparser.ConfigParser]:
    """从配置文件读取，返回 ConfigParser 或 None"""
    for path in CONFIG_PATHS:
        if path.exists():
            try:
                cp = configparser.ConfigParser()
                cp.read(path, encoding="utf-8")
                return cp
            except Exception:
                pass
    return None


def get_default_notify_emails() -> list[str]:
    """从配置文件读取默认收件人"""
    cp = _load_config_file()
    if not cp or not cp.has_section("notify"):
        return []
    emails = cp.get("notify", "emails", fallback="").strip()
    if not emails:
        return []
    return [e.strip() for e in emails.replace("，", ",").split(",") if e.strip()]


def _get_smtp_config() -> Optional[dict]:
    """
    读取 SMTP 配置，优先级：环境变量 > 配置文件
    配置文件路径：.codingplan/email.conf 或 ~/.config/codingplan/email.conf
    """
    # 1. 环境变量
    host = os.environ.get("CODINGPLAN_SMTP_HOST")
    port = os.environ.get("CODINGPLAN_SMTP_PORT")
    user = os.environ.get("CODINGPLAN_SMTP_USER")
    password = os.environ.get("CODINGPLAN_SMTP_PASSWORD")
    from_addr = os.environ.get("CODINGPLAN_SMTP_FROM", user)
    use_tls = os.environ.get("CODINGPLAN_SMTP_TLS")

    # 2. 从配置文件补充（环境变量未设置时）
    cp = _load_config_file()
    if cp and cp.has_section("smtp"):
        s = cp["smtp"]
        host = host or s.get("host")
        port = port or s.get("port", "587")
        user = user or s.get("user")
        password = password or s.get("password")
        from_addr = from_addr or s.get("from", user) or user
        if use_tls is None:
            use_tls = s.get("use_tls", "1")

    if not host or not user or not password:
        return None

    return {
        "host": host.strip(),
        "port": int(str(port).strip() or "587"),
        "user": user.strip(),
        "password": password.strip(),
        "from_addr": (from_addr or user).strip(),
        "use_tls": _parse_bool(use_tls),
    }


def send_notification(
    to_emails: list[str],
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
) -> bool:
    """
    发送邮件通知

    Args:
        to_emails: 收件人列表
        subject: 主题
        body_text: 纯文本正文
        body_html: 可选 HTML 正文

    Returns:
        True 发送成功，False 发送失败或未配置
    """
    if not to_emails:
        return False

    config = _get_smtp_config()
    if not config or not config.get("user") or not config.get("password"):
        print("提示: 未配置 SMTP，跳过邮件通知。无需邮件时可忽略；需要时请配置 .codingplan/email.conf 或环境变量，详见 docs/EMAIL-NOTIFICATION.md")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config["from_addr"] or config["user"]
    msg["To"] = ", ".join(to_emails)

    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    if body_html:
        msg.attach(MIMEText(body_html, "html", "utf-8"))

    try:
        if config["use_tls"]:
            context = ssl.create_default_context()
            with smtplib.SMTP(config["host"], config["port"]) as server:
                server.starttls(context=context)
                server.login(config["user"], config["password"])
                server.sendmail(config["from_addr"], to_emails, msg.as_string())
        else:
            with smtplib.SMTP_SSL(config["host"], config["port"], context=ssl.create_default_context()) as server:
                server.login(config["user"], config["password"])
                server.sendmail(config["from_addr"], to_emails, msg.as_string())
        print(f"已发送邮件通知至: {', '.join(to_emails)}")
        return True
    except Exception as e:
        print(f"邮件发送失败: {e}")
        return False


def send_workflow_complete(
    to_emails: list[str],
    success: bool,
    project_path: str,
    files_processed: list[str],
    duration_str: str,
    error_msg: Optional[str] = None,
) -> bool:
    """发送工作流完成通知"""
    status = "成功" if success else "失败"
    subject = f"[CodingPlan] 需求处理{status} - {project_path}"

    body_lines = [
        f"状态: {status}",
        f"项目路径: {project_path}",
        f"处理文件数: {len(files_processed)}",
        f"耗时: {duration_str}",
        "",
        "已处理文件:",
    ]
    for f in files_processed:
        body_lines.append(f"  - {f}")
    if error_msg:
        body_lines.extend(["", "错误信息:", error_msg])

    body_text = "\n".join(body_lines)
    body_html = f"""
<html><body><pre style="font-family: sans-serif;">{body_text}</pre></body></html>
"""
    return send_notification(to_emails, subject, body_text, body_html)
