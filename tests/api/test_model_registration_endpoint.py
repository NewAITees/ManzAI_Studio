"""
Live2Dモデル登録APIのテストモジュール
"""
import json
import pytest
import io
from unittest.mock import patch, MagicMock

from tests.utils.test_helpers import app, client

@pytest.fixture
def mock_model_service():
    """
    モックモデルサービスを提供するフィクスチャ
    """
    with patch('src.app.model_service') as mock_service:
        mock_instance = MagicMock()
        mock_service.return_value = mock_instance
        yield mock_instance

def test_model_registration_success(client, mock_model_service):
    """
    モデル登録APIの成功ケースをテスト
    
    Args:
        client: テスト用クライアント
        mock_model_service: モックモデルサービス
    """
    # モックサービスの設定
    mock_model_id = "test_model_123"
    mock_model_service.register_model.return_value = mock_model_id
    
    # テスト用ファイルデータ
    model_data = io.BytesIO(b"test model data")
    thumbnail_data = io.BytesIO(b"test thumbnail data")
    
    # マルチパートフォームデータ
    data = {
        'name': 'テストモデル',
        'description': 'テストモデルの説明',
        'model_file': (model_data, 'model.zip'),
        'thumbnail': (thumbnail_data, 'thumbnail.png')
    }
    
    # テスト実行
    response = client.post('/api/models/register',
                          data=data,
                          content_type='multipart/form-data')
    
    # レスポンスの検証
    assert response.status_code == 200
    result = json.loads(response.data)
    assert "model_id" in result
    assert result["model_id"] == mock_model_id
    
    # モックサービスの呼び出し検証
    mock_model_service.register_model.assert_called_once()

def test_model_registration_missing_files(client, mock_model_service):
    """
    必須ファイルが不足している場合のモデル登録APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_model_service: モックモデルサービス
    """
    # 不完全なフォームデータ（ファイルなし）
    data = {
        'name': 'テストモデル',
        'description': 'テストモデルの説明'
    }
    
    # テスト実行
    response = client.post('/api/models/register',
                          data=data,
                          content_type='multipart/form-data')
    
    # レスポンスの検証
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    
    # モックサービスが呼び出されていないことを検証
    mock_model_service.register_model.assert_not_called()

def test_model_registration_invalid_format(client, mock_model_service):
    """
    無効なファイル形式での登録をテスト
    
    Args:
        client: テスト用クライアント
        mock_model_service: モックモデルサービス
    """
    # 無効なファイル形式
    model_data = io.BytesIO(b"test model data")
    thumbnail_data = io.BytesIO(b"test thumbnail data")
    
    # マルチパートフォームデータ
    data = {
        'name': 'テストモデル',
        'description': 'テストモデルの説明',
        'model_file': (model_data, 'model.txt'),  # 無効な拡張子
        'thumbnail': (thumbnail_data, 'thumbnail.png')
    }
    
    # テスト実行
    response = client.post('/api/models/register',
                          data=data,
                          content_type='multipart/form-data')
    
    # レスポンスの検証
    assert response.status_code == 400
    result = json.loads(response.data)
    assert "error" in result
    
    # モックサービスが呼び出されていないことを検証
    mock_model_service.register_model.assert_not_called()

def test_model_registration_service_error(client, mock_model_service):
    """
    サービスエラー発生時のモデル登録APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_model_service: モックモデルサービス
    """
    # モックサービスにエラーを設定
    mock_model_service.register_model.side_effect = Exception("登録エラー")
    
    # テスト用ファイルデータ
    model_data = io.BytesIO(b"test model data")
    thumbnail_data = io.BytesIO(b"test thumbnail data")
    
    # マルチパートフォームデータ
    data = {
        'name': 'テストモデル',
        'description': 'テストモデルの説明',
        'model_file': (model_data, 'model.zip'),
        'thumbnail': (thumbnail_data, 'thumbnail.png')
    }
    
    # テスト実行
    response = client.post('/api/models/register',
                          data=data,
                          content_type='multipart/form-data')
    
    # レスポンスの検証
    assert response.status_code == 500
    result = json.loads(response.data)
    assert "error" in result 