"""Test API endpoints."""
import json
import pytest
from flask import Flask
from src.backend.app import create_app
from src.backend.app.config import TestConfig

def test_index(client):
    """Test the index endpoint."""
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert data['message'] == 'ManzAI Studio API is running'

def test_404_error(client):
    """Test 404 error handling."""
    response = client.get('/nonexistent')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Resource not found' 