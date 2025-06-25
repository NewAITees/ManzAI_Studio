# CI/CDとCodeRabbit品質確認実装ガイド

## 概要

このドキュメントでは、Claude Code主導でCI/CDパイプラインを自動化し、CodeRabbitによる品質確認を実装するための実装テクニックをまとめています。

## 目次

1. [CI/CD自動化のアーキテクチャ](#cicd自動化のアーキテクチャ)
2. [実装テクニック](#実装テクニック)
3. [CodeRabbit統合戦略](#coderabbit統合戦略)
4. [エラーハンドリングとリトライ機構](#エラーハンドリングとリトライ機構)
5. [品質基準と自動修正パターン](#品質基準と自動修正パターン)
6. [実装のベストプラクティス](#実装のベストプラクティス)

## CI/CD自動化のアーキテクチャ

### 1. 3層構造のアプローチ

```
┌─────────────────────────────────────────┐
│          Claude Code Layer              │  ← 主体的判断・実行
├─────────────────────────────────────────┤
│          Automation Scripts            │  ← 自動修正・リトライ
├─────────────────────────────────────────┤
│        GitHub Actions CI/CD            │  ← 品質チェック・実行
└─────────────────────────────────────────┘
```

### 2. ワークフロー設計原則

**主体性の原則**: Claude Codeが能動的にCI/CDを監視・修正
```bash
# 基本フロー
1. 変更検出 → 2. 自動コミット → 3. CI監視 → 4. エラー分析 → 5. 自動修正 → 6. リトライ
```

**冗長性の原則**: 複数の品質チェックポイント
- Pre-commit hooks (ローカル)
- GitHub Actions (リモート)
- CodeRabbit (レビュー)

## 実装テクニック

### 1. 自動CI/CDチェックスクリプト

#### 核心実装: `auto-ci-check.sh`

```bash
#!/bin/bash
set -e

AUTO_CI_CHECK_MAX_RETRIES=3
AUTO_CI_CHECK_RETRY_COUNT=0

auto_ci_check() {
    echo "🔍 CI/CDチェックを開始します..."

    # 1. 変更の自動コミット・プッシュ
    if [[ $(git status --porcelain) ]]; then
        git add .
        git commit -m "chore: auto CI check (attempt $((AUTO_CI_CHECK_RETRY_COUNT + 1)))"
        git push origin "$(git branch --show-current)"
    fi

    # 2. CI実行監視 (最大5分待機)
    local latest_run_id
    latest_run_id=$(gh run list --limit 1 --json databaseId -q '.[0].databaseId')

    local timeout=300
    local elapsed=0

    while [[ $elapsed -lt $timeout ]]; do
        status=$(gh run view "$latest_run_id" --json status -q '.status')
        if [[ "$status" == "completed" ]]; then
            break
        fi
        sleep 30
        elapsed=$((elapsed + 30))
    done

    # 3. 結果分析と自動修正
    conclusion=$(gh run view "$latest_run_id" --json conclusion -q '.conclusion')
    case "$conclusion" in
        "success")
            echo "✅ CI/CD成功！"
            return 0
            ;;
        "failure")
            fix_ci_errors "$latest_run_id"
            retry_ci_check
            ;;
    esac
}
```

#### キーテクニック

**1. 状態監視パターン**
```bash
# ポーリング vs ウェブフック
while [[ $elapsed -lt $timeout ]]; do
    status=$(gh run view "$run_id" --json status -q '.status')
    [[ "$status" == "completed" ]] && break
    sleep 30
done
```

**2. エラーパターン認識**
```bash
# ログ解析による自動判断
if echo "$error_log" | grep -q "mypy"; then
    echo "🔍 型チェックエラー検出"
    uv run mypy src/ --show-error-codes
elif echo "$error_log" | grep -q "pytest.*failed"; then
    echo "🧪 テストエラー検出"
    uv run pytest --tb=short -v
fi
```

### 2. GitHub CLI統合テクニック

#### 認証とアクセス制御
```bash
# 認証確認
if ! gh auth status >/dev/null 2>&1; then
    echo "❌ GitHub CLIの認証が必要です"
    exit 1
fi

# スコープ確認
gh auth status | grep "Token scopes" | grep -q "repo"
```

#### CI実行データ取得
```bash
# 最新実行の詳細取得
latest_run_id=$(gh run list --limit 1 --json databaseId -q '.[0].databaseId')
error_log=$(gh run view "$run_id" --log-failed)

# JSONパースによる構造化データ取得
gh run view "$run_id" --json conclusion,status,createdAt
```

### 3. 自動修正エンジンの実装

#### パターンベース修正
```bash
fix_ci_errors() {
    local run_id="$1"
    local error_log
    error_log=$(gh run view "$run_id" --log-failed)

    # 1. Linting自動修正
    echo "📝 コードフォーマット修正..."
    uv run ruff format .
    uv run ruff check --fix .

    # 2. 型エラー検出時の対応
    if echo "$error_log" | grep -q "mypy"; then
        echo "🔍 型チェックエラー検出、基本的な修正を試行..."
        # 基本的な型ヒント追加、import修正など
    fi

    # 3. テストエラー対応
    if echo "$error_log" | grep -q "pytest"; then
        echo "🧪 テストエラー検出、テスト実行してチェック..."
        uv run pytest --tb=short -v
    fi
}
```

## CodeRabbit統合戦略

### 1. PR駆動のレビューワークフロー

#### 自動PR作成
```bash
# ドラフトPRとして作成 → レビュー完了後にready for review
gh pr create \
  --title "feat: implement feature" \
  --body "Feature implementation with automated review requested" \
  --draft

# レビューコメント分析
gh pr view --json comments | jq -r '.comments[] | select(.user.login == "coderabbitai") | .body'
```

#### レビュー結果の構造化取得
```bash
# CodeRabbitコメント抽出
get_coderabbit_comments() {
    local pr_number="$1"
    gh pr view "$pr_number" --json comments | \
    jq -r '.comments[] | select(.user.login == "coderabbitai") | {
        body: .body,
        created_at: .createdAt,
        position: .position
    }'
}
```

### 2. 品質スコア分析

#### 重要度分類システム
```bash
analyze_review_priority() {
    local comment="$1"

    # 🔴 Critical: セキュリティ、重要なバグ
    if echo "$comment" | grep -iE "(security|vulnerability|sql injection|xss)"; then
        echo "critical"
    # 🟡 Important: パフォーマンス、保守性
    elif echo "$comment" | grep -iE "(performance|maintainability|complexity)"; then
        echo "important"
    # 🟢 Minor: スタイル、命名
    else
        echo "minor"
    fi
}
```

### 3. 自動修正統合

#### CodeRabbit指摘の自動修正
```bash
apply_coderabbit_fixes() {
    local pr_number="$1"
    local comments
    comments=$(get_coderabbit_comments "$pr_number")

    # 各コメントを分析して修正適用
    echo "$comments" | while read -r comment; do
        priority=$(analyze_review_priority "$comment")
        case "$priority" in
            "critical")
                echo "🔴 Critical修正を適用中..."
                # セキュリティ修正の自動適用
                ;;
            "important")
                echo "🟡 Important修正を適用中..."
                # パフォーマンス改善の自動適用
                ;;
        esac
    done
}
```

## エラーハンドリングとリトライ機構

### 1. 指数バックオフ実装

```bash
retry_with_backoff() {
    local max_attempts="$1"
    local delay="$2"
    local command="${@:3}"

    for ((i=1; i<=max_attempts; i++)); do
        if $command; then
            return 0
        fi

        if [[ $i -lt $max_attempts ]]; then
            echo "リトライ $i/$max_attempts 失敗、${delay}秒後に再試行..."
            sleep $delay
            delay=$((delay * 2))  # 指数バックオフ
        fi
    done

    return 1
}
```

### 2. 障害分離とフォールバック

```bash
safe_ci_operation() {
    local operation="$1"

    # タイムアウト設定
    timeout 300 "$operation" || {
        echo "⚠️ 操作がタイムアウトしました"
        # フォールバック処理
        fallback_ci_check
    }
}
```

## 品質基準と自動修正パターン

### 1. 品質ゲート定義

```yaml
# pyproject.toml
[tool.coverage.run]
branch = true
source = ["src"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError"
]
fail_under = 85  # 最低カバレッジ85%

[tool.mypy]
python_version = "3.12"
disallow_untyped_defs = true
strict_optional = true
warn_redundant_casts = true
```

### 2. 自動修正パターンライブラリ

#### Lint修正パターン
```bash
apply_lint_fixes() {
    # 1. インポート整理
    uv run ruff check --select I --fix .

    # 2. 未使用変数削除
    uv run ruff check --select F401,F841 --fix .

    # 3. フォーマット適用
    uv run ruff format .
}
```

#### 型エラー修正パターン
```bash
apply_type_fixes() {
    # 1. 基本的な型ヒント追加
    # 関数の戻り値型が不明な場合
    sed -i 's/def \([^(]*\)(\([^)]*\)):/def \1(\2) -> None:/g' src/**/*.py

    # 2. インポート追加
    # Listが使われているがインポートされていない場合
    grep -l "List\[" src/**/*.py | xargs sed -i '1i\from typing import List'
}
```

### 3. テスト品質向上パターン

#### モック除去パターン
```python
# Before: モックベース
@patch('requests.get')
def test_api_call(mock_get):
    mock_get.return_value.json.return_value = {"status": "ok"}
    result = api_service.get_status()
    assert result["status"] == "ok"

# After: 実装ベース
def test_api_call_real():
    # 実際のサービスが利用できない場合はskip
    if not check_service_availability("http://localhost:8080"):
        pytest.skip("Service not available")

    result = api_service.get_status()
    assert result["status"] == "ok"
```

## 実装のベストプラクティス

### 1. セキュリティ考慮事項

#### トークン管理
```bash
# 環境変数での管理
export GITHUB_TOKEN="$(gh auth token)"

# スコープ制限
gh auth refresh --scopes "repo,read:org"
```

#### ログサニタイズ
```bash
sanitize_logs() {
    local log_content="$1"
    # 機密情報のマスキング
    echo "$log_content" | sed 's/\(token[[:space:]]*:[[:space:]]*\)[^[:space:]]*/\1***MASKED***/gi'
}
```

### 2. パフォーマンス最適化

#### 並列実行
```bash
# 複数チェックの並列実行
run_quality_checks() {
    {
        uv run ruff check . &
        uv run mypy src/ &
        uv run pytest --quiet &
        wait
    } | tee quality_check_results.log
}
```

#### キャッシュ活用
```bash
# GitHub Actions結果のキャッシュ
cache_ci_results() {
    local run_id="$1"
    local cache_file=".ci_cache/${run_id}.json"

    mkdir -p .ci_cache
    gh run view "$run_id" --json conclusion,status > "$cache_file"
}
```

### 3. 監視と可観測性

#### メトリクス収集
```bash
collect_metrics() {
    local start_time=$(date +%s)

    # 処理実行
    execute_ci_pipeline

    local end_time=$(date +%s)
    local duration=$((end_time - start_time))

    echo "CI処理時間: ${duration}秒" | tee -a metrics.log
}
```

#### アラート設定
```bash
check_failure_threshold() {
    local failure_count
    failure_count=$(grep -c "❌ CI/CD失敗" ci_execution.log)

    if [[ $failure_count -gt 3 ]]; then
        echo "⚠️ 失敗回数が閾値を超えました: $failure_count"
        # アラート送信処理
    fi
}
```

## 今後の拡張可能性

### 1. AI統合の展望

- **GPT-4によるコードレビュー**: より詳細な品質分析
- **自動リファクタリング**: 構造的問題の自動修正
- **予測的品質管理**: 問題発生前の予防的修正

### 2. 多言語対応

```bash
# 言語別品質チェック拡張
case "$language" in
    "python")
        uv run ruff check . && uv run mypy src/
        ;;
    "typescript")
        npm run lint && npm run type-check
        ;;
    "rust")
        cargo clippy && cargo test
        ;;
esac
```

### 3. チーム連携機能

- **Slack通知統合**: 品質レポートの自動配信
- **JIRA連携**: 品質問題のチケット自動作成
- **ダッシュボード**: リアルタイム品質監視

## まとめ

Claude Code主導のCI/CD自動化とCodeRabbit品質確認の実装では、以下の要素が重要です：

1. **主体的な監視と修正**: 受動的ではなく能動的なパイプライン管理
2. **パターンベースの自動修正**: 一般的な問題に対する定型的な解決策
3. **段階的品質ゲート**: 複数レイヤーでの品質保証
4. **適応的リトライ機構**: 失敗に対する柔軟な対応
5. **観測可能性**: 問題の早期発見と分析

これらのテクニックを組み合わせることで、開発者の負担を最小化しながら高品質なコードベースを維持することが可能になります。
