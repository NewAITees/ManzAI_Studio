# ManzAI Studio インストールガイド

このガイドでは、ManzAI Studioのインストール方法を詳しく説明します。

## 目次

1. [必要要件](#必要要件)
2. [基本インストール](#基本インストール)
3. [開発環境のセットアップ](#開発環境のセットアップ)
4. [本番環境のセットアップ](#本番環境のセットアップ)
5. [手動インストール](#手動インストール)
6. [トラブルシューティング](#トラブルシューティング)

## 必要要件

ManzAI Studioを実行するには以下の環境が必要です：

### システム要件

- **オペレーティングシステム**: Windows 10/11、macOS 10.15以上、Ubuntu 20.04以上
- **RAM**: 最小8GB（16GB以上推奨）
- **CPU**: 4コア以上（8コア以上推奨）
- **ディスク容量**: 10GB以上の空き容量
- **ネットワーク**: インターネット接続（初回セットアップ時）

### ソフトウェア要件

- **Docker**: バージョン20.10.0以上
- **Docker Compose**: バージョン2.0.0以上
- **Webブラウザ**: Chrome 90+、Firefox 88+、Edge 90+（WebGL対応）

## 基本インストール

### 1. Dockerのインストール

お使いのOSに合わせて、Dockerをインストールしてください。

#### Windows

1. [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)をダウンロードしてインストール
2. WSL2の設定が推奨されます（インストーラーの指示に従ってください）
3. Docker Desktopを起動し、チュートリアルに従ってセットアップを完了

#### macOS

1. [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)をダウンロードしてインストール
2. Docker Desktopを起動し、チュートリアルに従ってセットアップを完了

#### Linux (Ubuntu)

```bash
# 必要なパッケージのインストール
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# Dockerの公式GPGキーを追加
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Dockerのリポジトリを追加
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Dockerのインストール
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# ユーザーをdockerグループに追加（sudo不要でDockerを実行可能に）
sudo usermod -aG docker $USER
newgrp docker
```

### 2. ManzAI Studioのダウンロード

```bash
# GitHubリポジトリをクローン
git clone https://github.com/your-username/manzai-studio.git
cd manzai-studio
```

## 開発環境のセットアップ

開発環境では、コードの変更がリアルタイムで反映され、デバッグモードが有効になります。

```bash
# 開発環境用のdocker-compose.dev.ymlを使用して起動
docker-compose -f docker-compose.dev.yml up -d
```

これにより以下のサービスが起動します：
- Webサーバー: http://localhost:5000/
- フロントエンド開発サーバー: http://localhost:3000/
- VoiceVoxエンジン: http://localhost:50021/
- Ollamaサービス: http://localhost:11434/

### 開発モードの特徴

- ホットリロード機能（コード変更時に自動再読み込み）
- デバッグログの詳細表示
- モックデータによるバックエンドサービス障害時のフォールバック機能

## 本番環境のセットアップ

本番環境では、パフォーマンスが最適化され、デバッグ機能が無効化されます。

```bash
# 環境変数ファイルの作成（オプション）
cp .env.example .env.production
# 必要に応じて.env.productionを編集

# docker-compose.ymlを使用して起動
docker-compose up -d
```

アプリケーションは http://localhost:5000/ でアクセスできます。

### 本番環境のカスタマイズ

`.env.production`ファイルで以下の設定をカスタマイズできます：

```
# 言語モデル設定
OLLAMA_MODEL=llama2
# その他の設定
```

## 手動インストール

Docker Composeを使用せずに手動でインストールする場合は、以下の手順に従ってください。

### 1. Python環境のセットアップ

```bash
# Python 3.10のインストール（OSにより方法が異なります）
# Poetryのインストール
curl -sSL https://install.python-poetry.org | python3 -

# プロジェクトディレクトリに移動
cd manzai-studio

# 依存関係のインストール
poetry install
```

### 2. 外部サービスのセットアップ

#### VoiceVoxのインストール

公式サイトの指示に従ってインストールしてください：
[VoiceVox Engine](https://github.com/VOICEVOX/voicevox_engine)

#### Ollamaのインストール

公式サイトの指示に従ってインストールしてください：
[Ollama](https://github.com/ollama/ollama)

モデルのダウンロード：
```bash
ollama pull llama2
```

### 3. アプリケーションの起動

```bash
# 環境変数の設定
export VOICEVOX_URL=http://localhost:50021
export OLLAMA_URL=http://localhost:11434
export OLLAMA_MODEL=llama2

# アプリケーションの起動
poetry run python -m src.app
```

## トラブルシューティング

### Docker関連の問題

**Q: `docker-compose` コマンドが見つからない**

A: Docker Composeが正しくインストールされているか確認してください。最新のDocker Desktopでは `docker compose` （スペース区切り）の形式も使用できます。

**Q: ポートの競合エラーが表示される**

A: 既に使用されているポートがある場合は、`docker-compose.yml` または `docker-compose.dev.yml` ファイルを編集して、別のポートを指定してください。

### サービス接続の問題

**Q: "Ollama service is not available" というエラーが表示される**

A: Ollamaサービスが正常に起動しているか確認してください。ログを確認するには：
```bash
docker-compose logs ollama
```

**Q: "VoiceVox service is not available" というエラーが表示される**

A: VoiceVoxサービスが正常に起動しているか確認してください。ログを確認するには：
```bash
docker-compose logs voicevox
```

### その他の問題

詳細なトラブルシューティングについては、[GitHub Issuesページ](https://github.com/your-username/manzai-studio/issues)を参照するか、新しい問題を報告してください。 