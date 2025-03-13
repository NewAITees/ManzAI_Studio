"""Test configuration for the backend application."""
import pytest
from typing import Generator
from flask import Flask
from flask.testing import FlaskClient

from backend.app import create_app
from backend.app.config import TestConfig


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app: Flask):
    """Create a test runner for the app's CLI commands."""
    return app.test_cli_runner() 