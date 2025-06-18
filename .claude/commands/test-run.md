# テスト実行コマンド

ManzAI Studioのテスト実行に関するコマンド集です。

## バックエンドテスト

### 全テスト実行

```bash
# 基本的なテスト実行
uv run pytest

# カバレッジ付きテスト
uv run pytest --cov=src --cov-report=term-missing

# 詳細出力付きテスト
uv run pytest -v

# 並列実行（高速化）
uv run pytest -n auto
```

### 特定テストの実行

```bash
# 特定ファイルのテスト
uv run pytest tests/test_api.py

# 特定テスト関数の実行
uv run pytest tests/test_services.py::test_generate_manzai_script

# パターンマッチでテスト選択
uv run pytest -k "test_ollama"

# マーカー指定でテスト実行
uv run pytest -m "not integration"
```

### テストカテゴリ別実行

```bash
# 単体テストのみ
python tests/run_tests.py --unit

# 統合テストのみ
python tests/run_tests.py --integration

# サービステストのみ
python tests/run_tests.py --services

# APIテストのみ
python tests/run_tests.py --api
```

## フロントエンドテスト

### 基本実行

```bash
cd frontend/

# 全テスト実行
npm test -- --watchAll=false

# カバレッジ付きテスト
npm run test:coverage

# ウォッチモード
npm run test:watch
```

### 特定テストの実行

```bash
# 特定ファイルのテスト
npm test -- --testPathPattern=AudioPlayer.test.js

# 特定テスト名の実行
npm test -- --testNamePattern="should play audio"

# 更新されたファイルのみテスト
npm test -- --onlyChanged
```

## コード品質チェック

### リンティング・フォーマット

```bash
# Ruffによるリンティング
uv run ruff check .

# Ruffによる自動修正
uv run ruff check --fix .

# Ruffフォーマットチェック
uv run ruff format --check .

# Ruffフォーマット適用
uv run ruff format .
```

### 型チェック

```bash
# MyPyによる型チェック
uv run mypy src/

# 設定ファイル指定
uv run mypy --config-file mypy.ini src/

# 特定ファイルの型チェック
uv run mypy src/backend/app/services/ollama_service.py
```

### セキュリティチェック

```bash
# Safetyによる脆弱性チェック
uv run safety check

# Banditによるセキュリティスキャン
uv run bandit -r src/

# 設定ファイル指定
uv run bandit -c pyproject.toml -r src/
```

## 統合テスト

### Docker環境でのテスト

```bash
# Docker環境でバックエンドテスト実行
make test

# 開発環境起動後のテスト
make dev
sleep 30  # サービス起動待ち
uv run pytest tests/test_integration.py
```

### 手動統合テスト

```bash
# サービス起動確認
curl http://localhost:5000/api/health
curl http://localhost:11434/api/tags
curl http://localhost:50021/version

# フルワークフローテスト
python scripts/test_full_manzai.py
```

## テストデバッグ

### 詳細ログ付きテスト

```bash
# ログレベル指定
uv run pytest --log-level=DEBUG

# 標準出力キャプチャ無効
uv run pytest -s

# デバッガ起動
uv run pytest --pdb

# 失敗時のみデバッガ
uv run pytest --pdb-failures
```

### テスト環境設定

```bash
# テスト用環境変数
export FLASK_ENV=testing
export VOICEVOX_URL=http://localhost:50021
export OLLAMA_URL=http://localhost:11434

# モックモード有効
export USE_MOCK_SERVICES=true
```

## CI/CDテスト

### GitHub Actions相当のテスト

```bash
# CI環境と同じコマンド実行
uv run ruff format --check .
uv run ruff check .
uv run mypy src/
uv run pytest --cov=src --cov-report=xml
uv run safety check --ignore 70612
uv run bandit -r src/
```

### フロントエンドCIテスト

```bash
cd frontend/
npm ci
npm test -- --coverage --watchAll=false
npm run build
```
