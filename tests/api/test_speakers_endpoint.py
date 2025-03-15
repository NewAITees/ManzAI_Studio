"""
話者一覧取得APIのテストモジュール
"""
import json
import pytest
from unittest.mock import patch

from tests.utils.test_helpers import app, client, create_mock_voicevox_service

@pytest.fixture
def mock_voicevox_service():
    """
    モックVoiceVoxサービスを提供するフィクスチャ
    """
    with patch('src.app.voicevox_service') as mock_service:
        mock_service_instance = create_mock_voicevox_service()
        mock_service.return_value = mock_service_instance
        yield mock_service_instance

def test_speakers_endpoint_success(client, mock_voicevox_service):
    """
    話者一覧取得APIの成功ケースをテスト
    
    Args:
        client: テスト用クライアント
        mock_voicevox_service: モックVoiceVoxサービス
    """
    # 期待される話者リスト
    expected_speakers = [
        {"name": "四国めたん", "styles": [{"id": 2, "name": "ノーマル"}]},
        {"name": "ずんだもん", "styles": [{"id": 3, "name": "ノーマル"}]}
    ]
    mock_voicevox_service.list_speakers.return_value = expected_speakers
    
    # テスト実行
    response = client.get('/api/speakers')
    
    # レスポンスの検証
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "speakers" in data
    assert data["speakers"] == expected_speakers
    
    # モックサービスの呼び出し検証
    mock_voicevox_service.list_speakers.assert_called_once()

def test_speakers_endpoint_service_error(client, mock_voicevox_service):
    """
    サービスエラー発生時の話者一覧取得APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_voicevox_service: モックVoiceVoxサービス
    """
    # VoiceVoxサービスがエラーを発生させるように設定
    mock_voicevox_service.list_speakers.side_effect = Exception("サービスエラー")
    
    # テスト実行
    response = client.get('/api/speakers')
    
    # レスポンスの検証
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data 