"""Configuration settings for the backend application."""

import os

from pydantic import BaseModel, Field


class BaseConfig(BaseModel):
    """ベース設定モデル"""

    TESTING: bool = Field(False, description="テストモードかどうか")
    VOICEVOX_URL: str = Field(
        default_factory=lambda: os.getenv("VOICEVOX_URL", "http://localhost:50021"),
        description="VoiceVox API URL",
    )
    OLLAMA_URL: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_URL", "http://localhost:11434"),
        description="Ollama API URL",
    )
    OLLAMA_MODEL: str = Field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "phi"),
        description="OllamaのデフォルトモデルID",
    )
    AUDIO_OUTPUT_DIR: str = Field(
        default_factory=lambda: os.getenv("AUDIO_OUTPUT_DIR", "./audio"),
        description="音声ファイル出力ディレクトリ",
    )

    model_config = {
        "env_prefix": "",  # 環境変数の接頭辞（なし）
        "validate_assignment": True,  # 代入時にバリデーションを行う
    }


class TestConfig(BaseConfig):
    """テスト環境の設定"""

    TESTING: bool = Field(True, description="テストモードかどうか")
    VOICEVOX_URL: str = Field("http://voicevox:50021", description="VoiceVox API URL (テスト環境)")
    OLLAMA_URL: str = Field("http://ollama:11434", description="Ollama API URL (テスト環境)")


class DevelopmentConfig(BaseConfig):
    """開発環境の設定"""

    DEBUG: bool = Field(True, description="デバッグモードかどうか")
    VOICEVOX_URL: str = Field("http://voicevox:50021", description="VoiceVox API URL (開発環境)")
    OLLAMA_URL: str = Field("http://ollama:11434", description="Ollama API URL (開発環境)")


class ProductionConfig(BaseConfig):
    """本番環境の設定"""

    DEBUG: bool = Field(False, description="デバッグモードかどうか")


def get_config() -> BaseConfig:
    """環境に基づいた設定を取得する

    Returns:
        環境に応じた設定インスタンス
    """
    env = os.getenv("FLASK_ENV", "development")

    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestConfig()
    else:
        return DevelopmentConfig()


config = get_config()

# 後方互換性のために BaseConfig を Config としてエクスポート
Config = BaseConfig
