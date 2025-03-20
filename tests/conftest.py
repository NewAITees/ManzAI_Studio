"""Test configuration for the backend application."""
import pytest
from typing import Generator, Dict, Any
from flask import Flask
from flask.testing import FlaskClient
from unittest.mock import MagicMock

from src.backend.app import create_app
from src.backend.app.config import TestConfig
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.services.audio_manager import AudioManager
from src.backend.app.utils.prompt_loader import PromptLoader

@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create and configure a new app instance for each test."""
    test_config = TestConfig()
    app = create_app(test_config)
    yield app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app: Flask):
    """Create a test runner for the app's CLI commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_voicevox_service() -> MagicMock:
    """Mock VoiceVox service for testing."""
    mock = MagicMock(spec=VoiceVoxService)
    mock.synthesize.return_value = "test_audio_file.wav"
    mock.list_speakers.return_value = [
        {"name": "四国めたん", "styles": [{"id": 2, "name": "ノーマル"}]},
        {"name": "ずんだもん", "styles": [{"id": 3, "name": "ノーマル"}]}
    ]
    return mock

@pytest.fixture
def mock_audio_manager() -> MagicMock:
    """Mock audio manager for testing."""
    mock = MagicMock(spec=AudioManager)
    mock.get_audio_file_path.return_value = "/path/to/audio.wav"
    mock.generate_filename.return_value = "test_audio_file.wav"
    mock.save_audio.return_value = "test_audio_file.wav"
    mock.get_audio_url.return_value = "/audio/test_audio_file.wav"
    return mock

@pytest.fixture
def mock_prompt_loader() -> MagicMock:
    """Mock prompt loader for testing."""
    mock = MagicMock(spec=PromptLoader)
    mock.get_all_prompts.return_value = [
        {"id": "1", "name": "基本プロンプト", "description": "テスト用", "template": "テンプレート"}
    ]
    return mock

@pytest.fixture
def mock_services(mock_voicevox_service: MagicMock, mock_audio_manager: MagicMock) -> Dict[str, Any]:
    """Combine all mock services into a dictionary."""
    return {
        'voicevox': mock_voicevox_service,
        'audio_manager': mock_audio_manager
    } 