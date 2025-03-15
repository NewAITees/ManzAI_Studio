#!/usr/bin/env python3
"""
VoiceVox音声合成機能のテストスクリプト
"""
import requests
import json
import os
import time

def main():
    """メイン関数"""
    base_url = "http://localhost:5000/api"
    
    # 1. 話者一覧を取得
    print("話者一覧を取得中...")
    try:
        speakers_response = requests.get(f"{base_url}/speakers")
        
        if speakers_response.status_code == 200:
            speakers = speakers_response.json().get("speakers", [])
            print(f"利用可能な話者: {len(speakers)}人")
            for i, speaker in enumerate(speakers[:10]):  # 最初の10人だけ表示
                print(f"  {speaker['id']}: {speaker['name']}")
        else:
            print(f"話者一覧の取得に失敗: {speakers_response.text}")
            return
    except Exception as e:
        print(f"エラー: {str(e)}")
        return
    
    # 2. 単一のテキストを音声合成
    print("\n単一テキストの音声合成...")
    text = "こんにちは、VoiceVoxのテストです。"
    try:
        synthesis_response = requests.post(
            f"{base_url}/synthesize",
            json={"text": text, "speaker_id": 1}
        )
        
        if synthesis_response.status_code == 200:
            result = synthesis_response.json()
            audio_url = result["audio_url"]
            timing_data = result["timing_data"]
            
            print(f"音声URL: {audio_url}")
            print(f"アクセント句: {len(timing_data.get('accent_phrases', []))}個")
            print("音声合成成功!")
        else:
            print(f"音声合成に失敗: {synthesis_response.text}")
    except Exception as e:
        print(f"エラー: {str(e)}")
    
    # 3. 漫才スクリプト全体の音声合成
    print("\n漫才スクリプトの音声合成...")
    # サンプルスクリプト
    script = [
        {"role": "tsukkomi", "text": "いやー、今日はいい天気ですね。"},
        {"role": "boke", "text": "そうですね、空が青いです。まるでソーダ水みたいに。"},
        {"role": "tsukkomi", "text": "ソーダ水!? 透明やん! 空と全然違うやん!"}
    ]
    
    try:
        script_synthesis_response = requests.post(
            f"{base_url}/synthesize_script",
            json={
                "script": script,
                "tsukkomi_id": 1,  # ずんだもん
                "boke_id": 3  # 四国めたん
            }
        )
        
        if script_synthesis_response.status_code == 200:
            result = script_synthesis_response.json()
            results = result.get("results", [])
            
            print(f"{len(results)}個の台詞の音声合成に成功!")
            for i, line in enumerate(results):
                role = "ツッコミ" if line["role"] == "tsukkomi" else "ボケ"
                print(f"{role}: {line['text']}")
                print(f"  音声URL: {line['audio_url']}")
        else:
            print(f"スクリプト音声合成に失敗: {script_synthesis_response.text}")
    except Exception as e:
        print(f"エラー: {str(e)}")
    
    print("\nテスト完了!")

if __name__ == "__main__":
    main() 