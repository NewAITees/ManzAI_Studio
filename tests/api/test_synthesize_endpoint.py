"""
台本音声合成APIのテストモジュール
"""
import json
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_services(app, mock_voicevox_service, mock_audio_manager):
    """
    モックサービスを提供するフィクスチャ
    
    Args:
        app: Flaskアプリケーションのインスタンス
        mock_voicevox_service: VoiceVoxServiceのモック
        mock_audio_manager: AudioManagerのモック
    """
    app.voicevox_service = mock_voicevox_service
    app.audio_manager = mock_audio_manager
    
    # テスト用の戻り値を設定
    mock_voicevox_service.synthesize.return_value = "test_audio_file.wav"
    
    return {
        'voicevox': mock_voicevox_service,
        'audio_manager': mock_audio_manager
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