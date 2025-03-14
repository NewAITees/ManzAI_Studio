import pytest
from unittest.mock import patch, MagicMock
from src.services.ollama_service import OllamaService, OllamaServiceError

@pytest.fixture
def ollama_service():
    """テスト用のOllamaServiceインスタンスを作成"""
    return OllamaService()

def test_generate_manzai_script_returns_valid_structure(ollama_service):
    """Ollamaサービスが有効な漫才スクリプト構造を返すことを確認"""
    mock_response = {
        'script': [
            {'role': 'tsukkomi', 'text': 'こんにちは'},
            {'role': 'boke', 'text': 'どうも！'}
        ]
    }
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200
        
        script = ollama_service.generate_manzai_script("猫")
        
        assert isinstance(script, dict)
        assert 'script' in script
        assert len(script['script']) > 0
        
        for line in script['script']:
            assert 'role' in line
            assert 'text' in line
            assert line['role'] in ['tsukkomi', 'boke']

def test_generate_manzai_script_handles_connection_error(ollama_service):
    """Ollamaサービスが接続エラーを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = ConnectionError()
        
        with pytest.raises(OllamaServiceError) as exc_info:
            ollama_service.generate_manzai_script("テスト")
        
        assert "connection error" in str(exc_info.value).lower()

def test_generate_manzai_script_handles_invalid_response(ollama_service):
    """Ollamaサービスが不正なレスポンスを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {'error': 'Internal Server Error'}
        
        with pytest.raises(OllamaServiceError) as exc_info:
            ollama_service.generate_manzai_script("テスト")
        
        assert "invalid response" in str(exc_info.value).lower()

def test_generate_manzai_script_handles_missing_script(ollama_service):
    """Ollamaサービスがスクリプトを含まないレスポンスを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'invalid': 'response'}
        
        with pytest.raises(OllamaServiceError) as exc_info:
            ollama_service.generate_manzai_script("テスト")
        
        assert "invalid script format" in str(exc_info.value).lower()

def test_generate_manzai_script_handles_empty_topic(ollama_service):
    """Ollamaサービスが空のトピックを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        ollama_service.generate_manzai_script("")
    
    assert "topic cannot be empty" in str(exc_info.value).lower() 