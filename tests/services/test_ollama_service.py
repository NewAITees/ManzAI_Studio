import pytest
from unittest.mock import patch, MagicMock
import re
from src.services.ollama_service import OllamaService, OllamaServiceError
from src.utils.prompt_loader import PromptLoader
import requests

@pytest.fixture
def mock_prompt_loader():
    """Mock PromptLoader for testing"""
    loader = MagicMock(spec=PromptLoader)
    loader.load_template.return_value = "テスト用プロンプト"
    return loader

@pytest.fixture
def ollama_service(mock_prompt_loader):
    """Create OllamaService instance with mocked dependencies"""
    service = OllamaService()
    service.prompt_loader = mock_prompt_loader
    return service

def test_init_with_custom_params():
    """カスタムパラメータでOllamaServiceが初期化されることを確認"""
    service = OllamaService(base_url="http://custom-url")
    assert service.client.base_url == "http://custom-url"

def test_generate_manzai_script_returns_valid_structure(ollama_service, mock_prompt_loader):
    """Ollamaサービスが有効な漫才スクリプト構造を返すことを確認"""
    # モックレスポンス
    mock_response_json = {
        "response": """```json
{
    "script": [
        {"speaker": "A", "text": "こんにちは、今日は猫について話しましょう"},
        {"speaker": "B", "text": "猫って可愛いですよね〜"},
        {"speaker": "A", "text": "そうですね、でも猫は気まぐれなところがありますよね"}
    ]
}```"""
    }

    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response_json

        # メソッドを呼び出し
        result = ollama_service.generate_manzai_script("猫")

        # プロンプトの読み込みを確認
        mock_prompt_loader.load_template.assert_called_once_with("manzai_prompt", topic="猫")

        # レスポンスの構造を確認
        assert len(result) == 3
        assert result[0]["speaker"] == "A"
        assert "猫" in result[0]["text"]
        assert result[1]["speaker"] == "B"
        assert result[2]["speaker"] == "A"

def test_parse_manzai_script_with_code_block():
    """コードブロック内のスクリプトを適切に解析することを確認"""
    service = OllamaService()
    raw_script = """```
{
    "script": [
        {"speaker": "A", "text": "こんにちは"},
        {"speaker": "B", "text": "どうも"},
        {"speaker": "A", "text": "今日はいい天気ですね"}
    ]
}```"""
    
    result = service._parse_manzai_script(raw_script)
    
    assert len(result) == 3
    assert result[0]["speaker"] == "A"
    assert result[0]["text"] == "こんにちは"
    assert result[1]["speaker"] == "B"
    assert result[2]["speaker"] == "A"

def test_parse_manzai_script_without_code_block():
    """コードブロックがない場合も適切に解析することを確認"""
    service = OllamaService()
    raw_script = """
A: こんにちは
B: どうも
A: 今日はいい天気ですね
    """
    
    result = service._parse_manzai_script(raw_script)
    
    assert len(result) == 3
    assert result[0]["speaker"] == "A"
    assert result[0]["text"] == "こんにちは"
    assert result[1]["speaker"] == "B"
    assert result[2]["speaker"] == "A"

def test_generate_manzai_script_handles_connection_error(ollama_service):
    """Ollamaサービスが接続エラーを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = ConnectionError("Connection failed")
        
        with pytest.raises(OllamaServiceError) as exc_info:
            ollama_service.generate_manzai_script("テスト")
        
        assert "connection failed" in str(exc_info.value).lower()

def test_generate_manzai_script_handles_invalid_response(ollama_service):
    """Ollamaサービスが不正なレスポンスを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.side_effect = Exception("Invalid response")
        
        with pytest.raises(OllamaServiceError) as exc_info:
            ollama_service.generate_manzai_script("テスト")
        
        assert "error" in str(exc_info.value).lower()

def test_generate_manzai_script_handles_empty_topic(ollama_service):
    """Ollamaサービスが空のトピックを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        ollama_service.generate_manzai_script("")
    
    assert "empty" in str(exc_info.value).lower() 