"""漫才スクリプトのデータモデル定義"""

from enum import Enum
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator, model_validator


class Role(str, Enum):
    """漫才の役割を表す列挙型"""
    TSUKKOMI = "tsukkomi"
    BOKE = "boke"


class ScriptLine(BaseModel):
    """漫才スクリプトの1行を表すモデル"""
    role: Role = Field(..., description="セリフの発話者の役割")
    text: str = Field(..., description="セリフの内容")

    @field_validator("text")
    @classmethod
    def text_cannot_be_empty(cls, v: str) -> str:
        """テキストが空でないことを検証"""
        if not v or not v.strip():
            raise ValueError("セリフの内容は空にできません")
        return v.strip()


class ManzaiScript(BaseModel):
    """漫才スクリプト全体を表すモデル"""
    script: List[ScriptLine] = Field(default_factory=list, description="スクリプトの行")
    topic: Optional[str] = Field(None, description="スクリプトのトピック")

    @model_validator(mode='after')
    def script_must_have_lines(self) -> 'ManzaiScript':
        """スクリプトが少なくとも1行あることを検証"""
        if not self.script:
            raise ValueError("スクリプトは少なくとも1行必要です")
        return self


class GenerateScriptRequest(BaseModel):
    """スクリプト生成リクエストを表すモデル"""
    topic: str = Field(..., description="漫才のトピック")
    model: str = Field("llama3", description="使用するモデル名")
    use_mock: bool = Field(False, description="モックデータを使用するかどうか")

    @field_validator("topic")
    @classmethod
    def topic_cannot_be_empty(cls, v: str) -> str:
        """トピックが空でないことを検証"""
        if not v or not v.strip():
            raise ValueError("トピックは空にできません")
        return v.strip()


class AudioMetadata(BaseModel):
    """音声メタデータを表すモデル"""
    filename: str = Field(..., description="音声ファイル名")
    duration: float = Field(..., description="音声の長さ（秒）")
    line_index: int = Field(..., description="対応するスクリプト行のインデックス")


class GenerateScriptResponse(BaseModel):
    """スクリプト生成レスポンスを表すモデル"""
    topic: str = Field("", description="リクエストされたトピック")
    model: str = Field("llama3", description="使用されたモデル名")
    script: List[ScriptLine] = Field(default_factory=list, description="生成されたスクリプト")
    audio_data: List[AudioMetadata] = Field(default_factory=list, description="音声データ情報")
    error: Optional[str] = Field(None, description="エラーメッセージ（該当する場合）") 