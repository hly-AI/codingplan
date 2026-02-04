# Homebrew Formula for CodingPlan
# 使用方式:
#   brew tap your-org/codingplan  # 若使用独立 tap 仓库
#   brew install codingplan
#
# 或直接安装（若 formula 在 homebrew-tap 中）:
#   brew install your-org/tap/codingplan

class Codingplan < Formula
  desc "基于 Cursor CLI 的自动化需求处理、代码实现与测试闭环工具"
  homepage "https://github.com/your-org/codingplan"
  url "https://github.com/your-org/codingplan/archive/refs/tags/v0.1.0.tar.gz"
  sha256 ""  # 发布时填写: openssl dgst -sha256 < tarball
  license "MIT"

  depends_on "python@3.11"

  def install
    system "pip3", "install", *std_pip_args, "."
  end

  test do
    system "#{bin}/codingplan", "--version"
  end
end
