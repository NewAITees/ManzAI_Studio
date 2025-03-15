"""サービス関連のデータモデル定義"""

from typing import Dict, List, Any, Optional

from pydantic import BaseModel, Field


class OllamaModel(BaseModel):
    """Ollamaモデル情報を表すモデル"""
    name: str = Field(..., description="モデル名")
    size: Optional[int] = Field(None, description="モデルサイズ（バイト）")
    modified_at: Optional[str] = Field(None, description="最終更新タイムスタンプ（ISO 8601形式の文字列）")
    digest: Optional[str] = Field(None, description="モデルダイジェスト")
    details: Optional[Dict[str, Any]] = Field(None, description="モデルの詳細情報")


class VoiceVoxSpeaker(BaseModel):
    """VoiceVox話者情報を表すモデル"""
    id: int = Field(..., description="話者ID")
    name: str = Field(..., description="話者名")
    style_id: Optional[int] = Field(None, description="スタイルID")
    style_name: Optional[str] = Field(None, description="スタイル名")


class OllamaStatus(BaseModel):
    """Ollamaサービスの状態を表すモデル"""
    available: bool = Field(False, description="サービスが利用可能かどうか")
    models: Optional[List[OllamaModel]] = Field(None, description="利用可能なモデル一覧")
    error: Optional[str] = Field(None, description="エラーメッセージ（該当する場合）")
    instance_type: Optional[str] = Field(None, description="インスタンスタイプ（local/docker）")
    api_version: Optional[str] = Field(None, description="OllamaのAPIバージョン")
    base_url: Optional[str] = Field(None, description="接続先URL")
    response_time_ms: Optional[int] = Field(None, description="応答時間（ミリ秒）")


class VoiceVoxStatus(BaseModel):
    """VoiceVoxサービスの状態を表すモデル"""
    available: bool = Field(False, description="サービスが利用可能かどうか")
    speakers: Optional[List[VoiceVoxSpeaker]] = Field(None, description="利用可能な話者一覧")
    error: Optional[str] = Field(None, description="エラーメッセージ（該当する場合）")
    version: Optional[str] = Field(None, description="VoiceVoxのバージョン")
    base_url: Optional[str] = Field(None, description="接続先URL")
    response_time_ms: Optional[int] = Field(None, description="応答時間（ミリ秒）")


class ServiceStatus(BaseModel):
    """サービスの状態を表すモデル"""
    ollama: OllamaStatus = Field(
        default_factory=lambda: OllamaStatus(available=False, models=None, error=None),
        description="Ollamaサービスの状態"
    )
    voicevox: VoiceVoxStatus = Field(
        default_factory=lambda: VoiceVoxStatus(available=False, speakers=None, error=None),
        description="VoiceVoxサービスの状態"
    ) 