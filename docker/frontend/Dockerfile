FROM node:18-alpine AS build

WORKDIR /app

# 依存関係のインストール
COPY package.json package-lock.json* ./
RUN npm ci

# ソースコードをコピー
COPY . .

# ビルド実行
RUN npm run build

# 実行環境用の軽量イメージ
FROM nginx:alpine

# ビルドされたファイルをコピー
COPY --from=build /app/build /usr/share/nginx/html

# Nginx設定
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

# ヘルスチェックの追加
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
