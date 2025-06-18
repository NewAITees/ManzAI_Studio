#!/bin/bash

# ManzAI Studio デプロイスクリプト
# 使用方法: ./scripts/deploy.sh [環境]
# 環境: production, staging (デフォルトは production)

set -e  # エラーが発生したらスクリプトを終了

# 環境設定
ENV=${1:-production}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# カラー出力設定
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ヘルパー関数
log_info() {
    echo -e "${GREEN}INFO:${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}WARNING:${NC} $1"
}

log_error() {
    echo -e "${RED}ERROR:${NC} $1"
}

# 環境チェック
if [ "$ENV" != "production" ] && [ "$ENV" != "staging" ]; then
    log_error "無効な環境指定です: $ENV (production または staging を指定してください)"
    exit 1
fi

# 作業ディレクトリをプロジェクトルートに変更
cd "$PROJECT_ROOT"

# Git リポジトリであることを確認
if [ ! -d .git ]; then
    log_error "Gitリポジトリではありません。デプロイを中止します。"
    exit 1
fi

# 環境に応じた設定
if [ "$ENV" == "production" ]; then
    DOCKER_COMPOSE_FILE="docker-compose.yml"
    ENV_FILE=".env.production"
else
    DOCKER_COMPOSE_FILE="docker-compose.staging.yml"
    ENV_FILE=".env.staging"
fi

# 必要なファイルの存在確認
if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    log_error "Docker Compose ファイルが見つかりません: $DOCKER_COMPOSE_FILE"
    exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
    log_warning "環境設定ファイルが見つかりません: $ENV_FILE"
    log_warning "デフォルトの環境変数を使用します"
fi

# 最新のコードを取得
log_info "最新のコードを取得しています..."
git pull origin main

# バックアップの作成
log_info "現在の状態をバックアップしています..."
BACKUP_DIR="backups/${ENV}_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

# 既存のコンテナが実行中の場合は設定をバックアップ
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${BACKUP_DIR}/"
fi

# タグ付け
if [ "$ENV" == "production" ]; then
    log_info "リリースタグを作成しています..."
    git tag "release-${TIMESTAMP}"
    git push origin "release-${TIMESTAMP}"
fi

# ビルドとデプロイ
log_info "${ENV} 環境にデプロイしています..."

# 環境変数の読み込み
if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
fi

# Docker イメージのビルドとデプロイ
docker-compose -f "$DOCKER_COMPOSE_FILE" build
docker-compose -f "$DOCKER_COMPOSE_FILE" down
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d

# ヘルスチェック
log_info "ヘルスチェックを実行しています..."
sleep 10  # サービスの起動を待つ

# API ヘルスチェック
HEALTH_CHECK_URL="http://localhost:5000/api/status"
if curl -s "$HEALTH_CHECK_URL" | grep -q "status.*ok"; then
    log_info "ヘルスチェック成功: APIサーバーは正常に動作しています"
else
    log_error "ヘルスチェック失敗: APIサーバーの応答が正常ではありません"
    log_info "ログを確認してください: docker-compose -f $DOCKER_COMPOSE_FILE logs"
fi

log_info "デプロイ完了しました！"
echo -e "環境: ${GREEN}${ENV}${NC}"
echo -e "タイムスタンプ: ${GREEN}${TIMESTAMP}${NC}"
echo -e "アプリケーションURL: ${GREEN}http://localhost:5000${NC}"

# デプロイ後の操作手順
echo -e "\n${YELLOW}次のコマンドでログを確認できます:${NC}"
echo "docker-compose -f $DOCKER_COMPOSE_FILE logs -f"

exit 0
