#!/bin/bash
# security_check.sh - PersonaAnalyzer CLI セキュリティチェックスクリプト

set -e  # エラー時に実行を停止

# 色付きの出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 PersonaAnalyzer CLI セキュリティチェックを開始します...${NC}"
echo "======================================================="

# 1. 依存関係の脆弱性チェック (pip-audit)
echo -e "\n${YELLOW}1. 依存関係の脆弱性チェック (pip-audit)${NC}"
echo "---------------------------------------------------"
if command -v pip-audit &> /dev/null; then
    echo "pip-audit を実行中..."
    if pip-audit --desc --format=table; then
        echo -e "${GREEN}✅ pip-audit: 脆弱性は検出されませんでした${NC}"
    else
        echo -e "${RED}⚠️ pip-audit: 脆弱性が検出されました${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ pip-audit がインストールされていません${NC}"
    echo "インストール方法: pip install pip-audit"
fi

# 2. セキュリティライブラリチェック (safety)
echo -e "\n${YELLOW}2. セキュリティライブラリチェック (safety)${NC}"
echo "---------------------------------------------------"
if command -v safety &> /dev/null; then
    echo "safety check を実行中..."
    if safety check --json; then
        echo -e "${GREEN}✅ safety: 既知の脆弱性は検出されませんでした${NC}"
    else
        echo -e "${RED}⚠️ safety: 既知の脆弱性が検出されました${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ safety がインストールされていません${NC}"
    echo "インストール方法: pip install safety"
fi

# 3. 静的セキュリティ解析 (bandit)
echo -e "\n${YELLOW}3. 静的セキュリティ解析 (bandit)${NC}"
echo "---------------------------------------------------"
if command -v bandit &> /dev/null; then
    echo "bandit を実行中..."
    if [ -d "./cli" ]; then
        if bandit -r ./cli -f json -o bandit_report.json; then
            echo -e "${GREEN}✅ bandit: セキュリティ問題は検出されませんでした${NC}"
        else
            echo -e "${RED}⚠️ bandit: セキュリティ問題が検出されました${NC}"
            echo "詳細: bandit_report.json を確認してください"
        fi
    else
        echo -e "${YELLOW}⚠️ ./cli ディレクトリが見つかりません${NC}"
    fi
else
    echo -e "${YELLOW}⚠️ bandit がインストールされていません${NC}"
    echo "インストール方法: pip install bandit"
fi

# 4. 設定ファイルのセキュリティチェック
echo -e "\n${YELLOW}4. 設定ファイルのセキュリティチェック${NC}"
echo "---------------------------------------------------"
CONFIG_DIR="$HOME/.persona-analyzer"
if [ -d "$CONFIG_DIR" ]; then
    echo "設定ディレクトリの権限をチェック中..."
    
    # ディレクトリの権限チェック (700 = rwx------)
    PERMS=$(stat -c "%a" "$CONFIG_DIR" 2>/dev/null || stat -f "%A" "$CONFIG_DIR" 2>/dev/null || echo "unknown")
    if [ "$PERMS" = "700" ]; then
        echo -e "${GREEN}✅ 設定ディレクトリの権限: 適切 (700)${NC}"
    else
        echo -e "${RED}⚠️ 設定ディレクトリの権限: 不適切 ($PERMS)${NC}"
        echo "修正方法: chmod 700 $CONFIG_DIR"
    fi
    
    # 設定ファイルの権限チェック
    if [ -f "$CONFIG_DIR/config.yaml" ]; then
        CONFIG_PERMS=$(stat -c "%a" "$CONFIG_DIR/config.yaml" 2>/dev/null || stat -f "%A" "$CONFIG_DIR/config.yaml" 2>/dev/null || echo "unknown")
        if [ "$CONFIG_PERMS" = "600" ]; then
            echo -e "${GREEN}✅ 設定ファイルの権限: 適切 (600)${NC}"
        else
            echo -e "${RED}⚠️ 設定ファイルの権限: 不適切 ($CONFIG_PERMS)${NC}"
            echo "修正方法: chmod 600 $CONFIG_DIR/config.yaml"
        fi
    fi
else
    echo -e "${YELLOW}⚠️ 設定ディレクトリが見つかりません: $CONFIG_DIR${NC}"
fi

# 5. 環境変数のセキュリティチェック
echo -e "\n${YELLOW}5. 環境変数のセキュリティチェック${NC}"
echo "---------------------------------------------------"
SENSITIVE_VARS=("API_KEY" "SECRET_KEY" "PASSWORD" "TOKEN" "PRIVATE_KEY")
FOUND_SENSITIVE=false

for var in "${SENSITIVE_VARS[@]}"; do
    if env | grep -q "^$var="; then
        echo -e "${RED}⚠️ 機密情報を含む可能性のある環境変数が設定されています: $var${NC}"
        FOUND_SENSITIVE=true
    fi
done

if [ "$FOUND_SENSITIVE" = false ]; then
    echo -e "${GREEN}✅ 機密情報を含む環境変数は検出されませんでした${NC}"
fi

# 6. 重要なファイルの暗号化チェック
echo -e "\n${YELLOW}6. 重要なファイルの暗号化チェック${NC}"
echo "---------------------------------------------------"
SENSITIVE_FILES=("$CONFIG_DIR/config.yaml" "$CONFIG_DIR/credentials.json" "$CONFIG_DIR/private_key.pem")
UNENCRYPTED_FILES=()

for file in "${SENSITIVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        # ファイルが暗号化されているかの簡易チェック（実際にはより詳細な検証が必要）
        if file "$file" | grep -q "text"; then
            UNENCRYPTED_FILES+=("$file")
        fi
    fi
done

if [ ${#UNENCRYPTED_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ 重要なファイルの暗号化: 適切${NC}"
else
    echo -e "${RED}⚠️ 以下のファイルが暗号化されていない可能性があります:${NC}"
    for file in "${UNENCRYPTED_FILES[@]}"; do
        echo "  - $file"
    done
fi

# 7. ネットワークセキュリティチェック
echo -e "\n${YELLOW}7. ネットワークセキュリティチェック${NC}"
echo "---------------------------------------------------"
if [ -f "$CONFIG_DIR/config.yaml" ]; then
    # HTTPSの使用確認
    if grep -q "https://" "$CONFIG_DIR/config.yaml"; then
        echo -e "${GREEN}✅ HTTPS接続が設定されています${NC}"
    else
        echo -e "${RED}⚠️ HTTPS接続が設定されていません${NC}"
    fi
    
    # SSL証明書検証の確認
    if grep -q "verify_ssl.*true" "$CONFIG_DIR/config.yaml"; then
        echo -e "${GREEN}✅ SSL証明書検証が有効です${NC}"
    else
        echo -e "${RED}⚠️ SSL証明書検証が無効です${NC}"
    fi
fi

# 8. ログファイルのセキュリティチェック
echo -e "\n${YELLOW}8. ログファイルのセキュリティチェック${NC}"
echo "---------------------------------------------------"
LOG_DIR="$CONFIG_DIR/logs"
if [ -d "$LOG_DIR" ]; then
    LOG_PERMS=$(stat -c "%a" "$LOG_DIR" 2>/dev/null || stat -f "%A" "$LOG_DIR" 2>/dev/null || echo "unknown")
    if [ "$LOG_PERMS" = "700" ]; then
        echo -e "${GREEN}✅ ログディレクトリの権限: 適切 (700)${NC}"
    else
        echo -e "${RED}⚠️ ログディレクトリの権限: 不適切 ($LOG_PERMS)${NC}"
    fi
    
    # ログファイル内の機密情報チェック
    if find "$LOG_DIR" -name "*.log" -exec grep -l -i "password\|secret\|token\|key" {} \; | head -1 > /dev/null; then
        echo -e "${RED}⚠️ ログファイルに機密情報が含まれている可能性があります${NC}"
    else
        echo -e "${GREEN}✅ ログファイルに機密情報は検出されませんでした${NC}"
    fi
fi

# 9. 依存関係のバージョンチェック
echo -e "\n${YELLOW}9. 重要な依存関係のバージョンチェック${NC}"
echo "---------------------------------------------------"
CRITICAL_PACKAGES=("requests:2.31.0" "httpx:0.25.2" "pyyaml:6.0" "sqlalchemy:1.4.49" "cryptography:41.0.0")

for package_info in "${CRITICAL_PACKAGES[@]}"; do
    IFS=':' read -r package min_version <<< "$package_info"
    
    if pip show "$package" &> /dev/null; then
        installed_version=$(pip show "$package" | grep "Version:" | cut -d' ' -f2)
        echo "  $package: $installed_version (required: >=$min_version)"
        
        # バージョン比較（簡易版）
        if python3 -c "from packaging import version; exit(0 if version.parse('$installed_version') >= version.parse('$min_version') else 1)" 2>/dev/null; then
            echo -e "    ${GREEN}✅ OK${NC}"
        else
            echo -e "    ${RED}⚠️ アップデートが必要です${NC}"
        fi
    else
        echo -e "  $package: ${YELLOW}インストールされていません${NC}"
    fi
done

# 10. セキュリティ設定の推奨事項
echo -e "\n${YELLOW}10. セキュリティ設定の推奨事項${NC}"
echo "---------------------------------------------------"
echo "以下の設定を確認してください:"
echo "  • 定期的なパッケージアップデート"
echo "  • 強力なパスワード・認証の使用"
echo "  • ログの定期的な確認"
echo "  • バックアップの暗号化"
echo "  • 不要なファイルの削除"

# 結果のサマリー
echo -e "\n${BLUE}=======================================================${NC}"
echo -e "${BLUE}🔍 セキュリティチェック完了${NC}"
echo -e "${BLUE}=======================================================${NC}"

# 推奨アクション
echo -e "\n${YELLOW}推奨アクション:${NC}"
echo "1. 検出された問題を修正してください"
echo "2. 定期的にこのスクリプトを実行してください"
echo "3. セキュリティアップデートを適用してください"
echo "4. 設定ファイルを定期的に見直してください"

echo -e "\n${GREEN}セキュリティチェックが完了しました！${NC}"