import pytest
import json
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_generate_endpoint_rejects_empty_topic(client):
    """空のトピックがAPIによって適切に拒否されることを確認"""
    response = client.post('/api/generate', 
                          json={'topic': ''},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_generate_endpoint_rejects_missing_topic(client):
    """トピックが欠けている場合にAPIが適切に拒否することを確認"""
    response = client.post('/api/generate', 
                          json={},
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_generate_endpoint_with_invalid_json(client):
    """不正なJSONを送信した場合にAPIが適切に処理することを確認"""
    response = client.post('/api/generate', 
                          data='不正なJSON', 
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_generate_endpoint_with_wrong_content_type(client):
    """誤ったコンテンツタイプでリクエストした場合にAPIが適切に処理することを確認"""
    response = client.post('/api/generate', 
                          data='{"topic":"テスト"}', 
                          content_type='text/plain')
    assert response.status_code == 415  # 不適切なメディアタイプ
    data = json.loads(response.data)
    assert 'error' in data

def test_generate_endpoint_with_excessive_payload(client):
    """非常に大きなペイロードでもAPIが適切に処理することを確認"""
    huge_topic = "あ" * 10000  # 10000文字の巨大なトピック
    response = client.post('/api/generate', 
                          json={'topic': huge_topic},
                          content_type='application/json')
    
    # サイズ制限があれば400エラー、なければ正常に処理
    if response.status_code == 400:
        data = json.loads(response.data)
        assert 'error' in data
        assert 'size' in data['error'].lower() or 'large' in data['error'].lower()
    else:
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'script' in data 