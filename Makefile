.PHONY: build up down restart logs clean test dev prod

# デフォルトは開発環境
dev:
	docker-compose -f docker-compose.dev.yml up -d

# 本番環境のビルドと起動
prod:
	docker-compose up -d

# ビルド
build:
	docker-compose build

# 起動
up:
	docker-compose up -d

# 停止
down:
	docker-compose down

# 再起動
restart:
	docker-compose restart

# ログ表示
logs:
	docker-compose logs -f

# クリーンアップ（ボリュームを含む）
clean:
	docker-compose down -v

# テスト実行
test:
	docker-compose run --rm backend poetry run pytest 