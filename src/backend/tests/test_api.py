"""Tests for the API routes."""
import pytest
from flask.testing import FlaskClient
from typing import Dict, Any


def test_health_check(client: FlaskClient) -> None:
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}


def test_generate_manzai_no_topic(client: FlaskClient) -> None:
    """Test the generate endpoint with no topic."""
    response = client.post("/api/generate", json={})
    assert response.status_code == 400
    assert "error" in response.json


def test_generate_manzai_with_topic(client: FlaskClient) -> None:
    """Test the generate endpoint with a topic."""
    response = client.post("/api/generate", json={"topic": "猫"})
    assert response.status_code == 501  # Not implemented yet
    assert "message" in response.json 