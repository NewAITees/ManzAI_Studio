import pytest
import requests
from unittest.mock import patch, MagicMock
from src.services.ollama_service import OllamaService, OllamaServiceError
from src.services.voicevox_service import VoiceVoxService, VoiceVoxServiceError

@patch('requests.post')
def test_ollama_service_timeout_handling(mock_post):
    """Ollamaサービスがタイムアウトした場合の適切なエラー処理を確認"""
    mock_post.side_effect = requests.exceptions.Timeout()
    
    service = OllamaService()
    with pytest.raises(OllamaServiceError) as excinfo:
        service.generate_manzai_script("テスト")
    
    assert "timeout" in str(excinfo.value).lower()
    
    # フォールバック応答を取得して検証
    fallback = service.get_fallback_response("テスト")
    assert fallback is not None
    assert isinstance(fallback, list)
    assert len(fallback) > 0
    
    # 各エントリが正しい構造を持っていることを確認
    for entry in fallback:
        assert 'role' in entry
        assert 'text' in entry
        assert entry['role'] in ['tsukkomi', 'boke']

@patch('requests.post')
def test_ollama_service_connection_error_handling(mock_post):
    """Ollamaサービスの接続エラーを適切に処理することを確認"""
    mock_post.side_effect = requests.exceptions.ConnectionError()
    
    service = OllamaService()
    with pytest.raises(OllamaServiceError) as excinfo:
        service.generate_manzai_script("テスト")
    
    assert "connection" in str(excinfo.value).lower()

@patch('requests.post')
def test_voicevox_service_unavailable_handling(mock_post):
    """VoiceVoxサービスが利用不可の場合の適切なエラー処理を確認"""
    mock_post.side_effect = requests.exceptions.HTTPError()
    
    service = VoiceVoxService()
    with pytest.raises(VoiceVoxServiceError):
        service.generate_voice("こんにちは", speaker_id=1)
    
    # テキスト読み上げのフォールバックが機能することを確認
    fallback_audio = service.get_fallback_audio("こんにちは")
    assert fallback_audio is not None
    assert isinstance(fallback_audio, bytes)
    assert len(fallback_audio) > 0

@patch('requests.post')
def test_voicevox_service_timeout_handling(mock_post):
    """VoiceVoxサービスがタイムアウトした場合の適切なエラー処理を確認"""
    mock_post.side_effect = requests.exceptions.Timeout()
    
    service = VoiceVoxService()
    with pytest.raises(VoiceVoxServiceError) as excinfo:
        service.generate_voice("こんにちは", speaker_id=1)
    
    assert "timeout" in str(excinfo.value).lower() 