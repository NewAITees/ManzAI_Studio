import pytest
from unittest.mock import patch, MagicMock
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

def test_generate_endpoint_with_valid_topic(client):
    """有効なトピックでAPIが正常に漫才を生成することを確認"""
    mock_response = {
        'script': [
            {'role': 'tsukkomi', 'text': 'こんにちは'},
            {'role': 'boke', 'text': 'どうも！'}
        ],
        'audio_data': [
            {'role': 'tsukkomi', 'audio_path': '/audio/1.wav'},
            {'role': 'boke', 'audio_path': '/audio/2.wav'}
        ]
    }
    
    with patch('src.services.ollama_service.OllamaService.generate_manzai_script') as mock_generate:
        mock_generate.return_value = mock_response
        
        response = client.post('/api/generate', json={'topic': 'テスト漫才'})
        
        assert response.status_code == 200
        assert 'script' in response.json
        assert 'audio_data' in response.json
        assert len(response.json['script']) > 0
        assert len(response.json['audio_data']) > 0

def test_generate_endpoint_with_missing_topic(client):
    """トピックが不足した場合にAPIが400エラーを返すことを確認"""
    response = client.post('/api/generate', json={})
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'topic is required' in response.json['error'].lower()

def test_generate_endpoint_with_empty_topic(client):
    """空のトピックでAPIが400エラーを返すことを確認"""
    response = client.post('/api/generate', json={'topic': ''})
    
    assert response.status_code == 400
    assert 'error' in response.json
    assert 'topic cannot be empty' in response.json['error'].lower()

def test_generate_endpoint_with_invalid_content_type(client):
    """不正なContent-TypeでAPIが415エラーを返すことを確認"""
    response = client.post('/api/generate', data='invalid data')
    
    assert response.status_code == 415
    assert 'error' in response.json
    assert 'content type' in response.json['error'].lower() 