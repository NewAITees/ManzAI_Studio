import pytest
from unittest.mock import patch, MagicMock
import re
from src.services.ollama_service import OllamaService, OllamaServiceError
from src.utils.prompt_loader import load_prompt
import requests

@pytest.fixture
def ollama_service():
    """テスト用のOllamaServiceインスタンスを作成"""
    return OllamaService()

def test_init_with_custom_params():
    """カスタムパラメータでOllamaServiceが初期化されることを確認"""
    service = OllamaService("http://custom-url", "custom-model")
    assert service.base_url == "http://custom-url"
    assert service.model == "custom-model"

def test_generate_manzai_script_returns_valid_structure(ollama_service):
    """Ollamaサービスが有効な漫才スクリプト構造を返すことを確認"""
    # モックレスポンス
    mock_response_json = {
        "response": """
A: こんにちは、今日は猫について話しましょう
B: 猫って可愛いですよね〜
A: そうですね、でも猫は気まぐれなところがありますよね
        """
    }
    
    with patch('src.services.ollama_service.load_prompt') as mock_load_prompt, \
         patch('requests.post') as mock_post:
        mock_load_prompt.return_value = "テスト用プロンプト"
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_response_json
        
        # メソッドを呼び出し
        result = ollama_service.generate_manzai_script("猫")
        
        # テスト
        assert isinstance(result, dict)
        assert "script" in result
        assert len(result["script"]) == 3  # 3行の台詞
        
        # 各行を確認
        assert result["script"][0]["role"] == "tsukkomi"
        assert "こんにちは" in result["script"][0]["text"]
        
        assert result["script"][1]["role"] == "boke"
        assert "可愛い" in result["script"][1]["text"]
        
        # プロンプトの読み込みを確認
        mock_load_prompt.assert_called_once_with("manzai_prompt", topic="猫")
        
        # APIリクエストを確認
        mock_post.assert_called_once()
        assert ollama_service.model in str(mock_post.call_args)
        assert "テスト用プロンプト" in str(mock_post.call_args)

def test_parse_manzai_script_with_code_block():
    """コードブロック内のスクリプトを適切に解析することを確認"""
    service = OllamaService()
    raw_script = """
生成されたスクリプトです:
```
A: こんにちは
B: どうも
A: 今日はいい天気ですね
```
以上です。
    """
    
    result = service._parse_manzai_script(raw_script)
    
    assert len(result) == 3
    assert result[0]["role"] == "tsukkomi"
    assert result[0]["text"] == "こんにちは"
    assert result[1]["role"] == "boke"
    assert result[2]["role"] == "tsukkomi"

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
    assert result[0]["role"] == "tsukkomi"
    assert result[0]["text"] == "こんにちは"
    assert result[1]["role"] == "boke"
    assert result[2]["role"] == "tsukkomi"

def test_generate_manzai_script_handles_connection_error(ollama_service):
    """Ollamaサービスが接続エラーを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(OllamaServiceError) as exc_info:
            ollama_service.generate_manzai_script("テスト")
        
        assert "connection error" in str(exc_info.value).lower()

def test_generate_manzai_script_handles_invalid_response(ollama_service):
    """Ollamaサービスが不正なレスポンスを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        
        with pytest.raises(OllamaServiceError) as exc_info:
            ollama_service.generate_manzai_script("テスト")
        
        assert "invalid response" in str(exc_info.value).lower()

def test_generate_manzai_script_handles_empty_topic(ollama_service):
    """Ollamaサービスが空のトピックを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        ollama_service.generate_manzai_script("")
    
    assert "topic cannot be empty" in str(exc_info.value).lower() 