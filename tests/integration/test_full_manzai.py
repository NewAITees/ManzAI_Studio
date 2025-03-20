#!/usr/bin/env python3
"""
漫才生成から音声合成までの一連の流れをテストするスクリプト
"""
import pytest
import requests
import json
import time
from typing import Dict, List

@pytest.fixture
def api_base_url() -> str:
    """APIのベースURLを返すフィクスチャ"""
    return "http://localhost:5000/api"

@pytest.fixture
def sample_topic() -> str:
    """テスト用のトピックを返すフィクスチャ"""
    return "スマートフォン"

def test_generate_script(api_base_url: str, sample_topic: str):
    """漫才台本生成のテスト"""
    response = requests.post(
        f"{api_base_url}/generate",
        json={"topic": sample_topic}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "script" in data
    script = data["script"]
    assert len(script) > 0
    
    # 各台詞の構造を確認
    for line in script:
        assert "role" in line
        assert "text" in line
        assert line["role"] in ["tsukkomi", "boke"]
        assert isinstance(line["text"], str)
        assert len(line["text"]) > 0

def test_synthesize_script(api_base_url: str, sample_topic: str):
    """音声合成のテスト"""
    # まず台本を生成
    script_response = requests.post(
        f"{api_base_url}/generate",
        json={"topic": sample_topic}
    )
    
    assert script_response.status_code == 200
    script = script_response.json()["script"]
    
    # 音声合成を実行
    synthesis_response = requests.post(
        f"{api_base_url}/synthesize_script",
        json={
            "script": script,
            "tsukkomi_id": 1,  # ずんだもん
            "boke_id": 3       # 四国めたん
        }
    )
    
    assert synthesis_response.status_code == 200
    results = synthesis_response.json().get("results", [])
    assert len(results) == len(script)
    
    # 各音声合成結果を確認
    for result in results:
        assert "role" in result
        assert "text" in result
        assert "audio_url" in result
        assert result["role"] in ["tsukkomi", "boke"]
        assert isinstance(result["text"], str)
        assert isinstance(result["audio_url"], str)
        assert result["audio_url"].startswith("http://") or result["audio_url"].startswith("https://")

def main():
    """メイン関数"""
    base_url = "http://localhost:5000/api"
    
    # 1. 漫才台本生成
    print("漫才台本を生成中...")
    topic = "スマートフォン"
    try:
        script_response = requests.post(
            f"{base_url}/generate",
            json={"topic": topic}
        )
        
        if script_response.status_code != 200:
            print(f"台本生成に失敗: {script_response.text}")
            return
            
        script_data = script_response.json()
        script = script_data["script"]
        
        print(f"トピック「{topic}」について{len(script)}行の台詞を生成しました")
        
        # 台本の内容を表示
        print("\n=== 生成された台本 ===")
        for i, line in enumerate(script):
            role = "ツッコミ" if line["role"] == "tsukkomi" else "ボケ"
            print(f"{role}: {line['text']}")
    except Exception as e:
        print(f"台本生成中にエラーが発生: {str(e)}")
        return
    
    # 2. 音声合成
    print("\n台本の音声を合成中...")
    try:
        synthesis_response = requests.post(
            f"{base_url}/synthesize_script",
            json={
                "script": script,
                "tsukkomi_id": 1,  # ずんだもん
                "boke_id": 3       # 四国めたん
            }
        )
        
        if synthesis_response.status_code != 200:
            print(f"音声合成に失敗: {synthesis_response.text}")
            return
            
        results = synthesis_response.json().get("results", [])
        
        print(f"{len(results)}行の台詞の音声合成に成功しました")
        print("\n=== 音声つき台本 ===")
        
        for i, line in enumerate(results):
            role = "ツッコミ" if line["role"] == "tsukkomi" else "ボケ"
            print(f"{role}: {line['text']}")
            print(f"   音声: {line['audio_url']}")
            
        print("\nテスト完了!")
        
    except Exception as e:
        print(f"音声合成中にエラーが発生: {str(e)}")

if __name__ == "__main__":
    main() 