.PHONY: build up down restart logs clean test dev prod devcontainer

# デフォルトは開発環境 (devcontainer推奨)
dev:
	@echo "⚠️  Legacy dev command. Please use devcontainer instead:"
	@echo "   code .  # Open in VS Code with devcontainer"
	@echo "   OR"
	@echo "   docker compose up -d  # Use new compose.yml"
	@echo ""
	@echo "Falling back to new compose.yml..."
	docker compose up -d

# Dev Container development (推奨)
devcontainer:
	@echo "🚀 Starting devcontainer development environment..."
	@echo "Please use one of the following methods:"
	@echo ""
	@echo "1. VS Code Dev Container (推奨):"
	@echo "   code .  # VS Code will detect devcontainer"
	@echo ""
	@echo "2. Docker Compose:"
	@echo "   docker compose up -d && docker compose exec dev bash"
	@echo ""
	@echo "3. Standalone script:"
	@echo "   ./run-with-cli.sh"

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

# Dockerイメージを完全に再ビルド (devcontainer対応)
rebuild:
	@echo "🔄 Rebuilding development environment..."
	@echo "Using new compose.yml instead of legacy docker-compose.dev.yml"
	docker compose down
	docker compose build --no-cache
	docker compose up -d

# バックエンドログの表示
backend-logs:
	docker-compose logs -f backend
