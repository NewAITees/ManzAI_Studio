"""
ManzAI Studioのメインアプリケーションモジュール
"""

import logging
import os
from typing import Any, Dict, Optional, cast

import psutil
from flask import Flask, Response, jsonify
from flask_cors import CORS

from src.backend.app.config import Config, get_config
from src.backend.app.routes.api import api_bp
from src.backend.app.services.audio_manager import AudioManager
from src.backend.app.services.ollama_service import OllamaService
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.utils.error_handlers import register_error_handlers
from src.backend.app.utils.exceptions import ContentTypeError

# テスト用のフラグ
testing_mode = False


def init_testing_mode() -> bool:
    """テストモードを有効化"""
    global testing_mode
    testing_mode = True
    return True


# ロガーの設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_app(config: Optional[Config] = None) -> Flask:
    """アプリケーションファクトリ関数

    Args:
        config: 設定オブジェクト（オプション）

    Returns:
        Flask: 設定済みのFlaskアプリケーション
    """
    app = Flask(__name__)
    CORS(app)

    # 設定の読み込み
    if config is None:
        config = get_config()

    # 設定の適用
    app.config.update(
        DEVELOPMENT=getattr(config, "DEBUG", False),
        TESTING=testing_mode or getattr(config, "TESTING", False),
        VOICEVOX_URL=config.VOICEVOX_URL,
        OLLAMA_URL=config.OLLAMA_URL,
        OLLAMA_MODEL=config.OLLAMA_MODEL,
    )

    # サービスの初期化
    app.ollama_service = OllamaService(base_url=config.OLLAMA_URL)
    app.voicevox_service = VoiceVoxService(base_url=config.VOICEVOX_URL)
    app.audio_manager = AudioManager()

    # エラーハンドラの登録
    register_error_handlers(app)

    # ブループリントの登録
    app.register_blueprint(api_bp)

    @app.route("/", methods=["GET"])
    def index() -> Response:
        """
        ルートエンドポイント

        Returns:
            Response: APIステータス情報
        """
        return cast(
            Response,
            jsonify({"status": "ok", "message": "ManzAI Studio API is running"}),
        )

    return app


# アプリケーションインスタンスの作成
app = create_app()
