"""Test configuration for the backend application."""
import pytest
from typing import Generator
from flask import Flask

from src.backend.app import create_app
from src.backend.app.config import TestConfig
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.services.audio_manager import AudioManager
from src.backend.app.utils.prompt_loader import PromptLoader
from unittest.mock import MagicMock

@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create and configure a new app instance for each test."""
    test_config = TestConfig()
    app = create_app(test_config)
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_voicevox_service():
    """Mock VoiceVox service for testing."""
    mock = MagicMock()
    mock.synthesize.return_value = "test_audio_file.wav"
    mock.list_speakers.return_value = [
        {"name": "四国めたん", "styles": [{"id": 2, "name": "ノーマル"}]},
        {"name": "ずんだもん", "styles": [{"id": 3, "name": "ノーマル"}]}
    ]
    return mock

@pytest.fixture
def mock_audio_manager():
    """Mock audio manager for testing."""
    mock = MagicMock()
    mock.get_audio_file_path.return_value = "/path/to/audio.wav"
    mock.generate_filename.return_value = "test_audio_file.wav"
    mock.save_audio.return_value = "test_audio_file.wav"
    mock.get_audio_url.return_value = "/audio/test_audio_file.wav"
    return mock

@pytest.fixture
def mock_prompt_loader():
    """Mock prompt loader for testing."""
    mock = MagicMock()
    mock.get_all_prompts.return_value = [
        {"id": "1", "name": "基本プロンプト", "description": "テスト用", "template": "テンプレート"}
    ]
    return mock

@pytest.fixture
def mock_services(mock_voicevox_service, mock_audio_manager):
    """Combine all mock services into a dictionary."""
    return {
        'voicevox': mock_voicevox_service,
        'audio_manager': mock_audio_manager
    } 