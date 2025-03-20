# テスト失敗時のデバッグ手順書

## 概要

この手順書は、Pytestのテスト失敗が発生した際に、体系的なアプローチでデバッグを行い、問題を解決するためのガイドラインです。

## 詳細手順

### 1. テストの実行と問題の特定

```bash
# テストを実行してログを取得
poetry run pytest -v > test_failures.log

# 特定のエラータイプを抽出
grep "ImportError" test_failures.log
grep "AttributeError" test_failures.log
```

- ログを詳細に確認し、どのようなエラーが発生しているかを特定します
- ImportErrorやModuleNotFoundErrorなどの基盤的な問題を優先的に特定します
- 同じ原因で失敗している複数のテストをグループ化します

### 2. 新しいGitブランチの作成

```bash
# 新しいブランチを作成
git checkout -b test-debug-<バグ名>-<日付>

# 例: ImportErrorの場合
git checkout -b test-debug-import-error-20250320
```

- 問題ごとに専用のブランチを作成することで、変更を分離します
- 日付を含めることで、いつ対応したかを明確にします

### 3. 問題の分析と原因の推測

```python
# 考えられる原因をコメントにまとめる
"""
考えられる原因:
1. モジュールが存在しない
2. 循環インポートが発生している
3. パスが正しくない
4. 名前空間の問題
"""
```

- エラーメッセージから考えられる原因を複数リストアップします
- 最も可能性の高い原因から順番に検証していきます

### 4. デバッグ用のログ追加

```python
# Pytestのログレベル調整
pytest --log-cli-level=DEBUG

# コードにログを追加
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("関数が呼び出されました")
    # ...
    logger.debug(f"結果: {result}")
    return result
```

- 問題が発生している箇所の前後にログを追加して状態を可視化します
- 変数の値やプログラムの流れを把握できるようにします

### 5. テストの再実行と結果の確認

```bash
# 特定のテストのみ実行
poetry run pytest tests/path/to/failing_test.py -v

# または特定の関数のみ
poetry run pytest tests/path/to/failing_test.py::test_specific_function -v
```

- 追加したログを確認し、問題の原因を特定します
- 必要に応じてさらにログを追加して情報を収集します

### 6. 問題の修正

```python
# 例: インポートエラーの修正
# 変更前
from .config import Config

# 変更後
from .config import BaseConfig as Config
# または
try:
    from .config import Config
except ImportError:
    from .config import BaseConfig as Config
```

- 特定した原因に基づいて問題を修正します
- 最小限の変更で問題を解決するよう心がけます

### 7. 修正の検証

```bash
# 修正後にテストを再実行
poetry run pytest tests/path/to/failing_test.py -v

# すべてのテストを実行して副作用がないことを確認
poetry run pytest
```

- 修正がうまくいかない場合は、ステップ3～6を繰り返します
- 修正によって他のテストに影響が出ていないか確認します

### 8. 知見のドキュメント化

バグ修正の記録は `docs/tests_bugs/` ディレクトリに保存します。以下のフォーマットでドキュメントを作成します：

```markdown
# 解決した問題: [バグ名]

## 現象

- どのようなエラーが発生したか
- どのテストが失敗したか

## 根本原因

- なぜ問題が発生したのか
- どのコードが問題を引き起こしていたのか

## 解決策

- どのように問題を修正したか
- なぜその修正方法を選んだか

## コード変更

\```python
# 変更前
[問題のあるコード]

# 変更後
[修正後のコード]
\```

## 学んだこと

- この問題から得られた教訓
- 将来同様の問題を防ぐための提案
```

### 9. 変更のコミットとマージ

```bash
# 変更をコミット
git add .
git commit -m "Fix: [バグの簡潔な説明]"

# メインブランチに変更をマージ
git checkout main
git merge test-debug-<バグ名>-<日付>
git push origin main
```

- コミットメッセージは具体的で分かりやすくします
- 必要に応じてPull Requestを作成してレビューを依頼します

## 追加のベストプラクティス

### 複雑な問題への対処

```python
# 一時的にテストをスキップ
@pytest.mark.skip(reason="現在修正中の問題があります")
def test_something():
    ...

# 条件付きスキップ
@pytest.mark.skipif(
    condition=some_condition,
    reason="特定の条件下でスキップします"
)
def test_conditional():
    ...

# モックを使用して依存関係を切り離す
@pytest.fixture
def mock_service(monkeypatch):
    mock = MagicMock()
    monkeypatch.setattr('src.app.Service', mock)
    return mock
```

### 環境問題の切り分け

```bash
# キャッシュをクリア
rm -rf __pycache__/ .pytest_cache/

# 環境をリセット
pip install --force-reinstall -r requirements.txt

# Pythonパスを明示的に設定
PYTHONPATH=/correct/path pytest
```

### チームでの協力

- 複雑な問題は他のメンバーと共有して協力して解決する
- ペアプログラミングを活用する
- 定期的にデバッグの知見を共有する会議を設ける

## まとめ

この手順書に従うことで、効率的にテスト失敗をデバッグし、解決することができます。最も重要なのは、体系的なアプローチで一つずつ問題を解決していくことです。デバッグ結果をドキュメント化することで、チーム全体の知識を向上させ、同様の問題の再発を防ぐことができます。 