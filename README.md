# ManzAI Studio

ローカルで動作する漫才生成・実演Webアプリケーション

## 概要

ManzAI Studioは、OllamaのLLMを使用して漫才の台本を生成し、Live2Dキャラクターとボイスボックスを使用してアニメーションと音声で実演する、完全ローカルで動作するWebアプリケーションです。

## 必要要件

### システム要件
- pyenv
- Poetry
- Node.js 18.0.0以上
- 2GB以上の空き容量（モデルファイル用）

### 必須コンポーネント
- [Ollama](https://ollama.ai/) - LLM実行環境
- [VoiceVox](https://voicevox.hiroshiba.jp/) - 音声合成エンジン
- Live2D Cubism SDK for Web

## セットアップ手順

### 1. 必須コンポーネントのインストール

#### pyenv と Poetry のインストール
```bash
# macOSの場合
brew install pyenv
brew install poetry

# pyenvでPythonをインストール
pyenv install 3.10.13
pyenv local 3.10.13  # プロジェクトのPythonバージョンを設定
```

#### Ollamaのインストール
```bash
# macOSの場合
curl -fsSL https://ollama.ai/install.sh | sh

# 必要なモデルのダウンロード
ollama pull phi
```

#### VoiceVoxのインストール
1. [VoiceVox公式サイト](https://voicevox.hiroshiba.jp/)からダウンロード
2. インストーラーの指示に従ってインストール

### 2. プロジェクトのセットアップ

```bash
# 1. Poetry環境のセットアップ
poetry install

# 2. フロントエンド依存関係のインストール
cd frontend
npm install
```

### 3. 開発サーバーの起動

```bash
# バックエンドサーバーの起動
poetry run python run.py

# 別のターミナルでフロントエンドの開発サーバーを起動
cd frontend
npm run dev
```

## プロジェクト構造

```
manzai_studio/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   ├── models/
│   │   └── services/
│   ├── tests/
│   └── config.py
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
├── models/
│   ├── live2d/
│   └── ollama/
├── pyproject.toml
├── poetry.lock
└── README.md
```

## 開発ガイドライン

- コードスタイル: black, flake8, mypyによる自動フォーマットと型チェック
- コミットメッセージ: Conventional Commitsに従う
- ブランチ戦略: GitHub Flow

### コード品質管理

```bash
# コードフォーマット
poetry run black .

# 型チェック
poetry run mypy .

# テスト実行
poetry run pytest
```

## ライセンス

MIT License

## 貢献について

プルリクエストは大歓迎です。大きな変更を加える場合は、まずissueを作成して変更内容を議論してください。

## 使い方

### Poetryによる開発環境でのセットアップと実行

1. 依存関係をインストールする:
   ```bash
   poetry install
   ```

2. アプリケーションを起動する:
   ```bash
   poetry run start
   ```

3. テストを実行する:
   ```bash
   poetry run test
   ```

4. カバレッジレポート付きでテストを実行する:
   ```bash
   poetry run coverage
   ```

5. リンターを実行する:
   ```bash
   poetry run lint
   ```

6. コードをフォーマットする:
   ```bash
   poetry run format
   ```

7. 型チェックを実行する:
   ```bash
   poetry run type-check
   ```

### Dockerによる実行

1. Docker Composeでサービスを起動する:
   ```bash
   docker-compose up -d
   ```

2. サービスの状態を確認する:
   ```bash
   docker-compose ps
   ```

3. サービスを停止する:
   ```bash
   docker-compose down
   ``` 