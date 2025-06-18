"""
Custom exceptions for the application
"""

from typing import Any


class BaseAppException(Exception):
    """アプリケーションの基本例外クラス"""

    def __init__(self, message: str, code: str | None = None, details: Any = None) -> None:
        self.message = message
        self.code = code or "APP_ERROR"
        self.details = details
        super().__init__(self.message)


class ValidationError(BaseAppException):
    """入力バリデーションエラー"""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, "VALIDATION_ERROR", details)


class APIError(BaseAppException):
    """API関連のエラー"""

    def __init__(self, message: str, status_code: int, details: Any = None) -> None:
        self.status_code = status_code
        super().__init__(message, f"API_ERROR_{status_code}", details)


class ContentTypeError(APIError):
    """不適切なContent-Typeエラー"""

    def __init__(self, message: str = "Unsupported Media Type", details: Any = None) -> None:
        super().__init__(message, 415, details)


class ModelServiceError(BaseAppException):
    """モデルサービス関連のエラー"""

    def __init__(self, message: str, details: Any = None) -> None:
        super().__init__(message, "MODEL_SERVICE_ERROR", details)
