"""Integration tests for ManzAI Studio."""
import pytest
import os
import json
import time
from unittest.mock import patch, MagicMock

from src.backend.app import create_app, init_testing_mode
from src.backend.app.config import TestConfig
from src.backend.app.services.ollama_service import OllamaService
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.models.script import ScriptLine, Role


@pytest.fixture(scope="module")
def mock_ollama_responses():
    """Prepare mock responses for Ollama service."""
    return {
        "script_response": {
            "script": [
                {"speaker": "A", "text": "今日は何について話しましょうか？"},
                {"speaker": "B", "text": "テストについて話しましょう！"},
                {"speaker": "A", "text": "なるほど、テストですか。どんなテストですか？"},
                {"speaker": "B", "text": "Pythonの単体テストです！"}
            ]
        }
    }


@pytest.fixture(scope="module")
def mock_voicevox_responses():
    """Prepare mock responses for VoiceVox service."""
    return {
        "audio_query_response": {
            "accent_phrases": [
                {
                    "moras": [
                        {"text": "こ", "consonant_length": 0.1, "vowel_length": 0.1},
                        {"text": "ん", "consonant_length": 0.0, "vowel_length": 0.2},
                        {"text": "に", "consonant_length": 0.1, "vowel_length": 0.1},
                        {"text": "ち", "consonant_length": 0.1, "vowel_length": 0.1},
                        {"text": "は", "consonant_length": 0.0, "vowel_length": 0.2}
                    ]
                }
            ]
        },
        "synthesis_response": b'mock audio data'
    }


@pytest.fixture
def mock_services(mock_ollama_responses, mock_voicevox_responses):
    """Set up mock external services."""
    # Mock OllamaService
    ollama_patcher = patch('src.backend.app.services.ollama_service.OllamaClient')
    mock_ollama_client = ollama_patcher.start()
    mock_ollama_client().check_ollama_availability.return_value = {
        "available": True,
        "models": ["gemma3:4b"],
        "error": None
    }
    mock_ollama_client().generate_json_sync.return_value = mock_ollama_responses["script_response"]
    
    # Mock VoiceVoxService requests
    voicevox_patcher = patch('src.backend.app.services.voicevox_service.requests')
    mock_voicevox = voicevox_patcher.start()
    
    # Configure the mock responses
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = mock_voicevox_responses["audio_query_response"]
    mock_post_response.content = mock_voicevox_responses["synthesis_response"]
    mock_voicevox.post.return_value = mock_post_response
    
    mock_get_response = MagicMock()
    mock_get_response.status_code = 200
    mock_get_response.json.return_value = [
        {"name": "Speaker1", "speaker_uuid": "uuid1", "styles": [{"id": 1, "name": "Normal"}]}
    ]
    mock_voicevox.get.return_value = mock_get_response
    
    # Mock file operations
    open_patcher = patch('builtins.open', MagicMock())
    open_patcher.start()
    
    # Enable testing mode
    init_testing_mode()
    
    yield
    
    # Cleanup
    ollama_patcher.stop()
    voicevox_patcher.stop()
    open_patcher.stop()


@pytest.fixture
def client(mock_services):
    """Create a test client for the Flask app."""
    app = create_app(TestConfig())
    with app.test_client() as client:
        yield client


def test_full_manzai_generation_flow(client):
    """Test the complete flow from script generation to audio synthesis."""
    # Step 1: Generate script
    generate_response = client.post('/api/generate',
                                   json={"topic": "テスト", "model": "gemma3:4b"})
    
    # Verify generate response
    assert generate_response.status_code == 200
    generate_data = json.loads(generate_response.data)
    assert "script" in generate_data
    assert len(generate_data["script"]) == 4
    assert generate_data["script"][0]["role"] == "tsukkomi"
    assert generate_data["script"][0]["text"] == "今日は何について話しましょうか？"
    
    # Step 2: Test audio synthesis with the generated script
    script_for_synthesis = [
        {"speaker": "ツッコミ", "text": generate_data["script"][0]["text"], "speaker_id": 1},
        {"speaker": "ボケ", "text": generate_data["script"][1]["text"], "speaker_id": 2}
    ]
    
    synthesis_response = client.post('/api/synthesize',
                                   json={"script": script_for_synthesis})
    
    # Verify synthesis response
    assert synthesis_response.status_code == 200
    synthesis_data = json.loads(synthesis_response.data)
    assert "audio_data" in synthesis_data
    assert len(synthesis_data["audio_data"]) == 2
    assert synthesis_data["audio_data"][0]["speaker"] == "ツッコミ"
    assert synthesis_data["audio_data"][1]["speaker"] == "ボケ"
    assert "audio_file" in synthesis_data["audio_data"][0]
    assert "audio_file" in synthesis_data["audio_data"][1]


def test_health_and_status_endpoints(client):
    """Test that health and status endpoints work correctly."""
    # Test health endpoint
    health_response = client.get('/api/health')
    assert health_response.status_code == 200
    health_data = json.loads(health_response.data)
    assert health_data["status"] == "healthy"
    
    # Test detailed status endpoint
    status_response = client.get('/api/detailed-status')
    assert status_response.status_code == 200
    status_data = json.loads(status_response.data)
    assert "timestamp" in status_data
    assert "ollama" in status_data
    assert "voicevox" in status_data
    assert "system" in status_data
    
    # Verify ollama status
    assert status_data["ollama"]["available"] is True
    
    # Verify voicevox status
    assert status_data["voicevox"]["available"] is True


def test_error_handling_and_recovery(client):
    """Test error handling and recovery in the application."""
    # Mock OllamaService to simulate an error
    with patch('src.backend.app.routes.api.current_app.ollama_service.generate_manzai_script') as mock_generate:
        mock_generate.side_effect = Exception("Simulated error")
        
        # Call the generate endpoint
        error_response = client.post('/api/generate',
                                    json={"topic": "エラーテスト", "model": "gemma3:4b"})
        
        # Verify error response
        assert error_response.status_code == 500
        error_data = json.loads(error_response.data)
        assert "error" in error_data
    
    # Now try a normal request again to verify recovery
    normal_response = client.post('/api/generate',
                                 json={"topic": "回復テスト", "model": "gemma3:4b"})
    
    # Verify normal response
    assert normal_response.status_code == 200
    normal_data = json.loads(normal_response.data)
    assert "script" in normal_data 