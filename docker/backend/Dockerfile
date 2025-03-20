FROM python:3.10-slim

WORKDIR /app

# セキュリティアップデートとビルドに必要なツールのインストール
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Poetryのインストール
RUN curl -sSL https://install.python-poetry.org | python3 -

# PATHの設定
ENV PATH="/root/.local/bin:$PATH"

# キャッシュ最適化のためにプロジェクトファイルをコピー
COPY pyproject.toml poetry.lock* ./

# 仮想環境なしで依存関係をインストール
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# アプリケーションコードをコピー
COPY . .

# 必要なディレクトリを作成
RUN mkdir -p data/audio

# 環境変数の設定
ENV FLASK_APP=src.app:create_app
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# コンテナ起動コマンド
CMD ["poetry", "run", "gunicorn", "src.app:app", "--bind", "0.0.0.0:5000", "--workers", "4"]

# ヘルスチェックの追加
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1 