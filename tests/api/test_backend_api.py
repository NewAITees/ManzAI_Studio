"""Backend API tests."""
import pytest
from unittest.mock import patch, MagicMock
import os
import io
from flask import Flask
from flask.testing import FlaskClient

from src.backend.app.services.ollama_service import OllamaService
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.services.audio_manager import AudioManager


@pytest.fixture
def app():
    """Create Flask application for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


def test_health_endpoint(client: FlaskClient) -> None:
    """Test health endpoint returns healthy status."""
    response = client.get("/api/health")
    
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_generate_endpoint_valid_topic(client: FlaskClient) -> None:
    """Test generate endpoint with valid topic returns proper response."""
    mock_script_data = {
        "script": [
            {"role": "tsukkomi", "text": "こんにちは！"},
            {"role": "boke", "text": "どうもどうも！"}
        ]
    }
    
    mock_audio_path = "test_audio_path.wav"
    
    # Ollamaサービスのモック
    with patch.object(OllamaService, "generate_manzai_script", return_value=mock_script_data):
        # VoiceVoxサービスのモック
        with patch.object(VoiceVoxService, "generate_voice", return_value=b"test_audio_data"):
            # AudioManagerのモック
            with patch.object(AudioManager, "save_audio", return_value=mock_audio_path):
                response = client.post("/api/generate", json={"topic": "テスト"})
                
                assert response.status_code == 200
                assert "script" in response.json
                assert "audio_data" in response.json
                assert len(response.json["script"]) == 2
                assert len(response.json["audio_data"]) == 2


def test_generate_endpoint_missing_topic(client: FlaskClient) -> None:
    """Test generate endpoint with missing topic returns 400 error."""
    response = client.post("/api/generate", json={})
    
    assert response.status_code == 400
    assert "error" in response.json
    assert "No topic provided" in response.json["error"]


def test_generate_endpoint_empty_topic(client: FlaskClient) -> None:
    """Test generate endpoint with empty topic returns 400 error."""
    response = client.post("/api/generate", json={"topic": ""})
    
    assert response.status_code == 400
    assert "error" in response.json
    assert "Topic cannot be empty" in response.json["error"]


def test_generate_endpoint_invalid_content_type(client: FlaskClient) -> None:
    """Test generate endpoint with invalid content type returns 415 error."""
    response = client.post("/api/generate", data="invalid data")
    
    assert response.status_code == 415
    assert "error" in response.json
    assert "Content-Type" in response.json["error"]


def test_audio_endpoint_file_found(client: FlaskClient) -> None:
    """Test audio endpoint with existing file returns audio file."""
    mock_audio_data = b"test_audio_data"
    filename = "test_audio.wav"
    
    # AudioManagerのget_audioメソッドをモック
    with patch.object(AudioManager, "get_audio", return_value=mock_audio_data):
        # send_fileをモック - 正しいモジュールパスを使用
        with patch("src.backend.app.routes.api.send_file", return_value=mock_audio_data) as mock_send_file:
            response = client.get(f"/api/audio/{filename}")
            
            # send_fileが呼ばれたことを確認
            assert mock_send_file.called
            

def test_audio_endpoint_file_not_found(client: FlaskClient) -> None:
    """Test audio endpoint with non-existing file returns 404 error."""
    filename = "nonexistent.wav"
    
    # AudioManagerのget_audioメソッドが例外を発生させるようにモック
    with patch.object(AudioManager, "get_audio", side_effect=FileNotFoundError):
        response = client.get(f"/api/audio/{filename}")
        
        assert response.status_code == 404
        assert "error" in response.json
        assert "Audio file not found" in response.json["error"] 