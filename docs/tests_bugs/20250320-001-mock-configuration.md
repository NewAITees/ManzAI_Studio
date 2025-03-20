# バグ修正記録: モック設定の競合と不足

## 基本情報

- **バグID**: 20250320-001
- **報告日**: 2025-03-20
- **修正日**: 2025-03-20
- **影響範囲**: テストスイート（音声合成APIテスト）
- **重要度**: Medium
- **ステータス**: Closed

## 現象

### エラーメッセージ
```
AttributeError: Mock object has no attribute 'get_audio_file_path'
```

### 失敗したテスト
- `tests/api/test_synthesize_endpoint.py::test_synthesize_endpoint_success`
- `tests/api/test_synthesize_endpoint.py::test_synthesize_endpoint_invalid_request`
- `tests/api/test_synthesize_endpoint.py::test_synthesize_endpoint_service_error`

### 再現手順
1. `poetry run pytest tests/api/test_synthesize_endpoint.py -v`を実行
2. テストがセットアップ段階で失敗

## 根本原因

### 技術的な原因
- モックの設定が複数の場所で重複して定義されていた
- `AudioManager`のモックに必要なメソッドが定義されていなかった
- モックの`spec`パラメータが制限を強くしすぎていた

### 発生要因
- テストヘルパーとconftest.pyでモック設定が重複
- モックの仕様が不完全
- テストコードのリファクタリング時の見落とし

## 解決策

### 実施した修正
1. モック設定の一元化
   - `conftest.py`にモック設定を集約
   - テストヘルパーからの重複を削除
2. モックメソッドの追加
   - `get_audio_file_path`
   - `save_audio`
   - `get_audio_url`
3. モックの柔軟性向上
   - 制限の強い`spec`パラメータを削除

### コード変更

```python
# 変更前（conftest.py）
@pytest.fixture
def mock_audio_manager():
    """Mock audio manager for testing."""
    return MagicMock(spec=AudioManager)

# 変更後（conftest.py）
@pytest.fixture
def mock_audio_manager():
    """Mock audio manager for testing."""
    mock = MagicMock()
    mock.get_audio_file_path.return_value = "/path/to/audio.wav"
    mock.generate_filename.return_value = "test_audio_file.wav"
    mock.save_audio.return_value = "test_audio_file.wav"
    mock.get_audio_url.return_value = "/audio/test_audio_file.wav"
    return mock
```

### 検証方法
- 全テストケースの実行
- モックメソッドの呼び出し回数の検証
- レスポンスデータの構造の検証

## 予防措置

### 再発防止策
1. モックの設定は`conftest.py`に一元化
2. 新しいメソッドを追加する際は、対応するモックメソッドも追加
3. モックの戻り値は明示的に設定
4. テストヘルパーの役割を明確化

### コードレビューのポイント
- モック設定の重複チェック
- 必要なモックメソッドの網羅性確認
- テストヘルパーとconftest.pyの役割分担

## 学んだこと

### 技術的な学び
- モックの柔軟性とテストの安定性のバランス
- テストコードの構造化の重要性
- Pytestのフィクスチャの効果的な活用方法

### プロセスの改善点
- テストコードのリファクタリング時のチェックリスト作成
- モック設定の定期的な見直し
- テストヘルパーの使用ガイドライン整備

## 関連情報

### 参考リンク
- [Pytest Documentation - Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)

### 関連チケット
- なし 