"""CodingPlan CLI 入口"""

import sys
from pathlib import Path

from .workflow import run_workflow
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
  codingplan ./docs/reqs -r          # 从上次中断处继续
  codingplan ./reqs -f feature-a.md   # 仅处理指定文件

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
        help="从上次中断处继续",
    )
    parser.add_argument(
        "-f", "--file",
        dest="single_file",
        type=str,
        metavar="FILE",
        help="仅处理指定文件",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    project_root = Path.cwd()
    req_dir = project_root / args.req_dir

    if not req_dir.exists():
        print(f"错误: 目录不存在: {req_dir}")
        sys.exit(1)

    if not req_dir.is_dir():
        print(f"错误: 不是目录: {req_dir}")
        sys.exit(1)

    exit_code = run_workflow(
        project_root=project_root,
        req_dir=req_dir,
        resume=args.resume,
        single_file=args.single_file,
    )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
