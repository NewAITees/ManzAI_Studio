"""Test the API endpoints."""

import json
from unittest.mock import MagicMock

import pytest

# Import the relevant components
from src.backend.app import create_app
from src.backend.app.config import TestConfig
from src.backend.app.models.script import Role, ScriptLine
from src.backend.app.services.audio_manager import AudioManager
from src.backend.app.services.ollama_service import OllamaService, OllamaServiceError
from src.backend.app.services.voicevox_service import (
    VoiceVoxService,
    VoiceVoxServiceError,
)


@pytest.fixture
def app_with_mocks():
    """Create Flask app with mocked services."""
    # Create mock services
    mock_ollama = MagicMock(spec=OllamaService)
    mock_voicevox = MagicMock(spec=VoiceVoxService)
    mock_audio_manager = MagicMock(spec=AudioManager)

    # Configure default behaviors
    mock_ollama.check_availability.return_value = {
        "available": True,
        "models": ["gemma3:4b"],
    }
    mock_ollama.get_detailed_status.return_value = {
        "available": True,
        "models": ["gemma3:4b"],
        "instance_type": "test",
    }
    mock_voicevox.check_availability.return_value = {"available": True, "speakers": 5}
    mock_voicevox.get_detailed_status.return_value = {
        "available": True,
        "speakers_count": 5,
        "version": "0.14.0",
    }

    # Create app with test config
    app = create_app(TestConfig())

    # Replace services with mocks
    app.ollama_service = mock_ollama
    app.voicevox_service = mock_voicevox
    app.audio_manager = mock_audio_manager

    return app, mock_ollama, mock_voicevox, mock_audio_manager


@pytest.fixture
def client(app_with_mocks):
    """Create test client."""
    app, _, _, _ = app_with_mocks
    with app.test_client() as client:
        yield client


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"


def test_detailed_status(client, app_with_mocks):
    """Test the detailed status endpoint."""
    _, mock_ollama, mock_voicevox, _ = app_with_mocks

    # Call endpoint
    response = client.get("/api/detailed-status")

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the response structure
    assert "timestamp" in data
    assert "ollama" in data
    assert "voicevox" in data
    assert "system" in data

    # Check that services were called
    mock_ollama.get_detailed_status.assert_called_once()
    mock_voicevox.get_detailed_status.assert_called_once()


def test_generate_endpoint_success(client, app_with_mocks):
    """Test successful script generation endpoint."""
    _, mock_ollama, mock_voicevox, mock_audio_manager = app_with_mocks

    # Configure mocks for successful generation
    mock_script = [
        ScriptLine(role=Role.TSUKKOMI, text="こんにちは"),
        ScriptLine(role=Role.BOKE, text="どうも"),
    ]
    mock_ollama.generate_manzai_script.return_value = mock_script
    mock_voicevox.synthesize_voice.side_effect = [b"audio1", b"audio2"]
    mock_audio_manager.save_audio.side_effect = ["audio1.wav", "audio2.wav"]

    # Call endpoint
    response = client.post("/api/generate", json={"topic": "テスト", "model": "gemma3:4b"})

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify response structure
    assert "script" in data
    assert len(data["script"]) == 2
    assert data["script"][0]["role"] == "TSUKKOMI"
    assert data["script"][0]["text"] == "こんにちは"
    assert data["script"][0]["audio_file"] == "audio1.wav"

    # Verify service calls
    mock_ollama.generate_manzai_script.assert_called_once_with("テスト", "gemma3:4b")
    assert mock_voicevox.synthesize_voice.call_count == 2
    assert mock_audio_manager.save_audio.call_count == 2


def test_generate_endpoint_empty_topic(client):
    """Test script generation with empty topic."""
    response = client.post("/api/generate", json={"topic": "", "model": "gemma3:4b"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "topic" in data["error"]


def test_generate_endpoint_ollama_error(client, app_with_mocks):
    """Test script generation when Ollama service fails."""
    _, mock_ollama, _, _ = app_with_mocks

    # Configure mock to raise error
    mock_ollama.generate_manzai_script.side_effect = OllamaServiceError("Test error")

    # Call endpoint
    response = client.post("/api/generate", json={"topic": "テスト", "model": "gemma3:4b"})

    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Test error" in data["error"]


def test_generate_endpoint_voicevox_error(client, app_with_mocks):
    """Test script generation when VoiceVox service fails."""
    _, mock_ollama, mock_voicevox, _ = app_with_mocks

    # Configure mocks
    mock_script = [
        ScriptLine(role=Role.TSUKKOMI, text="こんにちは"),
        ScriptLine(role=Role.BOKE, text="どうも"),
    ]
    mock_ollama.generate_manzai_script.return_value = mock_script
    mock_voicevox.synthesize_voice.side_effect = VoiceVoxServiceError("Test error")

    # Call endpoint
    response = client.post("/api/generate", json={"topic": "テスト", "model": "gemma3:4b"})

    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Test error" in data["error"]


def test_get_audio_success(client, app_with_mocks):
    """Test successful audio file retrieval."""
    _, _, _, mock_audio_manager = app_with_mocks

    # Configure mock
    mock_audio_manager.get_audio.return_value = b"test audio data"

    # Call endpoint
    response = client.get("/api/audio/test.wav")

    # Check response
    assert response.status_code == 200
    assert response.data == b"test audio data"
    assert response.mimetype == "audio/wav"

    # Verify service call
    mock_audio_manager.get_audio.assert_called_once_with("test.wav")


def test_get_audio_not_found(client, app_with_mocks):
    """Test audio file retrieval when file not found."""
    _, _, _, mock_audio_manager = app_with_mocks

    # Configure mock to raise error
    mock_audio_manager.get_audio.side_effect = FileNotFoundError("File not found")

    # Call endpoint
    response = client.get("/api/audio/nonexistent.wav")

    # Check response
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_list_audio_files(client, app_with_mocks):
    """Test listing audio files endpoint."""
    _, _, _, mock_audio_manager = app_with_mocks

    # Configure mock
    mock_audio_manager.list_audio_files.return_value = [
        {"filename": "test1.wav", "created_at": "2024-03-20T12:00:00"},
        {"filename": "test2.wav", "created_at": "2024-03-20T12:01:00"},
    ]

    # Call endpoint
    response = client.get("/api/audio/list")

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]["filename"] == "test1.wav"
    assert data[1]["filename"] == "test2.wav"

    # Verify service call
    mock_audio_manager.list_audio_files.assert_called_once()


def test_cleanup_audio_files(client, app_with_mocks):
    """Test audio file cleanup endpoint."""
    _, _, _, mock_audio_manager = app_with_mocks

    # Configure mock
    mock_audio_manager.cleanup_old_files.return_value = 2

    # Call endpoint
    response = client.post("/api/audio/cleanup")

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["deleted_files"] == 2

    # Verify service call
    mock_audio_manager.cleanup_old_files.assert_called_once()


def test_get_speakers(client, app_with_mocks):
    """Test getting available VoiceVox speakers."""
    _, _, mock_voicevox, _ = app_with_mocks

    # Configure mock
    mock_voicevox.list_speakers.return_value = [
        {"id": 1, "name": "Speaker1", "style_id": 1, "style_name": "Style1"},
        {"id": 2, "name": "Speaker2", "style_id": 2, "style_name": "Style2"},
    ]

    # Call endpoint
    response = client.get("/api/speakers")

    # Check response
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    assert data[0]["id"] == 1
    assert data[0]["name"] == "Speaker1"
    assert data[1]["id"] == 2
    assert data[1]["name"] == "Speaker2"

    # Verify service call
    mock_voicevox.list_speakers.assert_called_once()


def test_get_speakers_error(client, app_with_mocks):
    """Test getting speakers when service fails."""
    _, _, mock_voicevox, _ = app_with_mocks

    # Configure mock to raise error
    mock_voicevox.list_speakers.side_effect = VoiceVoxServiceError("Test error")

    # Call endpoint
    response = client.get("/api/speakers")

    # Check response
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "Test error" in data["error"]
