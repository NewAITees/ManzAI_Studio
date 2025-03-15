import os
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, cast
import json

import requests
from requests.exceptions import RequestException, ConnectionError, Timeout

from src.models.audio import AudioSynthesisResult, SpeechTimingData
from src.models.service import VoiceVoxSpeaker

logger = logging.getLogger(__name__)

class VoiceVoxServiceError(Exception):
    """VoiceVoxサービスのエラーを表す例外クラス"""
    pass

class VoiceVoxService:
    """VoiceVoxサービスとの通信を担当するクラス"""
    
    def __init__(self, base_url: str = "http://localhost:50021") -> None:
        """VoiceVoxServiceの初期化
        
        Args:
            base_url: VoiceVoxサービスのベースURL
        """
        self.base_url = base_url
        self.output_dir = os.path.join("audio")
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"VoiceVoxService initialized with base URL: {base_url}")
    
    def generate_voice(self, text: str, speaker_id: int = 1) -> bytes:
        """指定されたテキストから音声を生成
        
        Args:
            text: 音声化するテキスト
            speaker_id: 話者ID
            
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
            query_params: Dict[str, str] = {
                "text": text,
                "speaker": str(speaker_id)
            }
            query_response = requests.post(
                f"{self.base_url}/audio_query",
                params=query_params,
                timeout=30
            )
            query_response.raise_for_status()
            query = query_response.json()
            
            # 音声合成を実行
            synthesis_params: Dict[str, str] = {
                "speaker": str(speaker_id)
            }
            synthesis_response = requests.post(
                f"{self.base_url}/synthesis",
                headers={"Content-Type": "application/json"},
                params=synthesis_params,
                data=json.dumps(query),
                timeout=30
            )
            synthesis_response.raise_for_status()
            
            return synthesis_response.content
            
        except (ConnectionError, Timeout) as e:
            error_message = f"Connection error with VoiceVox API: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except RequestException as e:
            error_message = f"Error calling VoiceVox API: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except (ValueError, KeyError) as e:
            error_message = f"Error parsing VoiceVox API response: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except Exception as e:
            error_message = f"Unexpected error in generate_voice: {str(e)}"
            logger.exception(error_message)
            raise VoiceVoxServiceError(error_message)
    
    def get_timing_data(self, text: str, speaker_id: int = 1) -> Dict[str, Any]:
        """テキストの発話タイミングデータを取得
        
        Args:
            text: タイミングデータを取得するテキスト
            speaker_id: 話者ID
            
        Returns:
            タイミングデータ
            
        Raises:
            ValueError: テキストが空の場合、または話者IDが不正な場合
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        
        if speaker_id < 1:
            raise ValueError("invalid speaker id")
        
        try:
            # 音声合成用のクエリを作成（アクセント情報を含む）
            query_params: Dict[str, str] = {
                "text": text,
                "speaker": str(speaker_id)
            }
            query_response = requests.post(
                f"{self.base_url}/audio_query",
                params=query_params,
                timeout=30
            )
            query_response.raise_for_status()
            query = query_response.json()
            
            # アクセント句情報を取得
            accent_phrases = query.get("accent_phrases", [])
            
            # タイミング情報を構築
            timing_data = []
            current_position = 0.0
            
            for phrase in accent_phrases:
                for mora in phrase.get("moras", []):
                    timing_data.append({
                        "text": mora.get("text", ""),
                        "phoneme": mora.get("consonant", "") or mora.get("vowel", ""),
                        "start_time": current_position,
                        "end_time": current_position + mora.get("consonant_length", 0.0) + mora.get("vowel_length", 0.0)
                    })
                    current_position = timing_data[-1]["end_time"]
            
            return {"timing": timing_data, "duration": current_position}
            
        except (ConnectionError, Timeout) as e:
            error_message = f"Connection error with VoiceVox API: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except RequestException as e:
            error_message = f"Error calling VoiceVox API: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except (ValueError, KeyError) as e:
            error_message = f"Error parsing VoiceVox API response: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except Exception as e:
            error_message = f"Unexpected error in get_timing_data: {str(e)}"
            logger.exception(error_message)
            raise VoiceVoxServiceError(error_message)
    
    def synthesize_voice(self, text: str, speaker_id: int = 1) -> AudioSynthesisResult:
        """音声合成を行い、音声ファイルとタイミングデータを取得
        
        Args:
            text: 音声化するテキスト
            speaker_id: 話者ID
            
        Returns:
            AudioSynthesisResult: 音声合成結果（ファイルパスとタイミングデータを含む）
            
        Raises:
            ValueError: テキストが空の場合、または話者IDが不正な場合
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        
        if speaker_id < 1:
            raise ValueError("invalid speaker id")
        
        try:
            # タイミングデータを取得
            timing_result = self.get_timing_data(text, speaker_id)
            timing_data = timing_result.get("timing", [])
            duration = timing_result.get("duration", 0.0)
            
            # 音声を生成
            audio_data = self.generate_voice(text, speaker_id)
            
            # ファイル名を生成（話者IDとテキストの先頭を含める）
            safe_text = ''.join(c for c in text[:10] if c.isalnum() or c.isspace()).strip()
            timestamp = int(time.time())
            filename = f"voice_{speaker_id}_{safe_text}_{timestamp}.wav"
            file_path = os.path.join(self.output_dir, filename)
            
            # 音声データを保存
            with open(file_path, "wb") as f:
                f.write(audio_data)
            
            # タイミングデータをPydanticモデルに変換
            speech_timing_data = [
                SpeechTimingData(
                    start_time=item.get("start_time", 0.0),
                    end_time=item.get("end_time", 0.0),
                    phoneme=item.get("phoneme", ""),
                    text=item.get("text", "")
                )
                for item in timing_data
            ]
            
            # 結果を返す
            return AudioSynthesisResult(
                file_path=file_path,
                timing_data=speech_timing_data,
                duration=duration,
                text=text,
                speaker_id=speaker_id
            )
            
        except (ValueError, VoiceVoxServiceError) as e:
            # エラーをそのまま再送出
            raise
        except Exception as e:
            error_message = f"Unexpected error in synthesize_voice: {str(e)}"
            logger.exception(error_message)
            raise VoiceVoxServiceError(error_message)
    
    def get_speakers(self) -> List[Dict[str, Any]]:
        """利用可能な話者の一覧を取得
        
        Returns:
            話者情報のリスト
            
        Raises:
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        try:
            # 話者一覧を取得
            response = requests.get(
                f"{self.base_url}/speakers",
                timeout=10
            )
            response.raise_for_status()
            
            speakers_data = response.json()
            if not isinstance(speakers_data, list):
                logger.error(f"Unexpected speakers data format: {type(speakers_data)}")
                return []
            
            return cast(List[Dict[str, Any]], speakers_data)
            
        except (ConnectionError, Timeout) as e:
            error_message = f"Connection error with VoiceVox API: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except RequestException as e:
            error_message = f"Error calling VoiceVox API: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except (ValueError, KeyError) as e:
            error_message = f"Error parsing VoiceVox API response: {str(e)}"
            logger.error(error_message)
            raise VoiceVoxServiceError(error_message)
        except Exception as e:
            error_message = f"Unexpected error in get_speakers: {str(e)}"
            logger.exception(error_message)
            raise VoiceVoxServiceError(error_message)
    
    def list_speakers(self) -> List[VoiceVoxSpeaker]:
        """利用可能な話者の一覧をVoiceVoxSpeakerモデルで取得
        
        Returns:
            話者情報のリスト
            
        Raises:
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        try:
            # 話者一覧を取得
            speakers_data = self.get_speakers()
            result = []
            
            for speaker in speakers_data:
                speaker_name = speaker.get("name", "")
                speaker_uuid = speaker.get("speaker_uuid", "")
                
                for style in speaker.get("styles", []):
                    style_id = style.get("id", 0)
                    style_name = style.get("name", "")
                    
                    if style_id > 0:
                        result.append(VoiceVoxSpeaker(
                            id=style_id,
                            name=speaker_name,
                            style_id=style_id,
                            style_name=style_name
                        ))
            
            return result
            
        except VoiceVoxServiceError:
            # エラーをそのまま再送出
            raise
        except Exception as e:
            error_message = f"Unexpected error in list_speakers: {str(e)}"
            logger.exception(error_message)
            raise VoiceVoxServiceError(error_message)

    def check_availability(self) -> Dict[str, Any]:
        """VoiceVoxサービスの可用性と情報を確認
        
        Returns:
            状態情報の辞書 {"available": bool, "speakers": int, "error": Optional[str]}
        """
        result = {
            "available": False,
            "speakers": 0,
            "error": None,
            "version": None,
            "response_time_ms": 0
        }
        
        try:
            import time
            start_time = time.time()
            
            # バージョン情報を取得
            version_resp = requests.get(f"{self.base_url}/version", timeout=5)
            version_resp.raise_for_status()
            result["version"] = version_resp.text
            
            # 話者情報を取得
            speakers = self.list_speakers()
            
            # 情報を設定
            result["available"] = True
            result["speakers"] = len(speakers)
            
            # 応答時間を計算（ミリ秒）
            end_time = time.time()
            result["response_time_ms"] = int((end_time - start_time) * 1000)
            
        except (ConnectionError, Timeout) as e:
            result["error"] = f"Connection error: {str(e)}"
            logger.warning(f"VoiceVox service connection error: {str(e)}")
        except RequestException as e:
            result["error"] = f"Request error: {str(e)}"
            logger.warning(f"VoiceVox service request error: {str(e)}")
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
            logger.warning(f"Unexpected error checking VoiceVox availability: {str(e)}")
        
        return result
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """詳細なステータス情報を取得
        
        Returns:
            詳細なステータス情報の辞書
        """
        status = {
            "base_url": self.base_url,
            "available": False,
            "version": None,
            "speakers_count": 0,
            "error": None,
            "response_time_ms": 0
        }
        
        # 可用性チェック
        availability = self.check_availability()
        status.update({
            "available": availability["available"],
            "speakers_count": availability["speakers"],
            "version": availability["version"],
            "error": availability["error"],
            "response_time_ms": availability["response_time_ms"]
        })
        
        return status 