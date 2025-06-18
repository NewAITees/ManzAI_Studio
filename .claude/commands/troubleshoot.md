# トラブルシューティングコマンド

ManzAI Studioでよく発生する問題の診断と解決方法です。

## サービス起動問題

### 全サービスの状態確認

```bash
# Dockerサービス状態確認
docker-compose -f docker-compose.dev.yml ps

# ポート使用状況確認
netstat -tulpn | grep -E ":(3000|5000|11434|50021)"

# プロセス確認
ps aux | grep -E "(node|python|ollama|voicevox)"
```

### 個別サービス診断

```bash
# フロントエンド接続テスト
curl -f http://localhost:3000 || echo "Frontend not responding"

# バックエンドAPI接続テスト
curl -f http://localhost:5000/api/health || echo "Backend not responding"

# Ollama接続テスト
curl -f http://localhost:11434/api/tags || echo "Ollama not responding"

# VoiceVox接続テスト
curl -f http://localhost:50021/version || echo "VoiceVox not responding"
```

## 依存関係問題

### Python環境診断

```bash
# Pythonバージョン確認
python --version
uv python list

# 仮想環境確認
which python
echo $VIRTUAL_ENV

# 依存関係確認
uv run pip list
uv run pip check

# 設定状況確認
uv run python -c "import sys; print(sys.path)"
```

### 依存関係修復

```bash
# 仮想環境再作成
rm -rf .venv
uv sync

# 依存関係強制再インストール
uv sync --reinstall

# 開発依存関係同期
uv sync --dev

# ロックファイル更新
uv lock --upgrade
```

### Node.js環境診断

```bash
cd frontend/

# Node.jsバージョン確認
node --version
npm --version

# 依存関係確認
npm list
npm audit

# パッケージキャッシュ確認
npm cache verify
```

### フロントエンド依存関係修復

```bash
cd frontend/

# node_modules削除・再インストール
rm -rf node_modules package-lock.json
npm install

# キャッシュクリア後再インストール
npm cache clean --force
npm install

# 脆弱性修正
npm audit fix
```

## Docker問題

### Docker環境診断

```bash
# Docker状態確認
docker --version
docker-compose --version
docker system info

# コンテナ状態確認
docker ps -a
docker-compose -f docker-compose.dev.yml ps

# ネットワーク状態確認
docker network ls
docker network inspect manzai-network
```

### Docker問題修復

```bash
# サービス再起動
make restart

# 完全クリーンアップ
make clean
docker system prune -f

# イメージ再ビルド
make rebuild

# ボリューム削除（データ消失注意）
docker-compose -f docker-compose.dev.yml down -v
docker volume prune -f
```

## Ollama問題

### Ollama診断

```bash
# Ollamaサービス状態
curl -s http://localhost:11434/api/tags | jq '.'

# インストール済みモデル確認
ollama list

# モデル情報詳細
ollama show gemma3:4b

# Ollamaログ確認
docker-compose -f docker-compose.dev.yml logs ollama
```

### Ollama問題修復

```bash
# 推奨モデルプル
ollama pull gemma3:4b

# 代替モデルプル
ollama pull phi3:mini

# モデル削除（容量不足時）
ollama rm llama2

# Ollamaサービス再起動
docker-compose -f docker-compose.dev.yml restart ollama
```

## VoiceVox問題

### VoiceVox診断

```bash
# VoiceVoxサービス状態
curl -s http://localhost:50021/version

# スピーカー一覧確認
curl -s http://localhost:50021/speakers | jq '.[0:3]'

# エンジン情報確認
curl -s http://localhost:50021/engine_manifest

# VoiceVoxログ確認
docker-compose -f docker-compose.dev.yml logs voicevox
```

### VoiceVox問題修復

```bash
# VoiceVoxサービス再起動
docker-compose -f docker-compose.dev.yml restart voicevox

# ボイスモデル確認
curl -s http://localhost:50021/speakers | jq '.[] | {name: .name, styles: .styles[].name}'

# 音声合成テスト
curl -X POST http://localhost:50021/audio_query \
  -H "Content-Type: application/json" \
  -d '{"text": "テストです", "speaker": 1}'
```

## テスト問題

### テスト環境診断

```bash
# テスト実行環境確認
uv run python -c "import pytest; print(pytest.__version__)"
uv run python -c "import sys; print('Python:', sys.version)"

# テスト設定確認
uv run pytest --collect-only

# テストカバレッジ確認
uv run pytest --cov=src --cov-report=term
```

### テスト問題修復

```bash
# テストキャッシュクリア
uv run pytest --cache-clear

# テスト用一時ファイル削除
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name ".pytest_cache" -type d -exec rm -rf {} +

# 並列テスト無効化（競合状態回避）
uv run pytest -n 0

# 詳細デバッグモード
uv run pytest -vvv --tb=long
```

## Live2D問題

### Live2D診断

```bash
# Live2Dモデルファイル確認
find frontend/public/live2d/models/ -name "*.model3.json"

# Webサーバーからのアクセス確認
curl -f http://localhost:3000/live2d/models/Haru/Haru.model3.json

# ブラウザコンソールエラー確認（手動）
echo "ブラウザの開発者ツールでConsoleタブを確認してください"
```

### Live2D問題修復

```bash
# モデルファイル権限修正
chmod -R 644 frontend/public/live2d/models/

# Webサーバー再起動
cd frontend/
npm run start

# モデルファイル構造確認
tree frontend/public/live2d/models/ | head -20
```

## パフォーマンス問題

### システムリソース確認

```bash
# CPU・メモリ使用量
top -p $(pgrep -d, -f "python|node|ollama|voicevox")

# ディスク使用量
df -h
du -sh .venv/ frontend/node_modules/ || true

# Dockerリソース使用量
docker stats
```

### パフォーマンス最適化

```bash
# Pythonキャッシュクリア
find . -name "__pycache__" -type d -exec rm -rf {} +

# Node.jsキャッシュクリア
npm cache clean --force

# Dockerイメージクリーンアップ
docker image prune -f
docker system prune -f

# ログファイルクリーンアップ
find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null || true
```

## ネットワーク問題

### ポート競合確認

```bash
# 使用ポート確認
lsof -i :3000  # Frontend
lsof -i :5000  # Backend
lsof -i :11434 # Ollama
lsof -i :50021 # VoiceVox

# 競合プロセス終了
pkill -f "port 3000"
pkill -f "flask"
```

### ファイアウォール確認

```bash
# iptables確認（Linux）
sudo iptables -L -n

# UFW状態確認（Ubuntu）
sudo ufw status

# ローカルhost確認
ping localhost
telnet localhost 5000
```

## ログ収集

### 詳細ログ収集

```bash
# 全サービスログ収集
mkdir -p debug_logs/
docker-compose -f docker-compose.dev.yml logs > debug_logs/docker_logs.txt
uv run pytest --log-level=DEBUG > debug_logs/test_logs.txt 2>&1
npm run start > debug_logs/frontend_logs.txt 2>&1 &

# システム情報収集
uname -a > debug_logs/system_info.txt
docker version >> debug_logs/system_info.txt
uv --version >> debug_logs/system_info.txt
node --version >> debug_logs/system_info.txt
```
