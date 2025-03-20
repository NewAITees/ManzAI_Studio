import pytest
from src.backend.app import create_app
from src.backend.app.config import TestConfig

@pytest.fixture
def app():
    """Create and configure a test application instance."""
    app = create_app(TestConfig())
    return app

@pytest.fixture
def client(app):
    """Create a test client for the application."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner for the application."""
    return app.test_cli_runner() 