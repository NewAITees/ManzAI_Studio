import requests
from typing import Dict, List, Any, Optional, Tuple
import json
import os
import time

class VoiceVoxServiceError(Exception):
    """VoiceVoxサービスのエラーを表す例外クラス"""
    pass

class VoiceVoxService:
    """VoiceVoxサービスとの通信を担当するクラス"""
    
    def __init__(self, base_url: str = "http://localhost:50021"):
        """VoiceVoxServiceの初期化
        
        Args:
            base_url (str): VoiceVoxサービスのベースURL
        """
        self.base_url = base_url
        self.output_dir = os.path.join("audio")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_voice(self, text: str, speaker_id: int = 1) -> bytes:
        """指定されたテキストから音声を生成
        
        Args:
            text (str): 音声化するテキスト
            speaker_id (int): 話者ID
            
        Returns:
            bytes: 生成された音声データ
            
        Raises:
            ValueError: テキストが空の場合、または話者IDが不正な場合
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        
        if speaker_id < 1:
            raise ValueError("invalid speaker id")
        
        try:
            # 音声合成用のクエリを作成
            query_response = requests.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": speaker_id}
            )
            
            if query_response.status_code != 200:
                raise VoiceVoxServiceError(f"Failed to create audio query: {query_response.status_code}")
            
            # 音声合成を実行
            synthesis_response = requests.post(
                f"{self.base_url}/synthesis",
                params={"speaker": speaker_id},
                json=query_response.json()
            )
            
            if synthesis_response.status_code != 200:
                raise VoiceVoxServiceError(f"Failed to synthesize audio: {synthesis_response.status_code}")
            
            return synthesis_response.content
            
        except requests.exceptions.ConnectionError:
            raise VoiceVoxServiceError("Connection error: Failed to connect to VoiceVox service")
        except VoiceVoxServiceError:
            raise
        except Exception as e:
            raise VoiceVoxServiceError(f"Unexpected error: {str(e)}")
    
    def get_timing_data(self, text: str, speaker_id: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """指定されたテキストのタイミングデータを取得
        
        Args:
            text (str): タイミングデータを取得するテキスト
            speaker_id (int): 話者ID
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: タイミングデータ
            
        Raises:
            ValueError: テキストが空の場合、または話者IDが不正な場合
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        
        if speaker_id < 1:
            raise ValueError("invalid speaker id")
        
        try:
            response = requests.post(
                f"{self.base_url}/accent_phrases",
                params={"text": text, "speaker": speaker_id}
            )
            
            if response.status_code != 200:
                raise VoiceVoxServiceError(f"Failed to get timing data: {response.status_code}")
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            raise VoiceVoxServiceError("Connection error: Failed to connect to VoiceVox service")
        except VoiceVoxServiceError:
            raise
        except Exception as e:
            raise VoiceVoxServiceError(f"Unexpected error: {str(e)}")
            
    def synthesize_voice(self, text: str, speaker_id: int = 1) -> Tuple[str, Dict[str, Any]]:
        """テキストから音声を合成し、ファイルに保存する
        
        Args:
            text (str): 音声化するテキスト
            speaker_id (int): 話者ID
            
        Returns:
            Tuple[str, Dict[str, Any]]: (音声ファイルパス, タイミングデータ)
            
        Raises:
            ValueError: テキストが空の場合
            VoiceVoxServiceError: 音声合成に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        
        try:
            # 音声合成用のクエリを作成
            query_response = requests.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": speaker_id}
            )
            
            if query_response.status_code != 200:
                raise VoiceVoxServiceError(f"Failed to create audio query: {query_response.status_code}")
            
            query_data = query_response.json()
            
            # 音声合成を実行
            synthesis_response = requests.post(
                f"{self.base_url}/synthesis",
                params={"speaker": speaker_id},
                json=query_data
            )
            
            if synthesis_response.status_code != 200:
                raise VoiceVoxServiceError(f"Failed to synthesize audio: {synthesis_response.status_code}")
            
            # 音声ファイルを保存
            timestamp = int(time.time())
            filename = f"{timestamp}_{speaker_id}.wav"
            file_path = os.path.join(self.output_dir, filename)
            
            with open(file_path, "wb") as f:
                f.write(synthesis_response.content)
            
            return file_path, query_data
            
        except requests.exceptions.ConnectionError:
            raise VoiceVoxServiceError("Connection error: Failed to connect to VoiceVox service")
        except VoiceVoxServiceError:
            raise
        except Exception as e:
            raise VoiceVoxServiceError(f"Unexpected error: {str(e)}")
    
    def get_speakers(self) -> List[Dict[str, Any]]:
        """利用可能な話者の一覧を取得
        
        Returns:
            List[Dict[str, Any]]: 話者情報のリスト
            
        Raises:
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        try:
            response = requests.get(f"{self.base_url}/speakers")
            
            if response.status_code != 200:
                raise VoiceVoxServiceError(f"Failed to get speakers: {response.status_code}")
            
            speakers_data = response.json()
            
            # 簡略化した話者リストを作成
            simplified_speakers = []
            for speaker in speakers_data:
                for style in speaker.get("styles", []):
                    simplified_speakers.append({
                        "id": style.get("id"),
                        "name": f"{speaker.get('name')} ({style.get('name')})"
                    })
            
            return simplified_speakers
            
        except requests.exceptions.ConnectionError:
            raise VoiceVoxServiceError("Connection error: Failed to connect to VoiceVox service")
        except VoiceVoxServiceError:
            raise
        except Exception as e:
            raise VoiceVoxServiceError(f"Unexpected error: {str(e)}") 