"""Test configuration settings."""
import os
import pytest
from src.backend.app import create_app
from src.backend.app.config import BaseConfig, TestConfig, DevelopmentConfig, ProductionConfig

def test_development_config():
    """Test development configuration."""
    app = create_app(DevelopmentConfig())
    assert app.config['DEVELOPMENT']
    assert not app.config['TESTING']

def test_test_config():
    """Test test configuration."""
    app = create_app(TestConfig())
    assert app.config['TESTING']
    assert TestConfig().VOICEVOX_URL == "http://voicevox:50021"
    assert TestConfig().OLLAMA_URL == "http://ollama:11434"

def test_production_config():
    """Test production configuration."""
    app = create_app(ProductionConfig())
    assert not app.config['DEVELOPMENT']
    assert not app.config['TESTING'] 