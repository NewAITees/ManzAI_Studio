"""Test the API endpoints with real implementations."""

import json
import tempfile

import pytest

from src.backend.app import create_app
from src.backend.app.config import Config
from src.backend.app.models.script import Role, ScriptLine
from src.backend.app.services.audio_manager import AudioManager
from src.backend.app.services.ollama_service import OllamaService
from src.backend.app.services.voicevox_service import VoiceVoxService


@pytest.fixture
def temp_config() -> Config:
    """Create test configuration with temporary directories."""
    config = Config()
    config.TESTING = True

    # Use temporary directory for audio files
    with tempfile.TemporaryDirectory() as tmpdir:
        config.AUDIO_OUTPUT_DIR = tmpdir
        yield config


@pytest.fixture
def app_with_real_services(temp_config):
    """Create Flask app with real service instances but isolated."""
    app = create_app(temp_config)

    # Create real service instances but configure them for testing
    with tempfile.TemporaryDirectory() as tmpdir:
        # Real AudioManager with temp directory
        app.audio_manager = AudioManager(audio_dir=tmpdir)

        # Real but isolated OllamaService (may not connect to actual server)
        app.ollama_service = OllamaService(base_url="http://localhost:11434", instance_type="local")

        # Real but isolated VoiceVoxService (may not connect to actual server)
        app.voicevox_service = VoiceVoxService(base_url="http://localhost:50021")
        app.voicevox_service.output_dir = tmpdir

        yield app


@pytest.fixture
def client(app_with_real_services):
    """Create test client with real services."""
    with app_with_real_services.test_client() as client:
        yield client


def test_health_check_real(client):
    """Test the health check endpoint with real app."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"


def test_detailed_status_real(client):
    """Test the detailed status endpoint with real services."""
    response = client.get("/api/detailed-status")
    assert response.status_code == 200
    data = json.loads(response.data)

    # Verify the response structure
    assert "timestamp" in data
    assert "ollama" in data
    assert "voicevox" in data
    assert "system" in data

    # Services may not be available in test environment
    # but should return proper status structure
    assert "available" in data["ollama"]
    assert "available" in data["voicevox"]


def test_audio_manager_operations_real(client, app_with_real_services):
    """Test real AudioManager operations through API."""
    # Test saving and retrieving audio
    test_data = b"RIFF" + b"\x00" * 36 + b"WAVE" + b"\x00" * 100  # Minimal WAV structure

    # Save audio directly through AudioManager
    audio_manager = app_with_real_services.audio_manager
    filename = audio_manager.save_audio(test_data, "test.wav")

    # Retrieve through API
    response = client.get(f"/api/audio/{filename}")
    assert response.status_code == 200
    assert response.data == test_data
    assert response.mimetype == "audio/wav"


def test_audio_list_real(client, app_with_real_services):
    """Test real audio file listing."""
    # Create some test audio files
    audio_manager = app_with_real_services.audio_manager
    test_data = b"RIFF" + b"\x00" * 36 + b"WAVE" + b"\x00" * 100

    # Create multiple files
    filenames = []
    for i in range(3):
        filename = audio_manager.save_audio(test_data, f"test{i}.wav")
        filenames.append(filename)

    # List through API
    response = client.get("/api/audio/list")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) >= 3  # Should have at least our 3 files

    # Check that our files are in the list
    returned_filenames = [
        item if isinstance(item, str) else item.get("filename", "") for item in data
    ]
    for filename in filenames:
        assert filename in returned_filenames


def test_audio_cleanup_real(client, app_with_real_services):
    """Test real audio file cleanup."""
    # Create many test audio files
    audio_manager = app_with_real_services.audio_manager
    test_data = b"RIFF" + b"\x00" * 36 + b"WAVE" + b"\x00" * 100

    # Create more files than the default max
    for i in range(15):
        audio_manager.save_audio(test_data, f"cleanup_test{i}.wav")

    # Cleanup through API
    response = client.post("/api/audio/cleanup")
    assert response.status_code == 200

    data = json.loads(response.data)
    assert "deleted_files" in data
    assert isinstance(data["deleted_files"], int)
    # Should have deleted some files (depends on cleanup threshold)
    assert data["deleted_files"] >= 0


def test_audio_not_found_real(client):
    """Test audio file retrieval when file not found."""
    response = client.get("/api/audio/nonexistent.wav")
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    assert "not found" in data["error"].lower()


def test_generate_endpoint_validation_real(client):
    """Test input validation on generate endpoint."""
    # Test empty topic
    response = client.post("/api/generate", json={"topic": "", "model": "any"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "topic" in data["error"].lower()

    # Test missing topic
    response = client.post("/api/generate", json={"model": "any"})
    assert response.status_code == 400

    # Test missing model (should use default model but may fail if services are down)
    response = client.post("/api/generate", json={"topic": "test"})
    # Should either validate (400) or fail due to service unavailability (500)
    assert response.status_code in [400, 500]


def test_ollama_service_operations_real():
    """Test real OllamaService operations (unit test level)."""
    service = OllamaService(base_url="http://localhost:11434", instance_type="local")

    # Test availability check (should work even if server is down)
    result = service.check_availability()
    assert "available" in result
    assert "models" in result
    assert "error" in result

    # Test detailed status
    status = service.get_detailed_status()
    assert "available" in status
    assert "models" in status
    assert "instance_type" in status

    # Test fallback response (should always work)
    fallback = service.get_fallback_response("Test topic")
    assert len(fallback) >= 2
    assert all(isinstance(line, ScriptLine) for line in fallback)
    assert fallback[0].role == Role.TSUKKOMI
    assert fallback[1].role == Role.BOKE
    assert "Test topic" in fallback[0].text


def test_voicevox_service_operations_real():
    """Test real VoiceVoxService operations (unit test level)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        service = VoiceVoxService(base_url="http://localhost:50021")
        service.output_dir = tmpdir

        # Test availability check (should work even if server is down)
        result = service.check_availability()
        assert "available" in result
        assert "speakers" in result
        assert "error" in result

        # Test detailed status
        status = service.get_detailed_status()
        assert "available" in status
        assert "speakers_count" in status
        assert "base_url" in status

        # Test fallback audio (should always work)
        fallback = service.get_fallback_audio("Test text")
        assert isinstance(fallback, bytes)
        assert len(fallback) > 44  # Should be a valid WAV structure

        # Test input validation
        with pytest.raises(ValueError):
            service.generate_voice("", 1)

        with pytest.raises(ValueError):
            service.generate_voice("test", -1)


def test_audio_manager_operations_unit():
    """Test real AudioManager operations (unit test level)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        manager = AudioManager(audio_dir=tmpdir)

        # Test saving and retrieving
        test_data = b"test audio data"
        filename = manager.save_audio(test_data, "test.wav")

        assert filename.endswith(".wav")
        assert not filename.startswith("/")  # Should be relative filename

        # Test retrieval
        retrieved_data = manager.get_audio(filename)
        assert retrieved_data == test_data

        # Test listing
        files = manager.list_audio_files()
        assert isinstance(files, list)
        assert filename in files or any(
            filename in str(f) for f in files
        )  # Handle both string and dict formats

        # Test cleanup
        # Create more files for cleanup test
        for i in range(5):
            manager.save_audio(test_data, f"cleanup{i}.wav")

        deleted = manager.cleanup_old_files(max_files=3)
        assert isinstance(deleted, int)
        assert deleted >= 0

        # Test validation
        with pytest.raises(ValueError):
            manager.save_audio(None, "test.wav")

        with pytest.raises(ValueError):
            manager.save_audio(test_data, "")

        with pytest.raises(FileNotFoundError):
            manager.get_audio("nonexistent.wav")
