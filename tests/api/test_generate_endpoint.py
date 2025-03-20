"""生成エンドポイントのテスト"""

import os
import pytest
import json
from flask.testing import FlaskClient
from typing import Generator, Dict, Any

from tests.utils.test_helpers import init_testing_mode

@pytest.fixture(scope="module", autouse=True)
def setup_environment() -> None:
    """テスト環境のセットアップ"""
    os.environ["FLASK_ENV"] = "development"
    init_testing_mode()

def test_generate_script_success(client: FlaskClient) -> None:
    """Test successful script generation."""
    response = client.post('/api/generate-script', json={
        'topic': 'テスト',
        'model': 'gemma3:4b'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'script' in data
    assert isinstance(data['script'], list)
    assert len(data['script']) > 0

def test_generate_script_with_options(client: FlaskClient) -> None:
    """Test script generation with additional options."""
    response = client.post('/api/generate-script', json={
        'topic': 'テスト',
        'model': 'gemma3:4b',
        'options': {
            'temperature': 0.7,
            'top_p': 0.9
        }
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'script' in data
    assert isinstance(data['script'], list)
    assert len(data['script']) > 0

def test_generate_endpoint_with_missing_topic(client: FlaskClient) -> None:
    """トピックが不足した場合にAPIが400エラーを返すことを確認"""
    response = client.post('/api/generate', json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data

def test_generate_endpoint_with_empty_topic(client: FlaskClient) -> None:
    """空のトピックでAPIが400エラーを返すことを確認"""
    response = client.post('/api/generate', json={'topic': ''})
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'topic' in json_data['error'].lower()
    assert 'value error' in json_data['error'].lower()

def test_generate_endpoint_with_invalid_content_type(client: FlaskClient) -> None:
    """不正なContent-TypeでAPIが415エラーを返すことを確認"""
    response = client.post('/api/generate', data='invalid data')
    assert response.status_code in [400, 415]
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'json' in json_data['error'].lower() 