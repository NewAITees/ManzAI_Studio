"""API Error handlers for the Flask application."""
from typing import Dict, Any, Callable, Tuple
from functools import wraps
from flask import jsonify


class APIError(Exception):
    """Custom API error class for handling API errors."""
    
    def __init__(self, message: str, status_code: int = 400) -> None:
        """Initialize the API error.
        
        Args:
            message: Error message.
            status_code: HTTP status code.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def api_error_handler(f: Callable) -> Callable:
    """Decorator that handles API errors.
    
    Args:
        f: The function to decorate.
        
    Returns:
        Decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs) -> Tuple[Dict[str, Any], int]:
        try:
            return f(*args, **kwargs)
        except APIError as e:
            return jsonify({"error": e.message}), e.status_code
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
            
    return decorated 