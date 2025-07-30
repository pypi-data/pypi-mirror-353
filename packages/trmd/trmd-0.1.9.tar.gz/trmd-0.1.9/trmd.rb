class Trmd < Formula
  include Language::Python::Virtualenv

  desc "Translate Markdown using OpenAI"
  homepage "https://github.com/rioriost/homebrew-trmd/"
  url "https://files.pythonhosted.org/packages/f8/35/266ae6ded1571b996d4bcac41e977b9a4374f4b74471224997b5f07ec3df/trmd-0.1.8.tar.gz"
  sha256 "577bddea1ea571a079b2d6f734cd8f02b42af82f3410292336c2ded2260bb9ab"
  license "MIT"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
    system libexec/"bin/python", "-m", "pip", "install", "openai"
  end

  test do
    system "#{bin}/trmd", "--help"
  end
end
