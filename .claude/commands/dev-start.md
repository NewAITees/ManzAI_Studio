# 開発環境起動コマンド

ManzAI Studioの開発環境を起動するためのコマンド集です。

## Docker開発環境（推奨）

```bash
# 開発環境の起動（ホットリロード対応）
make dev

# サービスの状況確認
docker-compose -f docker-compose.dev.yml ps

# バックエンドログの確認
make backend-logs

# 全サービスのログ確認
make logs
```

## 手動開発環境

### バックエンド

```bash
# Python仮想環境の確認
uv run python --version

# 依存関係の同期
uv sync

# 開発サーバーの起動
uv run python -m src.backend.app

# テスト実行
uv run pytest

# 型チェック
uv run mypy src/
```

### フロントエンド

```bash
# フロントエンドディレクトリへ移動
cd frontend/

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run start

# テスト実行
npm test

# ビルド
npm run build
```

## 外部サービス

### Ollama（LLM）

```bash
# Ollamaサービス起動（Docker環境では自動）
ollama serve

# モデルの確認
curl http://localhost:11434/api/tags

# 推奨モデルのプル
ollama pull gemma3:4b
```

### VoiceVox（TTS）

```bash
# VoiceVoxサービス確認
curl http://localhost:50021/docs

# スピーカー一覧の確認
curl http://localhost:50021/speakers
```

## 開発用URL

- フロントエンド: http://localhost:3000
- バックエンドAPI: http://localhost:5000
- Ollama API: http://localhost:11434
- VoiceVox API: http://localhost:50021
