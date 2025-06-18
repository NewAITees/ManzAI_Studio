"""
Input validation utilities for ManzAI Studio API.

This module provides Pydantic models for validating input data for API endpoints.
It includes validation for models, prompts, script generation parameters, etc.
"""

import os
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field, field_validator
from werkzeug.datastructures import FileStorage


class ModelType(str, Enum):
    """モデルタイプの列挙型"""

    TSUKKOMI = "tsukkomi"
    BOKE = "boke"
    UNKNOWN = "unknown"


class ModelData(BaseModel):
    """モデル登録データのバリデーション用モデル"""

    name: str = Field(..., description="モデル名")
    type: ModelType = Field(..., description="モデルタイプ")
    description: Optional[str] = Field(None, description="モデルの説明")
    metadata: Optional[Dict[str, Any]] = Field(None, description="追加のメタデータ")

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        """モデル名が空でないことを検証"""
        if not v.strip():
            raise ValueError("モデル名は空にできません")
        return v


class PromptData(BaseModel):
    """プロンプトデータのバリデーション用モデル"""

    name: str = Field(..., description="プロンプト名")
    content: str = Field(..., description="プロンプト内容")
    description: Optional[str] = Field(None, description="プロンプトの説明")
    tags: List[str] = Field(default_factory=list, description="プロンプトのタグ")

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """プロンプト名のフォーマットを検証"""
        if not v.strip():
            raise ValueError("プロンプト名は空にできません")
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(
                "プロンプト名は英数字、アンダースコア、ハイフンのみを含むことができます"
            )
        return v

    @field_validator("content")
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        """プロンプト内容が空でないことを検証"""
        if not v.strip():
            raise ValueError("プロンプト内容は空にできません")
        return v

    @field_validator("tags", each_item=True)
    @classmethod
    def tags_must_be_strings(cls, v: str) -> str:
        """各タグが文字列であることを検証"""
        if not isinstance(v, str):
            raise ValueError("各タグは文字列である必要があります")
        return v


class ScriptParams(BaseModel):
    """スクリプト生成パラメータのバリデーション用モデル"""

    topic: str = Field(..., description="生成するスクリプトのトピック")
    prompt_name: Optional[str] = Field(None, description="使用するプロンプト名")
    max_length: int = Field(1000, ge=100, le=2000, description="生成する最大トークン数")
    temperature: float = Field(0.7, ge=0, le=2, description="生成の多様性")

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_empty(cls, v: str) -> str:
        """トピックが空でないことを検証"""
        if not v.strip():
            raise ValueError("トピックは空にできません")
        return v.strip()


# 以前の関数ベースのバリデーションの互換性維持のための関数


def validate_model_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate model registration data using Pydantic model.

    Args:
        data: Dictionary containing model data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ModelData(**data)
        return True, ""
    except Exception as e:
        return False, str(e)


def validate_prompt_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate prompt data for creation or update using Pydantic model.

    Args:
        data: Dictionary containing prompt data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        PromptData(**data)
        return True, ""
    except Exception as e:
        return False, str(e)


def validate_script_params(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate script generation parameters using Pydantic model.

    Args:
        data: Dictionary containing script generation parameters

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ScriptParams(**data)
        return True, ""
    except Exception as e:
        return False, str(e)


class FileValidationResult(BaseModel):
    """ファイル検証結果モデル"""

    is_valid: bool = Field(False, description="ファイルが有効かどうか")
    error_message: str = Field("", description="エラーメッセージ（該当する場合）")


def validate_model_file(file: FileStorage) -> Tuple[bool, str]:
    """
    Validate a model file upload

    Args:
        file: The uploaded file

    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"

    # Check file extension
    allowed_extensions = [".model3.json", ".zip"]
    filename = file.filename or ""  # Ensure filename is not None
    file_ext = os.path.splitext(filename)[-1].lower()

    if file_ext not in allowed_extensions:
        return (
            False,
            f"Invalid file extension: {file_ext}. Must be one of {allowed_extensions}",
        )

    # Check file size (max 50MB)
    if file.content_length > 50 * 1024 * 1024:  # 50MB in bytes
        return False, "File too large. Maximum size is 50MB"

    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal and other security issues.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename
    """
    # Remove path separators and ensure only allowed characters
    sanitized = re.sub(r"[^\w\.-]", "_", os.path.basename(filename))

    # Ensure it's not empty and doesn't start with a period
    if not sanitized or sanitized.startswith("."):
        sanitized = "file_" + sanitized

    return sanitized
