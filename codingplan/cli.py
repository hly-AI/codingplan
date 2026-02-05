"""CodingPlan CLI 入口"""

import sys
from pathlib import Path

from .workflow import run_workflow
from . import notify
from . import __version__


def main():
    """主入口"""
    import argparse

    parser = argparse.ArgumentParser(
        prog="codingplan",
        description="基于 Cursor CLI 的自动化需求处理、代码实现与测试闭环工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  codingplan ./requirements          # 处理 requirements 目录下所有需求
  codingplan ./docs/reqs -r           # 从上次中断处继续
  codingplan ./reqs -f feature-a.md   # 仅处理指定文件
  codingplan ./reqs -s ugc_kmp        # 仅限在 ugc_kmp 目录内实现
  codingplan ./reqs -H "需求含 iOS+Android，请确保两平台都实现"  # 额外提醒
  codingplan ./reqs -s ugc_kmp -H "需求含 iOS+Android，两平台都要实现"
  codingplan ./reqs -u uidesign           # 指定 UI 设计目录（默认即 uidesign）
  codingplan ./reqs -e user@example.com   # 完成后发邮件通知

前置条件:
  1. 已安装 Cursor CLI: curl https://cursor.com/install -fsS | bash
  2. 已登录 Cursor 账号
  3. 在项目根目录下执行
        """,
    )

    parser.add_argument(
        "req_dir",
        type=str,
        help="需求文件所在目录（相对于当前工作目录）",
    )
    parser.add_argument(
        "-r", "--resume",
        action="store_true",
        help="从上次中断处继续（默认会自动检测并续传）",
    )
    parser.add_argument(
        "-F", "--fresh",
        action="store_true",
        help="强制重新开始，忽略上次未完成状态",
    )
    parser.add_argument(
        "-f", "--file",
        dest="single_file",
        type=str,
        metavar="FILE",
        help="仅处理指定文件",
    )
    parser.add_argument(
        "-s", "--scope",
        dest="scope",
        type=str,
        metavar="DIR",
        help="实现范围限制：仅在此目录内实现/修改代码（如 ugc_kmp），其他目录不修改",
    )
    parser.add_argument(
        "-H", "--hint",
        dest="hint",
        type=str,
        metavar="TEXT",
        help="额外上下文或提醒，会注入到各步骤 prompt 中（如：需求包含 iOS 和 Android，请确保两个平台都实现）",
    )
    parser.add_argument(
        "-u", "--ui-dir",
        dest="ui_dir",
        type=str,
        metavar="DIR",
        default=None,
        help="UI 设计目录（Figma 链接与交互说明），默认 uidesign。空字符串表示不使用",
    )
    parser.add_argument(
        "-e", "--notify-email",
        dest="notify_email",
        type=str,
        metavar="EMAIL",
        help="任务完成后发送邮件到此地址（可多次指定）。可配置 .codingplan/email.conf 或环境变量",
        action="append",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    req_dir = project_root / args.req_dir
    # UI 设计目录：未指定用 uidesign，空字符串表示不使用
    ui_dir = None
    if args.ui_dir is not None:
        if args.ui_dir.strip():
            ui_dir = project_root / args.ui_dir.strip()
    else:
        ui_dir = project_root / "uidesign"

    if not req_dir.exists():
        print(f"错误: 目录不存在: {req_dir}")
        sys.exit(1)

    if not req_dir.is_dir():
        print(f"错误: 不是目录: {req_dir}")
        sys.exit(1)

    # 收件人：命令行 -e 优先，否则从配置文件 [notify] emails 读取
    notify_emails = args.notify_email or notify.get_default_notify_emails()

    exit_code = run_workflow(
        project_root=project_root,
        req_dir=req_dir,
        ui_dir=ui_dir,
        resume=args.resume,
        fresh=args.fresh,
        single_file=args.single_file,
        scope=args.scope,
        hint=args.hint,
        notify_emails=notify_emails,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
