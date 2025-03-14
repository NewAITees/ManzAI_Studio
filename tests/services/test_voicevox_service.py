import pytest
from unittest.mock import patch, MagicMock
from src.services.voicevox_service import VoiceVoxService, VoiceVoxServiceError

@pytest.fixture
def voicevox_service():
    """テスト用のVoiceVoxServiceインスタンスを作成"""
    return VoiceVoxService()

def test_generate_voice_returns_audio_data(voicevox_service):
    """VoiceVoxサービスが有効な音声データを返すことを確認"""
    mock_audio_data = b'test audio data'
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.content = mock_audio_data
        mock_post.return_value.status_code = 200
        
        audio_data = voicevox_service.generate_voice("こんにちは", speaker_id=1)
        
        assert audio_data is not None
        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0
        assert audio_data == mock_audio_data

def test_get_timing_data_returns_valid_structure(voicevox_service):
    """VoiceVoxサービスが有効なタイミングデータを返すことを確認"""
    mock_response = {
        'accent_phrases': [
            {
                'moras': [
                    {'text': 'こ', 'start_time': 0.0, 'end_time': 0.1},
                    {'text': 'ん', 'start_time': 0.1, 'end_time': 0.2},
                    {'text': 'に', 'start_time': 0.2, 'end_time': 0.3},
                    {'text': 'ち', 'start_time': 0.3, 'end_time': 0.4},
                    {'text': 'は', 'start_time': 0.4, 'end_time': 0.5}
                ]
            }
        ]
    }
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200
        
        timing = voicevox_service.get_timing_data("こんにちは", speaker_id=1)
        
        assert isinstance(timing, dict)
        assert 'accent_phrases' in timing
        assert len(timing['accent_phrases']) > 0
        
        for accent in timing['accent_phrases']:
            assert 'moras' in accent
            for mora in accent['moras']:
                assert 'text' in mora
                assert 'start_time' in mora
                assert 'end_time' in mora
                assert isinstance(mora['start_time'], float)
                assert isinstance(mora['end_time'], float)

def test_generate_voice_handles_connection_error(voicevox_service):
    """VoiceVoxサービスが接続エラーを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = ConnectionError()
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.generate_voice("テスト", speaker_id=1)
        
        assert "connection error" in str(exc_info.value).lower()

def test_generate_voice_handles_invalid_response(voicevox_service):
    """VoiceVoxサービスが不正なレスポンスを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {'error': 'Internal Server Error'}
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.generate_voice("テスト", speaker_id=1)
        
        assert "invalid response" in str(exc_info.value).lower()

def test_generate_voice_handles_empty_text(voicevox_service):
    """VoiceVoxサービスが空のテキストを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        voicevox_service.generate_voice("", speaker_id=1)
    
    assert "text cannot be empty" in str(exc_info.value).lower()

def test_generate_voice_handles_invalid_speaker_id(voicevox_service):
    """VoiceVoxサービスが不正なスピーカーIDを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        voicevox_service.generate_voice("テスト", speaker_id=-1)
    
    assert "invalid speaker id" in str(exc_info.value).lower() 