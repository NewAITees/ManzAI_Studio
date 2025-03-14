import requests
from typing import Dict, List, Any, Optional
import json

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
            raise VoiceVoxServiceError("Failed to connect to VoiceVox service")
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
            raise VoiceVoxServiceError("Failed to connect to VoiceVox service")
        except Exception as e:
            raise VoiceVoxServiceError(f"Unexpected error: {str(e)}") 