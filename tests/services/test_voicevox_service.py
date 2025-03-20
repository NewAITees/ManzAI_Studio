"""VoiceVoxサービスのテスト"""
import pytest
from unittest.mock import patch, MagicMock
import requests
from typing import Dict, Any

from src.backend.app.services.voicevox_service import VoiceVoxService, VoiceVoxServiceError

@pytest.fixture
def voicevox_service() -> VoiceVoxService:
    """テスト用のVoiceVoxServiceインスタンスを作成"""
    return VoiceVoxService()

@pytest.fixture
def mock_query_response() -> Dict[str, Any]:
    """音声合成クエリのモックレスポンス"""
    return {
        'accent_phrases': [{
            'moras': [{
                'text': 'こ',
                'consonant': 'k',
                'consonant_length': 0.1,
                'vowel': 'o',
                'vowel_length': 0.2,
                'pitch': 5.4
            }],
            'accent': 1,
            'pause_mora': None,
            'is_interrogative': False
        }],
        'speedScale': 1.0,
        'pitchScale': 1.0,
        'intonationScale': 1.0,
        'volumeScale': 1.0,
        'prePhonemeLength': 0.1,
        'postPhonemeLength': 0.1,
        'outputSamplingRate': 44100,
        'outputStereo': False,
        'kana': 'コンニチハ'
    }

class TestVoiceVoxBasics:
    """基本機能のテストスイート"""
    
    def test_initialization(self):
        """カスタムパラメータでの初期化テスト"""
        service = VoiceVoxService(base_url="http://custom-url")
        assert service.base_url == "http://custom-url"

    def test_voice_generation_success(self, voicevox_service: VoiceVoxService, mock_query_response: Dict[str, Any]):
        """正常系：音声生成テスト"""
        mock_audio_data = b'test audio data'
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = [
                MagicMock(status_code=200, json=lambda: mock_query_response),
                MagicMock(status_code=200, content=mock_audio_data)
            ]
            
            result = voicevox_service.generate_voice("テスト", speaker_id=1)
            
            assert result == mock_audio_data
            assert mock_post.call_count == 2
            mock_post.assert_called_with(
                f"{voicevox_service.base_url}/synthesis",
                json=mock_query_response,
                timeout=30
            )

class TestVoiceVoxErrorHandling:
    """エラー処理のテストスイート"""
    
    def test_empty_text_validation(self, voicevox_service: VoiceVoxService):
        """空テキストのバリデーション"""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            voicevox_service.generate_voice("", speaker_id=1)

    def test_invalid_speaker_id(self, voicevox_service: VoiceVoxService):
        """不正なスピーカーIDの処理"""
        with pytest.raises(ValueError, match="Invalid speaker ID: -1"):
            voicevox_service.generate_voice("テスト", speaker_id=-1)

    def test_connection_error(self, voicevox_service: VoiceVoxService):
        """接続エラーの処理"""
        with patch('requests.post', side_effect=requests.exceptions.ConnectionError):
            with pytest.raises(VoiceVoxServiceError, match="Connection error with VoiceVox API"):
                voicevox_service.generate_voice("テスト", speaker_id=1)

    def test_timeout_error(self, voicevox_service: VoiceVoxService):
        """タイムアウトエラーの処理"""
        with patch('requests.post', side_effect=requests.exceptions.Timeout):
            with pytest.raises(VoiceVoxServiceError, match="Timeout error occurred while communicating with VoiceVox API"):
                voicevox_service.generate_voice("テスト", speaker_id=1)

class TestVoiceVoxTimingData:
    """タイミングデータ関連のテストスイート"""
    
    def test_timing_data_structure(self, voicevox_service: VoiceVoxService, mock_query_response: Dict[str, Any]):
        """タイミングデータの構造テスト"""
        with patch('requests.post') as mock_post:
            mock_post.return_value = MagicMock(
                status_code=200,
                json=lambda: mock_query_response
            )
            
            result = voicevox_service.get_timing_data("テスト", speaker_id=1)
            
            assert isinstance(result, dict)
            assert 'accent_phrases' in result
            assert len(result['accent_phrases']) > 0
            
            # モーラデータの検証
            mora = result['accent_phrases'][0]['moras'][0]
            assert all(key in mora for key in ['text', 'consonant', 'vowel', 'consonant_length', 'vowel_length'])
            assert isinstance(mora['consonant_length'], float)
            assert isinstance(mora['vowel_length'], float)
            assert mora['text'] == 'こ'
            assert mora['consonant'] == 'k'
            assert mora['vowel'] == 'o' 