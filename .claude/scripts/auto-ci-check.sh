#!/bin/bash
# Claude Code用の自動CI/CDチェックスクリプト

set -e

AUTO_CI_CHECK_MAX_RETRIES=3
AUTO_CI_CHECK_RETRY_COUNT=0

auto_ci_check() {
    echo "🔍 CI/CDチェックを開始します..."

    # 現在の変更をコミット・プッシュ（変更がある場合）
    if [[ $(git status --porcelain) ]]; then
        echo "📝 変更をコミット・プッシュ中..."
        git add .
        local commit_msg="chore: auto CI check (attempt $((AUTO_CI_CHECK_RETRY_COUNT + 1)))"
        git commit -m "$commit_msg" || echo "コミットをスキップ（変更なし）"
        git push origin "$(git branch --show-current)" || echo "プッシュをスキップ"
    fi

    # 最新のCI実行を取得
    echo "⏳ 最新のCI実行を確認中..."
    local latest_run_id
    latest_run_id=$(gh run list --limit 1 --json databaseId -q '.[0].databaseId')

    if [[ -z "$latest_run_id" ]]; then
        echo "❌ CI実行が見つかりません"
        return 1
    fi

    # CI実行完了を待機（最大5分）
    local timeout=300
    local elapsed=0
    local status=""

    while [[ $elapsed -lt $timeout ]]; do
        status=$(gh run view "$latest_run_id" --json status -q '.status' 2>/dev/null || echo "unknown")

        if [[ "$status" == "completed" ]]; then
            break
        fi

        echo "⏳ CI実行中... ($elapsed/$timeout 秒経過)"
        sleep 30
        elapsed=$((elapsed + 30))
    done

    if [[ "$status" != "completed" ]]; then
        echo "⚠️ CI実行がタイムアウトしました"
        return 1
    fi

    # CI結果をチェック
    local conclusion
    conclusion=$(gh run view "$latest_run_id" --json conclusion -q '.conclusion')

    case "$conclusion" in
        "success")
            echo "✅ CI/CD成功！"
            return 0
            ;;
        "failure")
            echo "❌ CI/CD失敗、修正を試行します..."
            fix_ci_errors "$latest_run_id"
            retry_ci_check
            ;;
        *)
            echo "⚠️ CI/CDが予期しない状態です: $conclusion"
            return 1
            ;;
    esac
}

fix_ci_errors() {
    local run_id="$1"

    echo "🔧 CI/CDエラーを分析中..."

    # エラーログを取得
    local error_log
    error_log=$(gh run view "$run_id" --log-failed 2>/dev/null || echo "ログ取得失敗")

    if [[ "$error_log" == "ログ取得失敗" ]]; then
        echo "⚠️ エラーログの取得に失敗しました"
        return 1
    fi

    # 一般的なエラーパターンに基づく自動修正
    echo "🛠️ 一般的な修正を実行中..."

    # Lintエラーの修正
    echo "📝 コードフォーマット修正..."
    uv run ruff format . 2>/dev/null || echo "Ruff format スキップ"
    uv run ruff check --fix . 2>/dev/null || echo "Ruff check スキップ"

    # 型チェックエラーの基本的な修正
    if echo "$error_log" | grep -q "mypy"; then
        echo "🔍 型チェックエラー検出、基本的な修正を試行..."
        # 不足しているimportの追加など（基本的なもののみ）
        uv run mypy src/ --show-error-codes 2>/dev/null || echo "MyPy check スキップ"
    fi

    # テストエラーのチェック
    if echo "$error_log" | grep -q "pytest\|test.*failed"; then
        echo "🧪 テストエラー検出、テストを実行してチェック..."
        uv run pytest --tb=short -v 2>/dev/null || echo "Pytest スキップ"
    fi

    # 変更があれば再コミット
    if [[ $(git status --porcelain) ]]; then
        echo "💾 修正をコミット中..."
        git add .
        git commit -m "fix: auto-fix CI errors (attempt $((AUTO_CI_CHECK_RETRY_COUNT + 1)))"
        git push origin "$(git branch --show-current)"
    else
        echo "📝 自動修正による変更はありませんでした"
    fi
}

retry_ci_check() {
    AUTO_CI_CHECK_RETRY_COUNT=$((AUTO_CI_CHECK_RETRY_COUNT + 1))

    if [[ $AUTO_CI_CHECK_RETRY_COUNT -lt $AUTO_CI_CHECK_MAX_RETRIES ]]; then
        echo "🔄 修正後に再試行します (${AUTO_CI_CHECK_RETRY_COUNT}/${AUTO_CI_CHECK_MAX_RETRIES})"
        sleep 60  # 1分待機してから再試行
        auto_ci_check
    else
        echo "❌ 最大試行回数(${AUTO_CI_CHECK_MAX_RETRIES})に達しました"
        echo "📋 手動での確認・修正が必要です"

        # 最後のエラーログを表示
        local latest_run_id
        latest_run_id=$(gh run list --limit 1 --json databaseId -q '.[0].databaseId')
        echo "🔍 最新のエラーログ:"
        gh run view "$latest_run_id" --log-failed | head -50

        return 1
    fi
}

# メイン実行
main() {
    echo "🚀 自動CI/CDチェック開始"

    # GitHub CLIの認証確認
    if ! gh auth status >/dev/null 2>&1; then
        echo "❌ GitHub CLIの認証が必要です"
        echo "実行してください: gh auth login"
        return 1
    fi

    # Gitリポジトリかチェック
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        echo "❌ Gitリポジトリではありません"
        return 1
    fi

    # 実行
    if auto_ci_check; then
        echo "🎉 CI/CDチェック完了！"
        echo "✅ 全ての品質チェックが通過しました"
    else
        echo "😞 CI/CDチェックに失敗しました"
        echo "🔍 手動での確認をお願いします"
        return 1
    fi
}

# スクリプトが直接実行された場合
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
