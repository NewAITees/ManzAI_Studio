"""ヘルスエンドポイントのテスト"""
import pytest
from flask.testing import FlaskClient

def test_health_endpoint_returns_200(client: FlaskClient) -> None:
    """APIのヘルスエンドポイントが200を返すことを確認"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_health_endpoint_returns_correct_content_type(client: FlaskClient) -> None:
    """APIのヘルスエンドポイントが正しいContent-Typeを返すことを確認"""
    response = client.get('/api/health')
    assert response.content_type == 'application/json' 