"""
基本的なエンドツーエンドテスト
APIエンドポイントの一連の呼び出しをシミュレートし、システム全体の動作を検証します。
"""
import os
import json
import time
import pytest
import requests

# テスト設定
BASE_URL = os.environ.get("TEST_API_URL", "http://localhost:5000")
MAX_RETRIES = 5
RETRY_DELAY = 2  # 秒

def retry_request(func, *args, **kwargs):
    """
    リトライ機能付きのリクエスト送信関数
    
    Args:
        func: 実行する関数
        
    Returns:
        関数の実行結果
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = func(*args, **kwargs)
            return response
        except requests.RequestException as e:
            if attempt < MAX_RETRIES - 1:
                print(f"リクエスト失敗、{RETRY_DELAY}秒後に再試行します: {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise

def test_server_health():
    """サーバーのヘルスチェック"""
    response = retry_request(requests.get, f"{BASE_URL}/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"
    
    # サービスのステータスを確認
    assert "services" in data
    assert "ollama" in data["services"]
    assert "voicevox" in data["services"]

def test_full_manzai_generation_flow():
    """漫才生成から音声合成までの一連のフロー"""
    # 1. 漫才生成リクエスト
    topic = "人工知能"
    payload = {"topic": topic}
    response = retry_request(requests.post, f"{BASE_URL}/api/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # スクリプトの存在を確認
    assert "script" in data
    assert isinstance(data["script"], list)
    assert len(data["script"]) > 0
    
    # 各台詞の形式を確認
    script = data["script"]
    for line in script:
        assert "speaker" in line
        assert "text" in line
    
    # 2. 音声合成リクエスト （存在する場合）
    if "synthesize" in data.get("audio_data", [{}])[0].get("audio_file", ""):
        speakers = [
            {"speaker": "ツッコミ", "text": "こんにちは", "speaker_id": 1},
            {"speaker": "ボケ", "text": "どうも", "speaker_id": 2}
        ]
        payload = {"script": speakers}
        response = retry_request(requests.post, f"{BASE_URL}/api/synthesize", json=payload)
        assert response.status_code == 200
        audio_data = response.json()
        assert "audio_data" in audio_data
        
        # 音声ファイルへのアクセス確認
        for audio in audio_data["audio_data"]:
            assert "audio_file" in audio
            audio_url = f"{BASE_URL}/api/audio/{audio['audio_file']}"
            audio_response = retry_request(requests.get, audio_url)
            assert audio_response.status_code == 200

def test_speakers_endpoint():
    """話者一覧取得APIのテスト"""
    response = retry_request(requests.get, f"{BASE_URL}/api/speakers")
    assert response.status_code == 200
    data = response.json()
    assert "speakers" in data
    
    # 話者リストの検証
    speakers = data["speakers"]
    assert isinstance(speakers, list)
    if speakers:  # 話者が存在する場合
        for speaker in speakers:
            assert "name" in speaker
            assert "styles" in speaker 