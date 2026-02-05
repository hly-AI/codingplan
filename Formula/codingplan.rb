# Homebrew Formula for CodingPlan
# 使用方式:
#   brew tap hly-AI/homebrew-codingplan https://github.com/hly-AI/homebrew-codingplan
#   brew install codingplan              # 需先发布 tag 并填写 sha256
#   brew install codingplan --HEAD        # 从 main 分支安装（无 tag 时可用）
#
# 发布 tag 后需更新 url 和 sha256:
#   curl -sL "https://github.com/hly-AI/codingplan/archive/refs/tags/v0.1.0.tar.gz" -o /tmp/codingplan.tar.gz
#   shasum -a 256 /tmp/codingplan.tar.gz

class Codingplan < Formula
  desc "基于 Cursor CLI 的自动化需求处理、代码实现与测试闭环工具"
  homepage "https://github.com/hly-AI/codingplan"
  url "https://github.com/hly-AI/codingplan/archive/refs/tags/v0.1.0.tar.gz"
  sha256 ""  # 发布 tag 后执行上述命令获取
  license "MIT"

  head "https://github.com/hly-AI/codingplan.git", branch: "main"

  depends_on "python@3.11"

  def install
    system "python3", "-m", "pip", "install", "--prefix=#{prefix}", "--no-deps", "."
  end

  test do
    system "#{bin}/codingplan", "--version"
  end
end
