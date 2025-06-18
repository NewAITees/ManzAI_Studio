"""
ManzAI Studioのメインパッケージ
"""

from src.backend.app import create_app
from src.backend.app.config import Config

__all__ = ["Config", "create_app"]
