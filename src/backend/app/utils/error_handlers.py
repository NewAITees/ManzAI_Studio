"""API Error handlers for the Flask application."""
from typing import Dict, Any, Callable, Tuple, List, Union, Optional
from functools import wraps
from flask import jsonify, Response

from pydantic import ValidationError


class APIError(Exception):
    """Custom API error class for handling API errors."""
    
    def __init__(self, message: str, status_code: int = 400, details: Any = None) -> None:
        """Initialize the API error.
        
        Args:
            message: Error message.
            status_code: HTTP status code.
            details: 詳細エラー情報（オプション）
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details


def api_error_handler(f: Callable) -> Callable:
    """Decorator that handles API errors.
    
    Args:
        f: The function to decorate.
        
    Returns:
        Decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Union[Tuple[Response, int], Any]:
        try:
            return f(*args, **kwargs)
        except APIError as e:
            response = {"error": e.message}
            if e.details:
                response["details"] = e.details
            return jsonify(response), e.status_code
        except ValidationError as e:
            # Pydanticのバリデーションエラーを処理
            error_details = []
            for error in e.errors():
                error_details.append({
                    "loc": error["loc"],
                    "msg": error["msg"],
                    "type": error["type"]
                })
            return jsonify({
                "error": "Validation error",
                "details": error_details
            }), 400
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
            
    return decorated


def handle_pydantic_validation_error(e: ValidationError) -> Tuple[Response, int]:
    """Pydanticのバリデーションエラーをレスポンスに変換する
    
    Args:
        e: ValidationErrorインスタンス
        
    Returns:
        エラーレスポンスとステータスコード
    """
    error_details = []
    for error in e.errors():
        error_details.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        })
    
    return jsonify({
        "error": "Validation error",
        "details": error_details
    }), 400 