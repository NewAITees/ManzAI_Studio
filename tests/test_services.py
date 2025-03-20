"""Test service modules."""
import json
from typing import Dict, List, Any
import pytest
from unittest.mock import Mock, patch
from src.backend.app.services.ollama_service import OllamaClient, OllamaService, OllamaServiceError
from src.backend.app.utils.prompt_loader import PromptLoader
from src.backend.app.models.script import Role, ScriptLine

@pytest.fixture
def mock_response():
    """Mock response for requests."""
    mock = Mock()
    mock.status_code = 200
    return mock

@pytest.fixture
def ollama_client():
    """Create OllamaClient instance."""
    return OllamaClient(base_url="http://test:11434")

@pytest.fixture
def ollama_service():
    """Create OllamaService instance with mocked health check."""
    with patch.object(OllamaService, 'perform_health_check') as mock_health:
        mock_health.return_value = {
            "status": "healthy",
            "error": None,
            "available_models": ["gemma3:4b", "test-model"]
        }
        service = OllamaService(base_url="http://test:11434", instance_type="local")
        service.prompt_loader = Mock(spec=PromptLoader)
        yield service

def test_ollama_client_init():
    """Test OllamaClient initialization."""
    client = OllamaClient(base_url="http://test:11434")
    assert client.base_url == "http://test:11434"
    assert client.instance_type == "local"

def test_prepare_request_data(ollama_client):
    """Test request data preparation."""
    data = ollama_client._prepare_request_data("test prompt", "test-model")
    assert data["prompt"] == "test prompt"
    assert data["model"] == "test-model"
    assert data["stream"] is False

@patch.object(OllamaClient, 'check_ollama_availability')
@patch("requests.post")
def test_generate_text_sync_success(mock_post, mock_check, ollama_client, mock_response):
    """Test successful text generation."""
    mock_check.return_value = {
        "available": True,
        "models": ["test-model"],
        "error": None
    }
    mock_response.json.return_value = {"response": "generated text"}
    mock_post.return_value = mock_response
    
    result = ollama_client.generate_text_sync("test prompt", "test-model")
    assert result == "generated text"
    mock_post.assert_called_once()

@patch.object(OllamaClient, 'check_ollama_availability')
@patch("requests.post")
def test_generate_text_sync_error(mock_post, mock_check, ollama_client):
    """Test text generation error handling."""
    mock_check.return_value = {
        "available": True,
        "models": ["test-model"],
        "error": None
    }
    mock_post.side_effect = Exception("API error")
    
    with pytest.raises(OllamaServiceError):
        ollama_client.generate_text_sync("test prompt", "test-model")

@patch("requests.get")
def test_list_models_success(mock_get, ollama_client, mock_response):
    """Test successful model listing."""
    mock_response.json.return_value = {"models": [{"name": "test-model"}]}
    mock_get.return_value = mock_response
    
    result = ollama_client.list_models()
    assert len(result) == 1
    assert result[0]["name"] == "test-model"

def test_extract_json_block_success(ollama_client):
    """Test JSON block extraction."""
    text = '```json\n{"key": "value"}\n```'
    result = ollama_client._extract_json_block(text)
    assert json.loads(result) == {"key": "value"}

def test_extract_json_block_error(ollama_client):
    """Test JSON block extraction error."""
    with pytest.raises(OllamaServiceError):
        ollama_client._extract_json_block("invalid json")

def test_ollama_service_init():
    """Test OllamaService initialization."""
    with patch.object(OllamaService, 'perform_health_check') as mock_health:
        mock_health.return_value = {
            "status": "healthy",
            "error": None,
            "available_models": ["gemma3:4b", "test-model"]
        }
        service = OllamaService(base_url="http://test:11434", instance_type="local")
        assert isinstance(service.client, OllamaClient)

@patch.object(OllamaClient, "generate_json_sync")
def test_generate_manzai_script_success(mock_generate, ollama_service):
    """Test successful manzai script generation."""
    ollama_service.prompt_loader.load_template.return_value = "test prompt"
    mock_generate.return_value = {
        "script": [
            {"speaker": "A", "text": "こんにちは"},
            {"speaker": "B", "text": "どうも"}
        ]
    }
    
    result = ollama_service.generate_manzai_script("テスト")
    assert len(result) == 2
    assert isinstance(result[0], ScriptLine)
    assert result[0].role == Role.TSUKKOMI
    assert result[0].text == "こんにちは"
    assert isinstance(result[1], ScriptLine)
    assert result[1].role == Role.BOKE
    assert result[1].text == "どうも"

@patch.object(OllamaClient, "generate_json_sync")
def test_generate_manzai_script_error(mock_generate, ollama_service):
    """Test manzai script generation error handling."""
    ollama_service.prompt_loader.load_template.return_value = "test prompt"
    mock_generate.side_effect = OllamaServiceError("API error")
    
    with pytest.raises(OllamaServiceError):
        ollama_service.generate_manzai_script("テスト") 