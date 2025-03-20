"""Test configuration for the backend application."""
import pytest
from typing import Generator
from flask import Flask

from src.backend.app import create_app
from src.backend.app.config import TestConfig
from src.services.audio_manager import AudioManager
from src.services.voicevox_service import VoiceVoxService
from src.utils.prompt_loader import PromptLoader
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
    return MagicMock(spec=VoiceVoxService)

@pytest.fixture
def mock_audio_manager():
    """Mock audio manager for testing."""
    return MagicMock(spec=AudioManager)

@pytest.fixture
def mock_prompt_loader():
    """Mock prompt loader for testing."""
    return MagicMock(spec=PromptLoader)

@pytest.fixture
def mock_services(mock_voicevox_service, mock_audio_manager):
    """Combine all mock services into a dictionary."""
    return {
        'voicevox': mock_voicevox_service,
        'audio_manager': mock_audio_manager
    } 