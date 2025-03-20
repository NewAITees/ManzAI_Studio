"""サービスフォールバックのテスト"""
import pytest
import requests
from unittest.mock import patch, MagicMock
from src.backend.app.services.ollama_service import OllamaService, OllamaServiceError
from src.backend.app.services.voicevox_service import VoiceVoxService, VoiceVoxServiceError

class TestOllamaServiceFallbacks:
    """Ollamaサービスのフォールバック機能テスト"""
    
    def test_timeout_handling(self):
        """タイムアウト時のフォールバック処理"""
        with patch('requests.post', side_effect=requests.exceptions.Timeout):
            service = OllamaService()
            
            with pytest.raises(OllamaServiceError, match="Timeout error occurred"):
                service.generate_manzai_script("テスト")
            
            # フォールバック応答の検証
            fallback = service.get_fallback_response("テスト")
            assert isinstance(fallback, list)
            assert len(fallback) >= 2  # 最低2つの応答があることを確認
            assert all('role' in entry and 'text' in entry for entry in fallback)
            assert all(entry['role'] in ['tsukkomi', 'boke'] for entry in fallback)
            assert all(isinstance(entry['text'], str) and len(entry['text']) > 0 for entry in fallback)
    
    def test_connection_error_handling(self):
        """接続エラー時のフォールバック処理"""
        with patch('requests.post', side_effect=requests.exceptions.ConnectionError):
            service = OllamaService()
            
            with pytest.raises(OllamaServiceError, match="Connection error with Ollama API"):
                service.generate_manzai_script("テスト")
            
            # フォールバック応答の検証
            fallback = service.get_fallback_response("テスト")
            assert isinstance(fallback, list)
            assert len(fallback) >= 2
            assert all('role' in entry and 'text' in entry for entry in fallback)

class TestVoiceVoxServiceFallbacks:
    """VoiceVoxサービスのフォールバック機能テスト"""
    
    def test_service_unavailable_handling(self):
        """サービス利用不可時のフォールバック処理"""
        with patch('requests.post', side_effect=requests.exceptions.HTTPError):
            service = VoiceVoxService()
            
            with pytest.raises(VoiceVoxServiceError, match="HTTP error occurred with VoiceVox API"):
                service.generate_voice("こんにちは", speaker_id=1)
            
            # フォールバック音声の検証
            fallback_audio = service.get_fallback_audio("こんにちは")
            assert isinstance(fallback_audio, bytes)
            assert len(fallback_audio) > 0
            # 音声データの基本的な検証（WAVファイルのヘッダー）
            assert fallback_audio.startswith(b'RIFF')
    
    def test_timeout_handling(self):
        """タイムアウト時のフォールバック処理"""
        with patch('requests.post', side_effect=requests.exceptions.Timeout):
            service = VoiceVoxService()
            
            with pytest.raises(VoiceVoxServiceError, match="Timeout error occurred while communicating with VoiceVox API"):
                service.generate_voice("こんにちは", speaker_id=1)
            
            # フォールバック音声の検証
            fallback_audio = service.get_fallback_audio("こんにちは")
            assert isinstance(fallback_audio, bytes)
            assert len(fallback_audio) > 0
            assert fallback_audio.startswith(b'RIFF') 