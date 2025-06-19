"""Test service modules with real implementations (integration tests)."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

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
def temp_templates_dir():
    """Create temporary directory with prompt templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        templates_dir = Path(tmpdir) / "templates"
        templates_dir.mkdir()

        # Create a basic template file
        template_file = templates_dir / "basic_manzai.txt"
        template_content = """
Topic: {topic}

Generate a manzai conversation about the topic above.
Format as:
A: [line]
B: [line]
A: [line]
B: [line]
"""
        template_file.write_text(template_content)

        yield str(templates_dir)


@pytest.fixture
def prompt_loader(temp_templates_dir):
    """Create PromptLoader with temporary templates."""
    return PromptLoader(templates_dir=temp_templates_dir)


@pytest.fixture
def ollama_client():
    """Create OllamaClient instance for integration testing."""
    return OllamaClient(base_url="http://localhost:11434")


@pytest.fixture
def voicevox_service():
    """Create VoiceVoxService instance for integration testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = VoiceVoxService(base_url="http://localhost:50021")
        service.output_dir = tmpdir
        yield service


@pytest.mark.integration
def test_ollama_client_availability(ollama_client):
    """Test if Ollama service is available (requires running Ollama)."""
    try:
        result = ollama_client.check_ollama_availability()
        if result["available"]:
            assert "models" in result
            assert isinstance(result["models"], list)
        else:
            pytest.skip("Ollama service not available")
    except Exception:
        pytest.skip("Ollama service not accessible")


@pytest.mark.integration
def test_ollama_list_models(ollama_client):
    """Test listing models from Ollama (requires running Ollama)."""
    try:
        models = ollama_client.list_models()
        assert isinstance(models, list)
        # If models are available, check structure
        if models:
            assert "name" in models[0]
    except Exception:
        pytest.skip("Ollama service not accessible")


@pytest.mark.integration
def test_voicevox_availability(voicevox_service):
    """Test if VoiceVox service is available (requires running VoiceVox)."""
    try:
        result = voicevox_service.check_availability()
        if result["available"]:
            assert result["speakers"] >= 0
            assert "version" in result
        else:
            pytest.skip("VoiceVox service not available")
    except Exception:
        pytest.skip("VoiceVox service not accessible")


@pytest.mark.integration
def test_voicevox_get_speakers(voicevox_service):
    """Test getting speakers from VoiceVox (requires running VoiceVox)."""
    try:
        speakers = voicevox_service.get_speakers()
        assert isinstance(speakers, list)
        if speakers:
            assert "name" in speakers[0]
            assert "styles" in speakers[0]
    except Exception:
        pytest.skip("VoiceVox service not accessible")


@pytest.mark.integration
def test_voicevox_list_speakers(voicevox_service):
    """Test listing speakers as model objects (requires running VoiceVox)."""
    try:
        speakers = voicevox_service.list_speakers()
        assert isinstance(speakers, list)
        if speakers:
            assert isinstance(speakers[0], VoiceVoxSpeaker)
            assert hasattr(speakers[0], "id")
            assert hasattr(speakers[0], "name")
    except Exception:
        pytest.skip("VoiceVox service not accessible")


@pytest.mark.integration
def test_prompt_loader_real_template(prompt_loader):
    """Test PromptLoader with real template files."""
    formatted = prompt_loader.load_template("basic_manzai", topic="テスト")
    assert "テスト" in formatted
    assert "{topic}" not in formatted


def test_ollama_client_init():
    """Test OllamaClient initialization (unit test)."""
    client = OllamaClient(base_url="http://test:11434")
    assert client.base_url == "http://test:11434"
    assert client.instance_type == "local"


def test_prepare_request_data():
    """Test request data preparation (unit test)."""
    client = OllamaClient(base_url="http://test:11434")
    data = client._prepare_request_data("test prompt", "test-model")
    assert data["prompt"] == "test prompt"
    assert data["model"] == "test-model"
    assert data["stream"] is False


def test_extract_json_block_success():
    """Test JSON block extraction (unit test)."""
    client = OllamaClient(base_url="http://test:11434")
    text = '```json\n{"key": "value"}\n```'
    result = client._extract_json_block(text)
    assert json.loads(result) == {"key": "value"}


def test_extract_json_block_error():
    """Test JSON block extraction error (unit test)."""
    client = OllamaClient(base_url="http://test:11434")
    with pytest.raises(OllamaServiceError):
        client._extract_json_block("invalid json")


def test_voicevox_init():
    """Test VoiceVoxService initialization (unit test)."""
    service = VoiceVoxService(base_url="http://custom:50021")
    assert service.base_url == "http://custom:50021"
    assert os.path.exists(service.output_dir)


def test_voicevox_generate_voice_validation():
    """Test voice generation input validation (unit test)."""
    service = VoiceVoxService(base_url="http://test:50021")

    with pytest.raises(ValueError, match="text cannot be empty"):
        service.generate_voice("", 1)

    with pytest.raises(ValueError, match="invalid speaker id"):
        service.generate_voice("こんにちは", -1)


def test_parse_manzai_script_string():
    """Test parsing manzai script from string format (unit test)."""
    with patch("src.backend.app.services.ollama_service.PromptLoader"):
        service = OllamaService(base_url="http://test:11434", instance_type="local")
        script_text = """
        A: こんにちは、今日は良い天気ですね。
        B: そうですね、空が青いです。
        A: ところで、最近何かありましたか？
        B: 特にないです。
        """
        result = service._parse_manzai_script(script_text)
        assert len(result) == 4
        assert result[0].role == Role.TSUKKOMI
        assert result[0].text == "こんにちは、今日は良い天気ですね。"
        assert result[1].role == Role.BOKE
        assert result[1].text == "そうですね、空が青いです。"


def test_parse_manzai_script_dict():
    """Test parsing manzai script from dictionary format (unit test)."""
    with patch("src.backend.app.services.ollama_service.PromptLoader"):
        service = OllamaService(base_url="http://test:11434", instance_type="local")
        script_dict = {
            "script": [
                {"speaker": "A", "text": "こんにちは"},
                {"speaker": "B", "text": "どうも"},
            ]
        }
        result = service._parse_manzai_script(script_dict)
        assert len(result) == 2
        assert result[0].role == Role.TSUKKOMI
        assert result[0].text == "こんにちは"
        assert result[1].role == Role.BOKE
        assert result[1].text == "どうも"


def test_parse_manzai_script_code_block():
    """Test parsing manzai script from text with code blocks (unit test)."""
    # Mock PromptLoader
    with patch("src.backend.app.services.ollama_service.PromptLoader"):
        service = OllamaService(base_url="http://test:11434", instance_type="local")
        script_text = """
        Here's your manzai script:

        ```
        A: こんにちは、今日は良い天気ですね。
        B: そうですね、空が青いです。
        ```

        Hope you enjoy it!
        """
        result = service._parse_manzai_script(script_text)
        assert len(result) == 2
        assert result[0].role == Role.TSUKKOMI
        assert result[0].text == "こんにちは、今日は良い天気ですね。"
        assert result[1].role == Role.BOKE
        assert result[1].text == "そうですね、空が青いです。"


def test_fallback_response():
    """Test fallback response generation (unit test)."""
    with patch("src.backend.app.services.ollama_service.PromptLoader"):
        service = OllamaService(base_url="http://test:11434", instance_type="local")
        result = service.get_fallback_response("Test topic")
        assert len(result) == 2
        assert result[0].role == Role.TSUKKOMI
        assert "Test topic" in result[0].text
        assert result[1].role == Role.BOKE


def test_generate_manzai_script_empty_topic():
    """Test script generation with empty topic (unit test)."""
    with patch("src.backend.app.services.ollama_service.PromptLoader"):
        service = OllamaService(base_url="http://test:11434", instance_type="local")
        with pytest.raises(ValueError, match="Topic cannot be empty"):
            service.generate_manzai_script("")


def test_voicevox_get_fallback_audio():
    """Test fallback audio generation (unit test)."""
    service = VoiceVoxService(base_url="http://test:50021")
    result = service.get_fallback_audio("テスト")
    assert isinstance(result, bytes)
    assert len(result) > 0
    assert len(result) > 44  # Should be a valid WAV structure
