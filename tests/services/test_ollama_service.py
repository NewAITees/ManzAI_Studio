import pytest
from unittest.mock import patch, MagicMock
from src.backend.app.services.ollama_service import OllamaService, OllamaServiceError
from src.backend.app.utils.prompt_loader import PromptLoader

@pytest.fixture
def ollama_service():
    """基本的なOllamaServiceインスタンスを提供"""
    return OllamaService()

class TestOllamaServiceBasics:
    """基本機能のテストスイート"""
    
    def test_initialization(self):
        """基本的な初期化テスト"""
        service = OllamaService(base_url="http://custom-url")
        assert service.client.base_url == "http://custom-url"

    def test_script_generation_success(self, ollama_service):
        """正常系：漫才スクリプト生成テスト"""
        mock_response = {
            "response": """{"script": [
                {"speaker": "A", "text": "こんにちは"},
                {"speaker": "B", "text": "どうも"}
            ]}"""
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = mock_response
            
            result = ollama_service.generate_manzai_script("テスト")
            
            assert len(result) == 2
            assert all(key in result[0] for key in ["speaker", "text"])
            assert result[0]["speaker"] == "A"
            assert result[0]["text"] == "こんにちは"
            assert result[1]["speaker"] == "B"
            assert result[1]["text"] == "どうも"

class TestOllamaServiceErrorHandling:
    """エラー処理のテストスイート"""
    
    def test_empty_topic_validation(self, ollama_service):
        """空のトピックに対するバリデーション"""
        with pytest.raises(ValueError, match="Topic cannot be empty"):
            ollama_service.generate_manzai_script("")

    def test_connection_error_handling(self, ollama_service):
        """接続エラーのハンドリング"""
        with patch('requests.post', side_effect=ConnectionError):
            with pytest.raises(OllamaServiceError, match="Connection error with Ollama API"):
                ollama_service.generate_manzai_script("テスト")

    def test_timeout_error_handling(self, ollama_service):
        """タイムアウトエラーのハンドリング"""
        with patch('requests.post', side_effect=TimeoutError):
            with pytest.raises(OllamaServiceError, match="Timeout error occurred"):
                ollama_service.generate_manzai_script("テスト")

class TestScriptParsing:
    """スクリプト解析のテストスイート"""
    
    def test_parse_json_script(self, ollama_service):
        """JSON形式のスクリプト解析"""
        raw_script = """{"script": [
            {"speaker": "A", "text": "テスト"},
            {"speaker": "B", "text": "応答"}
        ]}"""
        
        result = ollama_service._parse_manzai_script(raw_script)
        assert len(result) == 2
        assert result[0]["speaker"] == "A"
        assert result[0]["text"] == "テスト"
        assert result[1]["speaker"] == "B"
        assert result[1]["text"] == "応答" 