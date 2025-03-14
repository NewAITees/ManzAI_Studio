# ManzAI Studio 開発工程書

## 開発ステップ1: 環境セットアップと基本的なプロジェクト構造の確立

### 必要なコンポーネントのインストール

1. **Python環境のセットアップ**
   - pyenvを使ってPython 3.10.13をインストールします
   ```bash
   brew install pyenv  # macOSの場合
   pyenv install 3.10.13
   pyenv local 3.10.13  # プロジェクトディレクトリでこのバージョンを使用
   ```

2. **Poetryのインストールと設定**
   ```bash
   brew install poetry  # macOSの場合
   poetry config virtualenvs.in-project true  # プロジェクト内に仮想環境を作成
   ```

3. **必須外部コンポーネントのインストール**
   - Ollama: テキスト生成エンジン
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull phi  # 漫才生成に使用する推奨モデル
   ```
   
   - VoiceVox: 音声合成エンジン
   ```bash
   # VoiceVox公式サイトからダウンロードしてインストール
   # https://voicevox.hiroshiba.jp/
   ```

4. **プロジェクト依存関係のインストール**
   ```bash
   # プロジェクトルートディレクトリで
   poetry install
   ```

### Docker環境のセットアップ（代替方法）

1. **Dockerのインストール**
   - Docker Desktopをインストール（[Docker公式サイト](https://www.docker.com/products/docker-desktop)）

2. **Docker Composeでの環境起動**
   ```bash
   docker-compose up -d
   ```
   これにより、以下のサービスが起動します:
   - VoiceVox: ポート50021でアクセス可能
   - Ollama: ポート11434でアクセス可能
   - Webアプリケーション: ポート5000でアクセス可能

### バックエンド構造の確認

1. **ディレクトリ構造**
   ```
   src/
   ├── backend/
   │   ├── app/
   │   │   ├── __init__.py  # Flaskアプリのファクトリ関数
   │   │   ├── config.py    # アプリケーション設定
   │   │   └── routes/      # APIエンドポイント
   │   │       └── api.py   # APIルート定義
   │   └── tests/           # テストディレクトリ
   ```

2. **アプリケーション設定の確認**
   - 環境変数の設定
   ```bash
   # .envファイルを作成（gitignoreされています）
   echo "FLASK_APP=backend/app/__init__.py" > .env
   echo "FLASK_ENV=development" >> .env
   echo "VOICEVOX_URL=http://localhost:50021" >> .env
   echo "OLLAMA_URL=http://localhost:11434" >> .env
   echo "OLLAMA_MODEL=phi" >> .env
   ```

### フロントエンド環境の準備

1. **フロントエンドディレクトリの作成**
   ```bash
   mkdir -p frontend/src frontend/public
   ```

2. **フロントエンドの初期ファイル作成**
   
   この部分はステップ5で詳細に実装していきますが、ここでは基本的なファイル構造だけを作成しておきます。

### 開発サーバーの起動テスト

1. **バックエンドサーバーの起動**
   ```bash
   # プロジェクトルートディレクトリで
   poetry run python -m flask --app backend/app/__init__.py run --debug
   ```

2. **健全性チェックAPIの確認**
   ```bash
   curl http://localhost:5000/api/health
   # 期待される応答: {"status":"healthy"}
   ```

この最初のステップでは、開発環境のセットアップと基本的なプロジェクト構造の確立に焦点を当てています。これにより、後続のステップでの実装作業がスムーズに進行するための土台が整います。

次のステップでは、Ollamaを使用して漫才の台本を生成する機能の実装に進みます。