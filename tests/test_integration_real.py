"""Real integration tests for ManzAI Studio."""

import json
import os
import tempfile

import pytest
import requests

from src.backend.app import create_app
from src.backend.app.config import Config


def check_service_availability(url: str, timeout: int = 2) -> bool:
    """Check if a service is available."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="module")
def services_available() -> dict:
    """Check which external services are available."""
    return {
        "ollama": check_service_availability("http://localhost:11434"),
        "voicevox": check_service_availability("http://localhost:50021"),
    }


@pytest.fixture
def real_app(services_available) -> object:
    """Create Flask app with real services if available."""
    if not (services_available["ollama"] and services_available["voicevox"]):
        pytest.skip("External services not available for integration test")

    # Create temporary directory for audio files
    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config()
        config.AUDIO_OUTPUT_DIR = tmpdir
        config.TESTING = True

        app = create_app(config)

        # Verify services are actually working
        try:
            with app.test_client() as client:
                health_response = client.get("/api/detailed-status")
                if health_response.status_code != 200:
                    pytest.skip("App health check failed")

                health_data = json.loads(health_response.data)
                if not (
                    health_data.get("ollama", {}).get("available")
                    and health_data.get("voicevox", {}).get("available")
                ):
                    pytest.skip("Services not properly initialized")
        except Exception:
            pytest.skip("Failed to initialize app with real services")

        yield app


@pytest.fixture
def client(real_app):
    """Create test client with real services."""
    with real_app.test_client() as client:
        yield client


@pytest.mark.integration
def test_real_health_check(client):
    """Test health check with real services."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"


@pytest.mark.integration
def test_real_detailed_status(client):
    """Test detailed status with real services."""
    response = client.get("/api/detailed-status")
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify response structure
    assert "timestamp" in data
    assert "ollama" in data
    assert "voicevox" in data
    assert "system" in data

    # Verify services are available
    assert data["ollama"]["available"] is True
    assert data["voicevox"]["available"] is True

    # Verify ollama has models
    assert "models" in data["ollama"]
    assert len(data["ollama"]["models"]) > 0

    # Verify voicevox has speakers
    assert data["voicevox"]["speakers_count"] > 0


@pytest.mark.integration
def test_real_get_speakers(client):
    """Test getting real VoiceVox speakers."""
    response = client.get("/api/speakers")
    assert response.status_code == 200
    data = json.loads(response.data)

    # Should have at least one speaker
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]
    assert "style_id" in data[0]
    assert "style_name" in data[0]


@pytest.mark.integration
def test_real_script_generation_simple(client):
    """Test real script generation with a simple topic."""
    # Use a simple topic that should work well
    topic = "天気"

    # Try to get available models first
    status_response = client.get("/api/detailed-status")
    status_data = json.loads(status_response.data)
    available_models = status_data["ollama"]["models"]

    if not available_models:
        pytest.skip("No Ollama models available")

    # Use the first available model
    model = available_models[0]

    response = client.post("/api/generate", json={"topic": topic, "model": model})

    # Should generate successfully
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify script structure
    assert "script" in data
    assert len(data["script"]) >= 2  # At least 2 lines

    # Check each script line
    for line in data["script"]:
        assert "role" in line
        assert "text" in line
        assert "audio_file" in line
        assert line["role"] in ["TSUKKOMI", "BOKE"]
        assert len(line["text"]) > 0
        assert line["audio_file"].endswith(".wav")


@pytest.mark.integration
def test_real_audio_retrieval(client):
    """Test retrieving real generated audio files."""
    # First generate a script to create audio files
    topic = "簡単なテスト"

    status_response = client.get("/api/detailed-status")
    status_data = json.loads(status_response.data)
    available_models = status_data["ollama"]["models"]

    if not available_models:
        pytest.skip("No Ollama models available")

    model = available_models[0]

    # Generate script
    generate_response = client.post("/api/generate", json={"topic": topic, "model": model})
    assert generate_response.status_code == 200

    generate_data = json.loads(generate_response.data)
    audio_file = generate_data["script"][0]["audio_file"]

    # Try to retrieve the audio file
    audio_response = client.get(f"/api/audio/{audio_file}")
    assert audio_response.status_code == 200
    assert audio_response.mimetype == "audio/wav"
    assert len(audio_response.data) > 44  # Should be a valid WAV file


@pytest.mark.integration
def test_real_audio_list(client):
    """Test listing real audio files."""
    # First generate a script to create audio files
    topic = "リストテスト"

    status_response = client.get("/api/detailed-status")
    status_data = json.loads(status_response.data)
    available_models = status_data["ollama"]["models"]

    if not available_models:
        pytest.skip("No Ollama models available")

    model = available_models[0]

    # Generate script to create audio files
    generate_response = client.post("/api/generate", json={"topic": topic, "model": model})
    assert generate_response.status_code == 200

    # List audio files
    list_response = client.get("/api/audio/list")
    assert list_response.status_code == 200

    data = json.loads(list_response.data)
    assert isinstance(data, list)
    # Should have at least the files we just created
    assert len(data) >= 1


@pytest.mark.integration
def test_real_audio_cleanup(client):
    """Test real audio file cleanup."""
    # Generate some audio files first
    topic = "クリーンアップテスト"

    status_response = client.get("/api/detailed-status")
    status_data = json.loads(status_response.data)
    available_models = status_data["ollama"]["models"]

    if not available_models:
        pytest.skip("No Ollama models available")

    model = available_models[0]

    # Generate script to create audio files
    generate_response = client.post("/api/generate", json={"topic": topic, "model": model})
    assert generate_response.status_code == 200

    # Cleanup files
    cleanup_response = client.post("/api/audio/cleanup")
    assert cleanup_response.status_code == 200

    data = json.loads(cleanup_response.data)
    assert "deleted_files" in data
    assert isinstance(data["deleted_files"], int)
    assert data["deleted_files"] >= 0


@pytest.mark.integration
def test_real_error_handling(client):
    """Test error handling with real services."""
    # Test with empty topic
    response = client.post("/api/generate", json={"topic": "", "model": "any"})
    assert response.status_code == 400

    # Test with non-existent model
    response = client.post("/api/generate", json={"topic": "テスト", "model": "nonexistent-model"})
    assert response.status_code == 500  # Should handle model not found

    # Test with non-existent audio file
    response = client.get("/api/audio/nonexistent.wav")
    assert response.status_code == 404


# Unit tests that don't require external services
def test_config_defaults():
    """Test that configuration has sensible defaults."""
    config = Config()
    assert hasattr(config, "OLLAMA_URL")
    assert hasattr(config, "VOICEVOX_URL")
    assert hasattr(config, "AUDIO_OUTPUT_DIR")


def test_app_creation_without_services():
    """Test that app can be created even without external services."""
    config = Config()
    config.TESTING = True

    app = create_app(config)
    assert app is not None
    assert app.config["TESTING"] is True
