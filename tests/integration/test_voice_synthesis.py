#!/usr/bin/env python3
"""
VoiceVox音声合成機能のテストスクリプト
"""
import pytest
import requests
import json
from typing import Dict, List

@pytest.fixture
def api_base_url() -> str:
    """APIのベースURLを返すフィクスチャ"""
    return "http://localhost:5000/api"

@pytest.fixture
def sample_text() -> str:
    """テスト用のテキストを返すフィクスチャ"""
    return "こんにちは、VoiceVoxのテストです。"

@pytest.fixture
def sample_script() -> List[Dict[str, str]]:
    """テスト用の漫才スクリプトを返すフィクスチャ"""
    return [
        {"role": "tsukkomi", "text": "いやー、今日はいい天気ですね。"},
        {"role": "boke", "text": "そうですね、空が青いです。まるでソーダ水みたいに。"},
        {"role": "tsukkomi", "text": "ソーダ水!? 透明やん! 空と全然違うやん!"}
    ]

def test_get_speakers(api_base_url: str):
    """話者一覧取得のテスト"""
    response = requests.get(f"{api_base_url}/speakers")
    
    assert response.status_code == 200
    data = response.json()
    assert "speakers" in data
    
    speakers = data["speakers"]
    assert len(speakers) > 0
    
    # 各話者の情報を確認
    for speaker in speakers:
        assert "id" in speaker
        assert "name" in speaker
        assert isinstance(speaker["id"], int)
        assert isinstance(speaker["name"], str)

def test_single_text_synthesis(api_base_url: str, sample_text: str):
    """単一テキストの音声合成テスト"""
    response = requests.post(
        f"{api_base_url}/synthesize",
        json={"text": sample_text, "speaker_id": 1}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "audio_url" in data
    assert "timing_data" in data
    
    # 音声URLの形式を確認
    audio_url = data["audio_url"]
    assert isinstance(audio_url, str)
    assert audio_url.startswith("http://") or audio_url.startswith("https://")
    
    # タイミングデータの構造を確認
    timing_data = data["timing_data"]
    assert "accent_phrases" in timing_data
    assert isinstance(timing_data["accent_phrases"], list)

def test_script_synthesis(api_base_url: str, sample_script: List[Dict[str, str]]):
    """漫才スクリプト全体の音声合成テスト"""
    response = requests.post(
        f"{api_base_url}/synthesize_script",
        json={
            "script": sample_script,
            "tsukkomi_id": 1,  # ずんだもん
            "boke_id": 3       # 四国めたん
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    
    results = data["results"]
    assert len(results) == len(sample_script)
    
    # 各音声合成結果を確認
    for result, original in zip(results, sample_script):
        assert "role" in result
        assert "text" in result
        assert "audio_url" in result
        assert result["role"] == original["role"]
        assert result["text"] == original["text"]
        assert isinstance(result["audio_url"], str)
        assert result["audio_url"].startswith("http://") or result["audio_url"].startswith("https://") 