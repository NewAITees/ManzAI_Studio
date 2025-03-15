import pytest
import threading
import time
import json
from src.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_multiple_concurrent_requests(client):
    """複数の同時リクエストが適切に処理されることを確認"""
    results = []
    errors = []
    
    def make_request(topic):
        try:
            response = client.post('/api/generate', 
                                  json={'topic': topic},
                                  content_type='application/json')
            results.append(json.loads(response.data))
        except Exception as e:
            errors.append(str(e))
    
    # 3つの同時リクエストを開始
    threads = []
    for i in range(3):
        t = threading.Thread(target=make_request, args=(f"同時リクエストテスト{i}",))
        threads.append(t)
        t.start()
    
    # すべてのスレッドの完了を待機
    for t in threads:
        t.join(timeout=60)  # 最大60秒待機
    
    assert len(errors) == 0, f"エラーが発生: {errors}"
    assert len(results) == 3, f"リクエスト結果数が不足: {len(results)}"
    
    # 各レスポンスが有効なスクリプトを含んでいることを確認
    for result in results:
        assert 'script' in result
        assert len(result['script']) > 0
        
    # 各レスポンスが異なるスクリプトを含んでいることを確認（内容のハッシュ比較）
    script_contents = [str(r['script']) for r in results]
    unique_scripts = set(script_contents)
    assert len(unique_scripts) == 3, "同時リクエストで同一の結果が返された"
    
def test_concurrent_request_isolation(client):
    """同時リクエストが互いに影響しないことを確認"""
    # 非常に異なるトピックで2つの同時リクエストを実行
    topics = ["猫について", "宇宙旅行"]
    results = []
    
    def make_request(topic):
        response = client.post('/api/generate', 
                              json={'topic': topic},
                              content_type='application/json')
        results.append({
            'topic': topic,
            'response': json.loads(response.data)
        })
    
    # 同時リクエストを開始
    threads = []
    for topic in topics:
        t = threading.Thread(target=make_request, args=(topic,))
        threads.append(t)
        t.start()
    
    # すべてのスレッドの完了を待機
    for t in threads:
        t.join(timeout=60)
    
    # 各レスポンスがそれぞれのトピックに関連した内容を含んでいることを確認
    for result in results:
        topic = result['topic']
        response = result['response']
        
        if topic == "猫について":
            # 猫に関連する単語が含まれているか確認
            script_text = " ".join([line.get('text', '') for line in response['script']])
            assert any(word in script_text for word in ["猫", "ねこ", "ネコ", "キャット"])
        
        elif topic == "宇宙旅行":
            # 宇宙に関連する単語が含まれているか確認
            script_text = " ".join([line.get('text', '') for line in response['script']])
            assert any(word in script_text for word in ["宇宙", "星", "ロケット", "惑星", "スペース"]) 