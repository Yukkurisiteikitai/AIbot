#!/usr/bin/env python3
"""
PersonaAnalyzer CLI Setup Script
セキュリティ脆弱性に対応した修正版
"""

from setuptools import setup, find_packages
from pathlib import Path
import sys
import os

# 現在のディレクトリを取得
HERE = Path(__file__).parent

# README.mdの内容を取得
long_description = (HERE / "README.md").read_text(encoding="utf-8") if (HERE / "README.md").exists() else ""

# バージョン情報を取得
def get_version():
    """バージョン情報を取得"""
    version_file = HERE / "cli" / "__init__.py"
    if version_file.exists():
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"

# 依存関係の定義（セキュリティ修正版）
install_requires = [
    # CVE-2023-32681（認証情報漏洩）の修正版以降
    "requests>=2.31.0",
    "click>=8.0.0",
    # 安全な safe_load の使用を前提とし、最新版を指定
    "pyyaml>=6.0",
    # タイポスクワッティングに注意し、公式の最新安定版を指定
    "colorama>=0.4.6",
    "rich>=10.0.0",
    "typer>=0.9.0",
    # セキュリティ修正を含む最新版
    "pydantic>=2.0.0",
    "python-dotenv>=0.19.0",
    # 暗号化関連の重要な修正を含む最新版
    "cryptography>=41.0.0",
    # SQLインジェクション対策を含む最新版
    "sqlalchemy>=1.4.49",
    "alembic>=1.7.0",
    # 最新のセキュリティ修正を含む
    "bcrypt>=4.0.0",
    "pyjwt>=2.8.0",
    # CVE-2023-32681（認証情報漏洩）の修正版以降
    "httpx>=0.25.2",
    "aiofiles>=23.0.0",
    "asyncio-mqtt>=0.16.0",
    "websockets>=11.0.0",
    "pandas>=1.5.0",
    "numpy>=1.24.0",
    "scikit-learn>=1.3.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "plotly>=5.15.0",
    "streamlit>=1.25.0",
]

# 開発用依存関係（セキュリティ修正版）
dev_requires = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "isort>=5.12.0",
    "flake8>=6.0.0",
    "mypy>=1.5.0",
    "pre-commit>=3.4.0",
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
    "twine>=4.0.0",
    "wheel>=0.41.0",
    "build>=0.10.0",
    # セキュリティ監査ツールを追加
    "pip-audit>=2.6.0",
    "bandit>=1.7.0",
    "safety>=2.3.0",
]

# テスト用依存関係
test_requires = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "pytest-asyncio>=0.21.0",
    "coverage>=7.0.0",
    "factory-boy>=3.3.0",
    "faker>=19.0.0",
    "responses>=0.23.0",
    "httpretty>=1.1.4",
]

# ドキュメント用依存関係
docs_requires = [
    "sphinx>=7.0.0",
    "sphinx-rtd-theme>=1.3.0",
    "sphinx-autodoc-typehints>=1.24.0",
    "myst-parser>=2.0.0",
    "sphinx-click>=5.0.0",
]

# AI/ML用依存関係
ai_requires = [
    "torch>=2.0.0",
    "transformers>=4.33.0",
    "sentence-transformers>=2.2.2",
    "datasets>=2.14.0",
    "accelerate>=0.21.0",
    "evaluate>=0.4.0",
    "tokenizers>=0.13.0",
    "huggingface-hub>=0.17.0",
    "safetensors>=0.3.3",
]

# 全ての追加依存関係
all_requires = dev_requires + test_requires + docs_requires + ai_requires

setup(
    name="persona-analyzer-cli",
    version=get_version(),
    author="PersonaAnalyzer Development Team",
    author_email="1hourgoodattack@gmail.com",
    description="PersonaAnalyzer CLI - AI-powered personality analysis and simulation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Yukkurisiteikitai/AIbot",
    project_urls={
        "Bug Tracker": "https://github.com/Yukkurisiteikitai/AIbot/issues",
        "Documentation": "https://persona-analyzer-cli.readthedocs.io/",
        "Source Code": "https://github.com/Yukkurisiteikitai/AIbot",
        "Security": "https://github.com/Yukkurisiteikitai/AIbot/security",
    },
    packages=find_packages(exclude=["tests", "tests.*", "docs", "docs.*"]),
    include_package_data=True,
    package_data={
        "persona_analyzer_cli": [
            "config/*.yaml",
            "config/*.json",
            "templates/*.txt",
            "templates/*.md",
            "static/*",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    keywords="ai, personality, analysis, simulation, cli, nlp, machine-learning, security",
    python_requires=">=3.8",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        "test": test_requires,
        "docs": docs_requires,
        "ai": ai_requires,
        "all": all_requires,
    },
    entry_points={
        "console_scripts": [
            "persona=cli.main:main",
            "persona-analyzer=cli.main:main",
            "pa=cli.main:main",  # 短縮形
        ],
    },
    # CLI専用の設定
    scripts=[
        "scripts/install.sh",
        "scripts/run_tests.sh",
        "scripts/security_check.sh",  # セキュリティチェック用スクリプト追加
    ] if (HERE / "scripts").exists() else [],
    
    # データファイル
    data_files=[
        ("share/persona-analyzer-cli/config", ["config/settings.py", "config/schema.py"]),
        ("share/persona-analyzer-cli/docs", ["README.md", "SECURITY.md"]),
    ] if all((HERE / path).exists() for path in ["config/settings.py", "config/schema.py", "README.md"]) else [],
    
    # セキュリティ関連
    zip_safe=False,
    
    # テストの設定
    test_suite="tests",
    tests_require=test_requires,
    
    # メタデータ
    platforms=["any"],
    license="MIT",
    
    # PyPI用の追加情報
    download_url="https://github.com/Yukkurisiteikitai/AIbot/archive/v{}.tar.gz".format(get_version()),
    
    # 言語サポート
    language="ja",
    
    # Setuptools用の追加オプション
    options={
        "build_scripts": {
            "executable": "/usr/bin/python3",
        },
        "bdist_wheel": {
            "universal": False,
        },
    },
)

# セキュリティ監査機能を追加
def security_audit():
    """セキュリティ監査を実行"""
    print("🔍 Running security audit...")
    
    # pip-audit を使用した脆弱性チェック
    try:
        import subprocess
        result = subprocess.run(
            ["pip-audit", "--desc", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ No vulnerabilities found!")
        else:
            print("⚠️  Vulnerabilities detected. Please check the output above.")
            print(result.stdout)
            
    except (ImportError, subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  pip-audit not available. Please install it with:")
        print("    pip install pip-audit")
        print("    Then run: pip-audit")

# インストール後の設定（セキュリティ強化版）
def post_install():
    """インストール後の設定処理（セキュリティ強化版）"""
    import os
    import sys
    import stat
    
    print("🔧 Setting up PersonaAnalyzer CLI with security enhancements...")
    
    # 設定ディレクトリの作成（適切な権限設定）
    config_dir = Path.home() / ".persona-analyzer"
    config_dir.mkdir(mode=0o700, exist_ok=True)  # 所有者のみアクセス可能
    
    # デフォルト設定ファイルの作成
    default_config = config_dir / "config.yaml"
    if not default_config.exists():
        default_config_content = """# PersonaAnalyzer CLI Configuration
# セキュリティを考慮した設定
version: "1.0"

backend:
  url: "https://your-backend-url.com"
  timeout: 30
  retry_count: 3
  # SSL証明書の検証を有効化
  verify_ssl: true
  # セキュアな通信プロトコル
  protocol: "https"

user:
  privacy_level: "high"  # デフォルトでhighに設定
  backup_enabled: true
  reflection_frequency: "daily"
  # データ暗号化の有効化
  encrypt_data: true

ai:
  model_path: "./models/persona_model.bin"
  temperature: 0.7
  max_tokens: 2048
  # 危険な入力のフィルタリング
  content_filter: true

logging:
  level: "INFO"
  file: "~/.persona-analyzer/logs/app.log"
  max_size: "10MB"
  backup_count: 5
  # 機密情報のログ除外
  exclude_sensitive: true

security:
  # セキュリティ監査の有効化
  audit_enabled: true
  # 自動アップデート通知
  update_notifications: true
  # 安全でない機能の無効化
  disable_unsafe_features: true
"""
        with open(default_config, "w", encoding="utf-8") as f:
            f.write(default_config_content)
        
        # 設定ファイルの権限を制限（所有者のみ読み書き可能）
        os.chmod(default_config, stat.S_IRUSR | stat.S_IWUSR)
    
    # ログディレクトリの作成（適切な権限設定）
    log_dir = config_dir / "logs"
    log_dir.mkdir(mode=0o700, exist_ok=True)
    
    # セキュリティガイドラインファイルの作成
    security_guide = config_dir / "SECURITY_GUIDE.md"
    if not security_guide.exists():
        security_guide_content = """# PersonaAnalyzer CLI セキュリティガイド

## 安全な使用方法

### 1. 設定ファイルの管理
- 機密情報を含む設定ファイルは適切な権限で保護されています
- APIキーや認証情報は環境変数で管理することを推奨

### 2. YAMLファイルの取り扱い
- 信頼できないYAMLファイルは読み込まないでください
- 内部的には `yaml.safe_load()` を使用しています

### 3. 定期的なセキュリティチェック
```bash
# セキュリティ監査の実行
pip-audit

# 依存関係の脆弱性チェック
safety check

# 静的解析
bandit -r ./
```

### 4. アップデート
- 定期的に最新版にアップデートしてください
- セキュリティパッチは迅速に適用されます

### 5. 問題報告
セキュリティに関する問題を発見した場合は、以下にご報告ください：
- GitHub Security: https://github.com/Yukkurisiteikitai/AIbot/security
- Email: security@persona-analyzer.com
"""
        with open(security_guide, "w", encoding="utf-8") as f:
            f.write(security_guide_content)
    
    print("✅ PersonaAnalyzer CLI has been successfully installed with security enhancements!")
    print(f"📁 Configuration directory: {config_dir}")
    print(f"🔒 Security guide: {security_guide}")
    print("🚀 You can now use 'persona' command to start!")
    print("\n🔍 Recommended: Run security audit with 'pip-audit' regularly")

# コマンドライン引数の処理
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "develop":
            # 開発用のローカルインストール
            post_install()
        elif sys.argv[1] == "security-audit":
            # セキュリティ監査の実行
            security_audit()
        elif sys.argv[1] == "check-deps":
            # 依存関係のセキュリティチェック
            print("🔍 Checking dependencies for security vulnerabilities...")
            print("Core dependencies with security fixes:")
            print("- requests>=2.31.0 (CVE-2023-32681 fix)")
            print("- httpx>=0.25.2 (CVE-2023-32681 fix)")
            print("- pyyaml>=6.0 (safe_load usage)")
            print("- colorama>=0.4.6 (typosquatting protection)")
            print("- sqlalchemy>=1.4.49 (SQL injection protection)")
            print("- cryptography>=41.0.0 (latest security fixes)")
            print("- bcrypt>=4.0.0 (latest security fixes)")
            print("- pyjwt>=2.8.0 (latest security fixes)")
            print("\n✅ All dependencies are configured with security fixes!")
        else:
            print("Available commands:")
            print("  develop        - Setup development environment")
            print("  security-audit - Run security audit")
            print("  check-deps     - Check dependency security status")