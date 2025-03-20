import pytest
from flask import json
from src.backend.app import create_app

# テスト用アプリケーションインスタンスを作成
app = create_app()

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

def test_empty_topic(client):
    """Test that empty topic returns an error."""
    response = client.post('/api/generate-script', json={
        'topic': '',
        'model': 'gemma3:4b'
    })
    assert response.status_code == 400
    assert b'Invalid request data' in response.data

def test_very_long_topic(client):
    """Test handling of very long topic."""
    long_topic = 'a' * 1000  # 1000文字の文字列
    response = client.post('/api/generate-script', json={
        'topic': long_topic,
        'model': 'gemma3:4b'
    })
    assert response.status_code == 400
    assert b'Topic too long' in response.data

def test_special_characters(client):
    """Test handling of special characters in topic."""
    response = client.post('/api/generate-script', json={
        'topic': '!@#$%^&*()',
        'model': 'gemma3:4b'
    })
    assert response.status_code == 400
    assert b'Invalid characters in topic' in response.data 