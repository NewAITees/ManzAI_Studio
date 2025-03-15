import pytest
from flask import json
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_endpoint_with_very_long_topic(client):
    """非常に長いトピックでもAPIが適切に処理することを確認"""
    long_topic = "あ" * 1000  # 1000文字のトピック
    response = client.post('/api/generate', 
                          json={'topic': long_topic},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'script' in data
    assert len(data['script']) > 0

def test_generate_endpoint_with_special_characters(client):
    """特殊文字を含むトピックでもAPIが正常に処理することを確認"""
    special_topic = "特殊文字!@#$%^&*()_+{}|:<>?[];\',./\\"
    response = client.post('/api/generate', 
                          json={'topic': special_topic},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'script' in data
    assert len(data['script']) > 0

def test_generate_endpoint_with_emoji(client):
    """絵文字を含むトピックでもAPIが正常に処理することを確認"""
    emoji_topic = "絵文字テスト😀🎉🚀💖🐱"
    response = client.post('/api/generate', 
                          json={'topic': emoji_topic},
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'script' in data
    assert len(data['script']) > 0 