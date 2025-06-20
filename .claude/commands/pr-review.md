# PR作成とレビュー依頼

## 概要
GitHub PRを作成してCodeRabbitなどの自動レビューを受け、指摘事項を修正する

## 実行手順
1. 現在のブランチからPRを作成
2. 自動レビュー（CodeRabbit）の実行を待機
3. レビューコメントを取得・分析
4. 指摘事項を修正
5. 品質基準をクリアするまで継続

## 使用方法
```bash
# PRを作成してレビュー
claude "PRを作成してコードレビューを受け、指摘事項があれば修正してください"

# 既存PRのレビュー結果チェック
claude "現在のPRのレビュー結果をチェックして、修正が必要な箇所があれば対応してください"
```

## PR作成コマンド
```bash
# PRを作成
gh pr create \
  --title "feat: implement new feature" \
  --body "Feature implementation with automated review requested" \
  --draft  # ドラフトとして作成、レビュー完了後にready for reviewに変更

# PR確認
gh pr view --json number,title,url

# レビューコメント取得
gh pr view --json reviews,comments
```

## レビュー分析
```bash
# CodeRabbitコメント抽出
gh pr view --json comments | jq -r '.comments[] | select(.user.login == "coderabbitai") | .body'

# 一般的なレビューコメント抽出
gh pr view --json reviews | jq -r '.reviews[].body'
```

## 修正優先度
- **🔴 Critical**: セキュリティ、重要なバグ → 即座に修正
- **🟡 Important**: パフォーマンス、保守性 → 可能な限り修正
- **🟢 Minor**: スタイル、命名 → 時間があれば修正

## 品質基準
- セキュリティスコア: 90点以上
- 保守性スコア: 80点以上
- テストカバレッジ: 85%以上
- 複雑度: Medium以下
