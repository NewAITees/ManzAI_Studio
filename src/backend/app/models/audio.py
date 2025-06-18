"""音声関連のデータモデル定義"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AudioFile(BaseModel):
    """音声ファイル情報を表すモデル"""

    path: str = Field(..., description="ファイルパス")
    filename: str = Field(..., description="ファイル名")
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    size_bytes: Optional[int] = Field(None, description="ファイルサイズ（バイト）")

    @field_validator("path")
    @classmethod
    def path_must_be_valid(cls, v: str) -> str:
        """パスが空でないことを検証"""
        if not v:
            raise ValueError("ファイルパスは空にできません")
        return v

    @field_validator("filename")
    @classmethod
    def filename_must_be_valid(cls, v: str) -> str:
        """ファイル名が空でないことを検証"""
        if not v:
            raise ValueError("ファイル名は空にできません")
        return v


class SpeechTimingData(BaseModel):
    """音声のタイミングデータを表すモデル"""

    start_time: float = Field(..., description="開始時間（秒）")
    end_time: float = Field(..., description="終了時間（秒）")
    phoneme: str = Field(..., description="音素")
    text: str = Field(..., description="テキスト")

    @field_validator("start_time", "end_time")
    @classmethod
    def time_must_be_positive(cls, v: float) -> float:
        """時間が正の値であることを検証"""
        if v < 0:
            raise ValueError("時間は負の値にできません")
        return v


class AudioSynthesisResult(BaseModel):
    """音声合成結果を表すモデル"""

    file_path: str = Field(..., description="音声ファイルパス")
    timing_data: List[SpeechTimingData] = Field(
        default_factory=list, description="タイミングデータ"
    )
    duration: float = Field(..., description="音声の長さ（秒）")
    text: str = Field(..., description="合成されたテキスト")
    speaker_id: int = Field(..., description="話者ID")
