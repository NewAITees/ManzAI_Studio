"""
台本音声合成APIのテストモジュール
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from tests.utils.test_helpers import app, client, create_mock_voicevox_service, create_mock_audio_manager

@pytest.fixture
def mock_services():
    """
    モックサービスを提供するフィクスチャ
    """
    with patch('src.app.voicevox_service') as mock_voicevox, \
         patch('src.app.audio_manager') as mock_audio_manager:
        
        mock_voicevox_instance = create_mock_voicevox_service()
        mock_audio_manager_instance = create_mock_audio_manager()
        
        mock_voicevox.return_value = mock_voicevox_instance
        mock_audio_manager.return_value = mock_audio_manager_instance
        
        yield {
            'voicevox': mock_voicevox_instance,
            'audio_manager': mock_audio_manager_instance
        }

def test_synthesize_endpoint_success(client, mock_services):
    """
    台本音声合成APIの成功ケースをテスト
    
    Args:
        client: テスト用クライアント
        mock_services: モックサービス
    """
    # リクエストデータ
    request_data = {
        "script": [
            {"speaker": "ツッコミ", "text": "こんにちは", "speaker_id": 1},
            {"speaker": "ボケ", "text": "どうも", "speaker_id": 2}
        ]
    }
    
    # テスト実行
    response = client.post('/api/synthesize', 
                          data=json.dumps(request_data),
                          content_type='application/json')
    
    # レスポンスの検証
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "audio_data" in data
    assert isinstance(data["audio_data"], list)
    assert len(data["audio_data"]) == 2
    
    # 各オーディオデータのフォーマット検証
    for audio in data["audio_data"]:
        assert "speaker" in audio
        assert "text" in audio
        assert "audio_file" in audio
    
    # モックサービスの呼び出し検証
    assert mock_services['voicevox'].synthesize.call_count == 2

def test_synthesize_endpoint_invalid_request(client, mock_services):
    """
    不正なリクエストでの台本音声合成APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_services: モックサービス
    """
    # 不正なリクエストデータ（scriptキーなし）
    request_data = {
        "invalid_key": "invalid_value"
    }
    
    # テスト実行
    response = client.post('/api/synthesize', 
                          data=json.dumps(request_data),
                          content_type='application/json')
    
    # レスポンスの検証
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_synthesize_endpoint_service_error(client, mock_services):
    """
    サービスエラー発生時の台本音声合成APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_services: モックサービス
    """
    # VoiceVoxサービスがエラーを発生させるように設定
    mock_services['voicevox'].synthesize.side_effect = Exception("サービスエラー")
    
    # リクエストデータ
    request_data = {
        "script": [
            {"speaker": "ツッコミ", "text": "こんにちは", "speaker_id": 1},
            {"speaker": "ボケ", "text": "どうも", "speaker_id": 2}
        ]
    }
    
    # テスト実行
    response = client.post('/api/synthesize', 
                          data=json.dumps(request_data),
                          content_type='application/json')
    
    # レスポンスの検証
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data 