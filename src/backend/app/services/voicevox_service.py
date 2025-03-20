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
    
    def get_fallback_audio(self, text: str) -> bytes:
        """フォールバック用の音声データを生成

        Args:
            text: 読み上げるテキスト

        Returns:
            音声データ（バイト列）
        """
        logger.warning(f"Using fallback audio for text: {text}")
        
        # 簡単な無音データを生成（1秒間の44.1kHz、16bitのモノラル無音）
        sample_rate = 44100
        duration = 1  # 1秒
        num_samples = sample_rate * duration
        
        # 16bitの無音データを生成（0x8000で中央値を設定）
        silence_data = bytearray()
        for _ in range(num_samples):
            silence_data.extend([0x00, 0x80])  # リトルエンディアンで0x8000を追加
        
        return bytes(silence_data)

    def generate_voice(self, text: str, speaker_id: int) -> bytes:
        """テキストから音声を生成します。

        Args:
            text (str): 音声化するテキスト
            speaker_id (int): 話者ID

        Returns:
            bytes: 生成された音声データ

        Raises:
            ValueError: テキストが空の場合、または話者IDが無効な場合
            VoiceVoxServiceError: VoiceVoxサービスとの通信に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        if not isinstance(speaker_id, int) or speaker_id < 0:
            raise ValueError("invalid speaker id")

        try:
            # 音声合成のクエリを作成
            query_response = requests.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": speaker_id},
                timeout=30  # タイムアウトを30秒に設定
            )
            if query_response.status_code >= 400:
                error_msg = f"VoiceVox API returned error status: {query_response.status_code}"
                logging.error(error_msg)
                raise VoiceVoxServiceError(error_msg)
            query_data = query_response.json()

            # 音声を合成
            synthesis_response = requests.post(
                f"{self.base_url}/synthesis",
                params={"speaker": speaker_id},
                json=query_data,
                timeout=30  # タイムアウトを30秒に設定
            )
            if synthesis_response.status_code >= 400:
                error_msg = f"VoiceVox API returned error status: {synthesis_response.status_code}"
                logging.error(error_msg)
                raise VoiceVoxServiceError(error_msg)
            return synthesis_response.content

        except requests.exceptions.Timeout:
            error_msg = "Timeout error occurred while communicating with VoiceVox API"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error with VoiceVox API"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with VoiceVox API: {str(e)}"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in VoiceVox service: {str(e)}"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
    
    def get_timing_data(self, text: str, speaker_id: int = 1) -> Dict[str, Any]:
        """
        テキストの音声合成に必要なタイミングデータを取得します。

        Args:
            text (str): タイミングデータを取得するテキスト
            speaker_id (int): 話者ID

        Returns:
            Dict[str, Any]: タイミングデータ（accent_phrases, speedScale, pitchScale等を含む）

        Raises:
            ValueError: テキストが空の場合、または話者IDが無効な場合
            VoiceVoxServiceError: VoiceVoxサービスとの通信に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        if not isinstance(speaker_id, int) or speaker_id < 0:
            raise ValueError("invalid speaker id")

        try:
            response = requests.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": speaker_id}
            )
            if response.status_code >= 400:
                error_msg = f"VoiceVox API returned error status: {response.status_code}"
                logging.error(error_msg)
                raise VoiceVoxServiceError(error_msg)
            return response.json()

        except requests.exceptions.ConnectionError:
            error_msg = "Connection error with VoiceVox API"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with VoiceVox API: {str(e)}"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in VoiceVox service: {str(e)}"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
    
    def synthesize_voice(self, text: str, speaker_id: int = 1) -> AudioSynthesisResult:
        """
        テキストから音声を合成し、ファイルに保存します。

        Args:
            text (str): 音声化するテキスト
            speaker_id (int): 話者ID

        Returns:
            AudioSynthesisResult: 生成された音声ファイルのパスとタイミングデータ

        Raises:
            ValueError: テキストが空の場合、または話者IDが無効な場合
            VoiceVoxServiceError: VoiceVoxサービスとの通信に失敗した場合
        """
        if not text:
            raise ValueError("text cannot be empty")
        if not isinstance(speaker_id, int) or speaker_id < 0:
            raise ValueError("invalid speaker id")

        try:
            # タイミングデータを取得
            timing_data = self.get_timing_data(text, speaker_id)

            # 音声を生成
            audio_data = self.generate_voice(text, speaker_id)

            # ファイルに保存
            timestamp = int(time.time())
            file_path = os.path.join(self.output_dir, f"{timestamp}_{speaker_id}.wav")
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'wb') as f:
                f.write(audio_data)

            # タイミングデータを変換
            speech_timing_data = []
            total_duration = 0.0

            for phrase in timing_data.get('accent_phrases', []):
                for mora in phrase.get('moras', []):
                    start_time = total_duration
                    duration = mora.get('consonant_length', 0.0) + mora.get('vowel_length', 0.0)
                    end_time = start_time + duration
                    
                    speech_timing_data.append(SpeechTimingData(
                        start_time=start_time,
                        end_time=end_time,
                        phoneme=mora.get('consonant', '') + mora.get('vowel', ''),
                        text=mora.get('text', '')
                    ))
                    
                    total_duration = end_time

            return AudioSynthesisResult(
                file_path=file_path,
                timing_data=speech_timing_data,
                duration=total_duration,
                text=text,
                speaker_id=speaker_id
            )

        except (ValueError, VoiceVoxServiceError) as e:
            raise e
        except Exception as e:
            error_msg = f"Unexpected error in synthesize_voice: {str(e)}"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
    
    def get_speakers(self) -> List[Dict[str, Any]]:
        """
        利用可能な話者のリストを取得します。

        Returns:
            List[Dict[str, Any]]: 話者情報のリスト

        Raises:
            VoiceVoxServiceError: VoiceVoxサービスとの通信に失敗した場合
        """
        try:
            response = requests.get(f"{self.base_url}/speakers")
            if response.status_code >= 400:
                error_msg = f"VoiceVox API returned error status: {response.status_code}"
                logging.error(error_msg)
                raise VoiceVoxServiceError(error_msg)
            return response.json()
        except requests.exceptions.ConnectionError:
            error_msg = "Connection error with VoiceVox API"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with VoiceVox API: {str(e)}"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error in VoiceVox service: {str(e)}"
            logging.error(error_msg)
            raise VoiceVoxServiceError(error_msg)
    
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

    def synthesize(self, text: str, speaker_id: int = 1) -> bytes:
        """generate_voiceのエイリアス

        Args:
            text: 音声化するテキスト
            speaker_id: 話者ID

        Returns:
            bytes: 生成された音声データ

        Raises:
            ValueError: テキストが空の場合、または話者IDが不正な場合
            VoiceVoxServiceError: サービスとの通信に失敗した場合
        """
        return self.generate_voice(text, speaker_id) 