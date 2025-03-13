"""Configuration settings for the backend application."""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Base configuration."""

    TESTING: bool = False
    VOICEVOX_URL: str = os.getenv("VOICEVOX_URL", "http://localhost:50021")
    OLLAMA_URL: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "phi")


@dataclass
class TestConfig(Config):
    """Test configuration."""

    TESTING: bool = True
    VOICEVOX_URL: str = "http://voicevox:50021"
    OLLAMA_URL: str = "http://ollama:11434"


@dataclass
class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG: bool = True


@dataclass
class ProductionConfig(Config):
    """Production configuration."""

    DEBUG: bool = False 