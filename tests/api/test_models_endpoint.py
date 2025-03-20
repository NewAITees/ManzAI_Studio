"""
Live2Dモデル一覧取得APIのテストモジュール
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from tests.utils.test_helpers import app, client

@pytest.fixture
def mock_models():
    """
    モックモデルリストを提供するフィクスチャ
    """
    return [
        {
            "id": "model1",
            "name": "モデル1",
            "thumbnail": "thumbnails/model1.png",
            "description": "テストモデル1の説明"
        },
        {
            "id": "model2",
            "name": "モデル2",
            "thumbnail": "thumbnails/model2.png",
            "description": "テストモデル2の説明"
        }
    ]

@pytest.fixture
def mock_model_service(app):
    """
    モックモデルサービスを提供するフィクスチャ
    
    Args:
        app: Flaskアプリケーションのインスタンス
    """
    mock_instance = MagicMock()
    app.ollama_service = mock_instance
    return mock_instance

def test_models_endpoint_success(client, mock_model_service, mock_models):
    """
    モデル一覧取得APIの成功ケースをテスト
    
    Args:
        client: テスト用クライアント
        mock_model_service: モックモデルサービス
        mock_models: モックモデルリスト
    """
    # モックサービスの設定
    mock_model_service.list_models.return_value = mock_models
    
    # テスト実行
    response = client.get('/api/models')
    
    # レスポンスの検証
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "models" in data
    assert data["models"] == mock_models
    
    # モックサービスの呼び出し検証
    mock_model_service.list_models.assert_called_once()

def test_models_endpoint_service_error(client, mock_model_service):
    """
    サービスエラー発生時のモデル一覧取得APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_model_service: モックモデルサービス
    """
    # モデルサービスがエラーを発生させるように設定
    mock_model_service.list_models.side_effect = Exception("サービスエラー")
    
    # テスト実行
    response = client.get('/api/models')
    
    # レスポンスの検証
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data 