# CI/CDエラーチェックと自動修正

## 概要
Claude Codeが主体的にCI/CDをチェックし、エラーがあれば自動修正するコマンド

## 実行手順
1. 現在の変更をコミット・プッシュ
2. GitHub Actionsの実行状況をチェック
3. エラーがあれば詳細を取得・分析
4. 自動修正を実施
5. 成功するまで最大3回リトライ

## 使用方法
```bash
# 基本実行
claude "CI/CDチェックして、エラーがあれば修正してください"

# 詳細指定
claude "今の実装でlintエラーやテストエラーがないかCI/CDで確認して、問題があれば修正してください"
```

## 修正パターン
- **Lintエラー**: `uv run ruff format . && uv run ruff check --fix .`
- **型エラー**: 型ヒント追加、import修正
- **テストエラー**: テストコード修正、アサーション調整
- **依存関係エラー**: requirements更新
- **セキュリティエラー**: 脆弱性修正

## 実行例
```bash
# 1. 変更をコミット・プッシュ
git add . && git commit -m "feat: implement feature" && git push

# 2. CI状況確認
gh run list --limit 1

# 3. 失敗時のエラー取得
LATEST_RUN=$(gh run list --limit 1 --json databaseId -q '.[0].databaseId')
gh run view $LATEST_RUN --log-failed

# 4. エラーに応じた修正実行
# (Claude Codeが自動で判断・実行)
```

## 成功基準
- ✅ 全てのGitHub Actionsワークフローが成功
- ✅ Linting、型チェック、テストが全てパス
- ✅ セキュリティチェックが通過
