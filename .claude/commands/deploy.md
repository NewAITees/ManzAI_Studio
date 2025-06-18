# デプロイメントコマンド

ManzAI Studioの本番環境デプロイに関するコマンド集です。

## 本番環境構築

### Docker本番デプロイ

```bash
# 本番環境ビルド・起動
make prod

# 本番設定でのビルド
docker-compose build

# 本番環境でのサービス起動
docker-compose up -d

# サービス状態確認
docker-compose ps
```

### 手動本番デプロイ

```bash
# 本番用Python環境構築
export FLASK_ENV=production
uv sync --no-dev

# フロントエンド本番ビルド
cd frontend/
npm ci --production
npm run build

# 静的ファイル配信設定
# （通常はNginxやApacheで配信）
```

## 環境設定

### 本番環境変数

```bash
# 本番環境設定ファイル作成
cat > .env.production << EOF
FLASK_ENV=production
DEBUG=False
VOICEVOX_URL=http://voicevox:50021
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=gemma3:4b
LOG_LEVEL=INFO
EOF
```

### セキュリティ設定

```bash
# ファイル権限設定
chmod 600 .env.production
chmod -R 755 frontend/build/
chmod -R 644 frontend/public/live2d/

# ユーザー作成（本番サーバー）
sudo useradd -m -s /bin/bash manzai
sudo usermod -aG docker manzai
```

## デプロイメント検証

### 本番環境テスト

```bash
# ヘルスチェック
curl -f http://localhost:5000/api/health

# API動作確認
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "テスト"}'

# フロントエンド確認
curl -f http://localhost:3000

# 外部サービス確認
curl -f http://localhost:11434/api/tags
curl -f http://localhost:50021/version
```

### パフォーマンステスト

```bash
# 同時接続テスト
for i in {1..10}; do
  curl -s http://localhost:5000/api/health &
done
wait

# レスポンス時間測定
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/health

# curl-format.txt内容
echo 'time_namelookup:  %{time_namelookup}\ntime_connect:     %{time_connect}\ntime_appconnect:  %{time_appconnect}\ntime_pretransfer: %{time_pretransfer}\ntime_redirect:    %{time_redirect}\ntime_starttransfer: %{time_starttransfer}\ntime_total:       %{time_total}\n' > curl-format.txt
```

## モニタリング

### ログ監視

```bash
# リアルタイムログ監視
docker-compose logs -f

# エラーログ抽出
docker-compose logs | grep -i error

# アクセスログ分析
docker-compose logs backend | grep "GET\|POST" | tail -20
```

### リソース監視

```bash
# コンテナリソース使用量
docker stats

# ディスク使用量監視
df -h
du -sh /var/lib/docker/

# メモリ使用量詳細
free -h
cat /proc/meminfo | grep -E "MemTotal|MemFree|MemAvailable"
```

## バックアップ

### データバックアップ

```bash
# Dockerボリュームバックアップ
docker run --rm -v manzai_ollama_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/ollama_data_backup.tar.gz -C /data .

docker run --rm -v manzai_voicevox_data:/data -v $(pwd):/backup alpine \
  tar czf /backup/voicevox_data_backup.tar.gz -C /data .

# 設定ファイルバックアップ
tar czf config_backup.tar.gz \
  docker-compose.yml \
  .env.production \
  frontend/public/live2d/
```

### データリストア

```bash
# Dockerボリュームリストア
docker run --rm -v manzai_ollama_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/ollama_data_backup.tar.gz -C /data

docker run --rm -v manzai_voicevox_data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/voicevox_data_backup.tar.gz -C /data
```

## アップデート

### ローリングアップデート

```bash
# 新バージョンのプル
git pull origin main

# 段階的サービス更新
docker-compose up -d --no-deps backend
sleep 30
docker-compose up -d --no-deps frontend

# 更新確認
curl -f http://localhost:5000/api/health
```

### ホットスワップ（ダウンタイム最小化）

```bash
# 新コンテナ準備
docker-compose build

# バックエンド更新
docker-compose up -d --no-deps --scale backend=2 backend
sleep 10
docker-compose up -d --no-deps --scale backend=1 backend

# フロントエンド更新
docker-compose up -d --no-deps frontend
```

## 災害復旧

### 緊急停止

```bash
# 全サービス緊急停止
docker-compose down

# 強制停止
docker-compose kill

# コンテナ削除
docker-compose rm -f
```

### サービス復旧

```bash
# データ整合性チェック
docker volume inspect manzai_ollama_data
docker volume inspect manzai_voicevox_data

# 段階的復旧
docker-compose up -d ollama voicevox
sleep 60
docker-compose up -d backend
sleep 30
docker-compose up -d frontend

# 復旧確認
./scripts/health_check.sh
```

## セキュリティ

### 本番セキュリティチェック

```bash
# 脆弱性スキャン
uv run safety check --json > security_report.json
uv run bandit -r src/ -f json > bandit_report.json

# コンテナセキュリティ
docker scan manzai-studio_backend
docker scan manzai-studio_frontend

# ネットワークセキュリティ
nmap -sV localhost -p 3000,5000,11434,50021
```

### アクセス制御

```bash
# ファイアウォール設定（例：UFW）
sudo ufw allow 22     # SSH
sudo ufw allow 80     # HTTP
sudo ufw allow 443    # HTTPS
sudo ufw deny 5000    # Backend直接アクセス拒否
sudo ufw deny 11434   # Ollama直接アクセス拒否
sudo ufw deny 50021   # VoiceVox直接アクセス拒否

# リバースプロキシ設定（Nginx例）
cat > /etc/nginx/sites-available/manzai-studio << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
```

## 運用メンテナンス

### 定期メンテナンス

```bash
# ログローテーション
docker-compose logs --since 24h > logs/daily_$(date +%Y%m%d).log

# 不要なDockerリソース削除
docker system prune -f
docker image prune -f

# システムアップデート（OS）
sudo apt update && sudo apt upgrade -y
```

### 容量管理

```bash
# ディスク容量警告
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Warning: Disk usage is ${DISK_USAGE}%"
fi

# 古いログ削除
find logs/ -name "*.log" -mtime +30 -delete

# 古いDockerイメージ削除
docker image prune -a -f --filter "until=720h"
```
