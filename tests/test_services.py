"""Test service modules."""

import json
import os
from unittest.mock import Mock, patch

import pytest

from src.backend.app.models.audio import AudioSynthesisResult, SpeechTimingData
from src.backend.app.models.script import Role, ScriptLine
from src.backend.app.models.service import VoiceVoxSpeaker
from src.backend.app.services.ollama_service import (
    OllamaClient,
    OllamaService,
    OllamaServiceError,
)
from src.backend.app.services.voicevox_service import (
    VoiceVoxService,
    VoiceVoxServiceError,
)
from src.backend.app.utils.prompt_loader import PromptLoader


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
    with patch.object(OllamaService, "perform_health_check") as mock_health:
        mock_health.return_value = {
            "status": "healthy",
            "error": None,
            "available_models": ["gemma3:4b", "test-model"],
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


@patch.object(OllamaClient, "check_ollama_availability")
@patch("requests.post")
def test_generate_text_sync_success(mock_post, mock_check, ollama_client, mock_response):
    """Test successful text generation."""
    mock_check.return_value = {
        "available": True,
        "models": ["test-model"],
        "error": None,
    }
    mock_response.json.return_value = {"response": "generated text"}
    mock_post.return_value = mock_response

    result = ollama_client.generate_text_sync("test prompt", "test-model")
    assert result == "generated text"
    mock_post.assert_called_once()


@patch.object(OllamaClient, "check_ollama_availability")
@patch("requests.post")
def test_generate_text_sync_error(mock_post, mock_check, ollama_client):
    """Test text generation error handling."""
    mock_check.return_value = {
        "available": True,
        "models": ["test-model"],
        "error": None,
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
    with patch.object(OllamaService, "perform_health_check") as mock_health:
        mock_health.return_value = {
            "status": "healthy",
            "error": None,
            "available_models": ["gemma3:4b", "test-model"],
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
            {"speaker": "B", "text": "どうも"},
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


@pytest.fixture
def mock_ollama_client():
    """Mock OllamaClient for testing."""
    mock_client = Mock(spec=OllamaClient)
    # Configure default behaviors
    mock_client.check_ollama_availability.return_value = {
        "available": True,
        "models": ["gemma3:4b", "llama2"],
        "error": None,
        "instance_type": "test",
    }
    mock_client.get_detailed_status.return_value = {
        "available": True,
        "models": ["gemma3:4b", "llama2"],
        "api_version": "0.1.0",
        "instance_type": "test",
        "base_url": "http://test:11434",
    }
    return mock_client


@pytest.fixture
def mock_prompt_loader():
    """Mock PromptLoader for testing."""
    mock_loader = Mock(spec=PromptLoader)
    mock_loader.load_template.return_value = "Test prompt template with {topic}"
    return mock_loader


def test_check_availability(ollama_service, mock_ollama_client):
    """Test check_availability method."""
    result = ollama_service.check_availability()
    assert result["available"] is True
    assert "models" in result
    assert "gemma3:4b" in result["models"]
    assert result["error"] is None
    mock_ollama_client.check_ollama_availability.assert_called_once()


def test_get_detailed_status(ollama_service, mock_ollama_client):
    """Test get_detailed_status method."""
    result = ollama_service.get_detailed_status()
    assert result["available"] is True
    assert "models" in result
    assert result["api_version"] == "0.1.0"
    mock_ollama_client.get_detailed_status.assert_called_once()


def test_perform_health_check(ollama_service, mock_ollama_client):
    """Test perform_health_check method."""
    mock_ollama_client.check_ollama_availability.return_value = {
        "available": True,
        "models": ["gemma3:4b"],
        "error": None,
    }
    result = ollama_service.perform_health_check()
    assert result["status"] == "healthy"
    assert "gemma3:4b" in result["available_models"]
    assert result["error"] is None


def test_generate_manzai_script_empty_topic(ollama_service):
    """Test script generation with empty topic."""
    with pytest.raises(ValueError, match="Topic cannot be empty"):
        ollama_service.generate_manzai_script("")


def test_generate_manzai_script_server_unavailable(ollama_service, mock_ollama_client):
    """Test script generation when server is unavailable."""
    mock_ollama_client.check_ollama_availability.return_value = {
        "available": False,
        "models": [],
        "error": "Connection refused",
    }
    with patch.object(ollama_service, "perform_health_check") as mock_health_check:
        mock_health_check.return_value = {
            "status": "unhealthy",
            "instance_type": "test",
            "available_models": [],
            "error": "Connection refused",
        }
        with pytest.raises(OllamaServiceError, match=r"Ollama server .* is not available"):
            ollama_service.generate_manzai_script("Test topic")


def test_generate_manzai_script_model_unavailable(ollama_service, mock_ollama_client):
    """Test script generation when requested model is unavailable."""
    with patch.object(ollama_service, "perform_health_check") as mock_health_check:
        mock_health_check.return_value = {
            "status": "healthy",
            "instance_type": "test",
            "available_models": ["llama2"],
            "error": None,
        }
        with pytest.raises(
            OllamaServiceError, match="Requested model 'gemma3:4b' is not available"
        ):
            ollama_service.generate_manzai_script("Test topic", "gemma3:4b")


def test_generate_manzai_script_api_error(ollama_service, mock_ollama_client, mock_prompt_loader):
    """Test script generation when API returns an error."""
    mock_ollama_client.generate_json_sync.side_effect = OllamaServiceError("API error")
    with pytest.raises(OllamaServiceError, match="API error"):
        ollama_service.generate_manzai_script("Test topic")


def test_fallback_response(ollama_service):
    """Test fallback response generation."""
    result = ollama_service.get_fallback_response("Test topic")
    assert len(result) == 2
    assert result[0].role == Role.TSUKKOMI
    assert "Test topic" in result[0].text
    assert result[1].role == Role.BOKE


def test_parse_manzai_script_string(ollama_service):
    """Test parsing manzai script from string format."""
    script_text = """
    A: こんにちは、今日は良い天気ですね。
    B: そうですね、空が青いです。
    A: ところで、最近何かありましたか？
    B: 特にないです。
    """
    result = ollama_service._parse_manzai_script(script_text)
    assert len(result) == 4
    assert result[0].role == Role.TSUKKOMI
    assert result[0].text == "こんにちは、今日は良い天気ですね。"
    assert result[1].role == Role.BOKE
    assert result[1].text == "そうですね、空が青いです。"


def test_parse_manzai_script_dict(ollama_service):
    """Test parsing manzai script from dictionary format."""
    script_dict = {
        "script": [
            {"speaker": "A", "text": "こんにちは"},
            {"speaker": "B", "text": "どうも"},
        ]
    }
    result = ollama_service._parse_manzai_script(script_dict)
    assert len(result) == 2
    assert result[0].role == Role.TSUKKOMI
    assert result[0].text == "こんにちは"
    assert result[1].role == Role.BOKE
    assert result[1].text == "どうも"


def test_parse_manzai_script_code_block(ollama_service):
    """Test parsing manzai script from text with code blocks."""
    script_text = """
    Here's your manzai script:

    ```
    A: こんにちは、今日は良い天気ですね。
    B: そうですね、空が青いです。
    ```

    Hope you enjoy it!
    """
    result = ollama_service._parse_manzai_script(script_text)
    assert len(result) == 2
    assert result[0].role == Role.TSUKKOMI
    assert result[0].text == "こんにちは、今日は良い天気ですね。"
    assert result[1].role == Role.BOKE
    assert result[1].text == "そうですね、空が青いです。"


@pytest.fixture
def mock_requests():
    """Mock the requests module."""
    with patch("src.backend.app.services.voicevox_service.requests") as mock_req:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.content = b"test audio data"
        mock_response.json.return_value = {
            "accent_phrases": [
                {"moras": [{"text": "こ", "consonant_length": 0.1, "vowel_length": 0.1}]}
            ]
        }
        mock_req.post.return_value = mock_response
        mock_req.get.return_value = mock_response
        yield mock_req


@pytest.fixture
def voicevox_service(mock_requests, tmp_path):
    """Create VoiceVoxService with mocked dependencies and temp directory."""
    audio_dir = tmp_path / "audio"
    audio_dir.mkdir()
    service = VoiceVoxService(base_url="http://test:50021")
    service.output_dir = str(audio_dir)
    return service


def test_voicevox_init():
    """Test service initialization."""
    service = VoiceVoxService(base_url="http://custom:50021")
    assert service.base_url == "http://custom:50021"
    assert os.path.exists(service.output_dir)


def test_generate_voice_success(voicevox_service, mock_requests):
    """Test successful voice generation."""
    result = voicevox_service.generate_voice("こんにちは", 1)
    assert result == b"test audio data"
    mock_requests.post.assert_called()
    assert mock_requests.post.call_count == 2
    args, kwargs = mock_requests.post.call_args_list[0]
    assert args[0].endswith("/audio_query")
    assert kwargs["params"] == {"text": "こんにちは", "speaker": 1}
    args, kwargs = mock_requests.post.call_args_list[1]
    assert args[0].endswith("/synthesis")
    assert kwargs["params"] == {"speaker": 1}


def test_generate_voice_empty_text(voicevox_service):
    """Test voice generation with empty text."""
    with pytest.raises(ValueError, match="text cannot be empty"):
        voicevox_service.generate_voice("", 1)


def test_generate_voice_invalid_speaker(voicevox_service):
    """Test voice generation with invalid speaker ID."""
    with pytest.raises(ValueError, match="invalid speaker id"):
        voicevox_service.generate_voice("こんにちは", -1)


def test_generate_voice_api_error(voicevox_service, mock_requests):
    """Test voice generation when API returns an error."""
    error_response = Mock()
    error_response.status_code = 400
    mock_requests.post.return_value = error_response
    with pytest.raises(VoiceVoxServiceError, match="VoiceVox API returned error status"):
        voicevox_service.generate_voice("こんにちは", 1)


def test_get_timing_data_success(voicevox_service, mock_requests):
    """Test successful timing data retrieval."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "accent_phrases": [
            {
                "moras": [
                    {"text": "こ", "consonant_length": 0.1, "vowel_length": 0.1},
                    {"text": "ん", "consonant_length": 0.0, "vowel_length": 0.2},
                ]
            }
        ]
    }
    mock_requests.post.return_value = mock_response
    result = voicevox_service.get_timing_data("こんにちは", 1)
    assert "accent_phrases" in result
    assert len(result["accent_phrases"]) == 1
    assert len(result["accent_phrases"][0]["moras"]) == 2
    assert result["accent_phrases"][0]["moras"][0]["text"] == "こ"
    mock_requests.post.assert_called_once()
    args, kwargs = mock_requests.post.call_args
    assert args[0].endswith("/audio_query")
    assert kwargs["params"] == {"text": "こんにちは", "speaker": 1}


def test_get_timing_data_error(voicevox_service, mock_requests):
    """Test timing data retrieval when API returns an error."""
    error_response = Mock()
    error_response.status_code = 500
    mock_requests.post.return_value = error_response
    with pytest.raises(VoiceVoxServiceError, match="VoiceVox API returned error status"):
        voicevox_service.get_timing_data("こんにちは", 1)


def test_synthesize_voice_success(voicevox_service, mock_requests, tmp_path):
    """Test successful voice synthesis with saved file."""
    mock_requests.post.return_value.json.return_value = {
        "accent_phrases": [
            {
                "moras": [
                    {"text": "こ", "consonant_length": 0.1, "vowel_length": 0.1},
                    {"text": "ん", "consonant_length": 0.0, "vowel_length": 0.2},
                ]
            }
        ]
    }
    mock_requests.post.return_value.content = b"test audio data"
    with patch("builtins.open", create=True) as mock_open:
        result = voicevox_service.synthesize_voice("こんにちは", 1)
        assert isinstance(result, AudioSynthesisResult)
        assert result.speaker_id == 1
        assert result.text == "こんにちは"
        assert len(result.timing_data) == 2
        assert isinstance(result.timing_data[0], SpeechTimingData)
        assert result.timing_data[0].text == "こ"
        assert result.timing_data[1].text == "ん"
        mock_open.assert_called()


def test_get_speakers_success(voicevox_service, mock_requests):
    """Test successful speaker list retrieval."""
    mock_requests.get.return_value.json.return_value = [
        {
            "name": "四国めたん",
            "speaker_uuid": "uuid1",
            "styles": [{"id": 2, "name": "ノーマル"}],
        },
        {
            "name": "ずんだもん",
            "speaker_uuid": "uuid2",
            "styles": [{"id": 3, "name": "ノーマル"}, {"id": 4, "name": "あまあま"}],
        },
    ]
    result = voicevox_service.get_speakers()
    assert len(result) == 2
    assert result[0]["name"] == "四国めたん"
    assert len(result[0]["styles"]) == 1
    assert result[1]["name"] == "ずんだもん"
    assert len(result[1]["styles"]) == 2
    mock_requests.get.assert_called_once()
    assert mock_requests.get.call_args[0][0].endswith("/speakers")


def test_list_speakers_success(voicevox_service, mock_requests):
    """Test successful speaker list conversion to model objects."""
    mock_requests.get.return_value.json.return_value = [
        {
            "name": "四国めたん",
            "speaker_uuid": "uuid1",
            "styles": [{"id": 2, "name": "ノーマル"}],
        },
        {
            "name": "ずんだもん",
            "speaker_uuid": "uuid2",
            "styles": [{"id": 3, "name": "ノーマル"}, {"id": 4, "name": "あまあま"}],
        },
    ]
    result = voicevox_service.list_speakers()
    assert len(result) == 3
    assert isinstance(result[0], VoiceVoxSpeaker)
    assert result[0].id == 2
    assert result[0].name == "四国めたん"
    assert result[0].style_id == 2
    assert result[0].style_name == "ノーマル"
    assert result[1].id == 3
    assert result[1].name == "ずんだもん"
    assert result[1].style_id == 3
    assert result[2].id == 4
    assert result[2].name == "ずんだもん"
    assert result[2].style_id == 4
    assert result[2].style_name == "あまあま"


def test_list_speakers_error(voicevox_service, mock_requests):
    """Test speaker list retrieval when API returns an error."""
    mock_requests.get.side_effect = Exception("Connection error")
    with pytest.raises(VoiceVoxServiceError):
        voicevox_service.list_speakers()


def test_check_availability_success(voicevox_service, mock_requests):
    """Test successful availability check."""
    mock_requests.get.return_value.text = "0.14.0"
    with patch.object(voicevox_service, "list_speakers") as mock_list_speakers:
        mock_list_speakers.return_value = [
            VoiceVoxSpeaker(id=1, name="Speaker1", style_id=1, style_name="Style1"),
            VoiceVoxSpeaker(id=2, name="Speaker2", style_id=2, style_name="Style2"),
        ]
        result = voicevox_service.check_availability()
        assert result["available"] is True
        assert result["speakers"] == 2
        assert result["version"] == "0.14.0"
        assert result["error"] is None
        assert result["response_time_ms"] > 0


def test_check_availability_error(voicevox_service, mock_requests):
    """Test availability check when API is unavailable."""
    mock_requests.get.side_effect = Exception("Connection error")
    result = voicevox_service.check_availability()
    assert result["available"] is False
    assert result["speakers"] == 0
    assert result["error"] is not None
    assert "Connection error" in result["error"]


def test_voicevox_get_detailed_status(voicevox_service):
    """Test detailed status information retrieval."""
    with patch.object(voicevox_service, "check_availability") as mock_check:
        mock_check.return_value = {
            "available": True,
            "speakers": 5,
            "version": "0.14.0",
            "error": None,
            "response_time_ms": 123,
        }
        result = voicevox_service.get_detailed_status()
        assert result["base_url"] == "http://test:50021"
        assert result["available"] is True
        assert result["speakers_count"] == 5
        assert result["version"] == "0.14.0"
        assert result["error"] is None
        assert result["response_time_ms"] == 123


def test_synthesize_alias(voicevox_service):
    """Test synthesize method as an alias for generate_voice."""
    with patch.object(voicevox_service, "generate_voice") as mock_generate:
        mock_generate.return_value = b"test audio data"
        result = voicevox_service.synthesize("こんにちは", 1)
        mock_generate.assert_called_once_with("こんにちは", 1)
        assert result == b"test audio data"


def test_get_fallback_audio(voicevox_service):
    """Test fallback audio generation."""
    result = voicevox_service.get_fallback_audio("テスト")
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert len(result) > 44  # Should be a valid WAV structure
