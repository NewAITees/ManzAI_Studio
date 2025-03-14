import pytest
from flask import Flask
from src.app import create_app

@pytest.fixture
def app():
    """テスト用のFlaskアプリケーションを作成"""
    app = create_app()
    app.config['TESTING'] = True
    return app

@pytest.fixture
def client(app):
    """テスト用のクライアントを作成"""
    return app.test_client()

def test_health_endpoint_returns_200(client):
    """APIのヘルスエンドポイントが200を返すことを確認"""
    response = client.get('/api/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_health_endpoint_returns_correct_content_type(client):
    """APIのヘルスエンドポイントが正しいContent-Typeを返すことを確認"""
    response = client.get('/api/health')
    assert response.content_type == 'application/json' 