"""
ManzAI Studioのメインアプリケーションモジュール
"""
import os
import logging
from typing import Dict, Any, cast, Optional
from flask import Flask, Response, jsonify
from flask_cors import CORS

from src.backend.app.config import Config, get_config
from src.backend.app.services.ollama_service import OllamaService
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.utils.audio_manager import AudioManager
from src.backend.app.utils.exceptions import ContentTypeError

# テスト用のフラグ
testing_mode = False

def init_testing_mode():
    """テストモードを有効化"""
    global testing_mode
    testing_mode = True
    return True

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
        DEVELOPMENT=getattr(config, 'DEBUG', False),
        TESTING=testing_mode or getattr(config, 'TESTING', False),
        VOICEVOX_URL=config.VOICEVOX_URL,
        OLLAMA_URL=config.OLLAMA_URL,
        OLLAMA_MODEL=config.OLLAMA_MODEL
    )

    # サービスの初期化
    app.ollama_service = OllamaService(base_url=config.OLLAMA_URL)
    app.voicevox_service = VoiceVoxService(base_url=config.VOICEVOX_URL)
    app.audio_manager = AudioManager()

    # ブループリントの登録
    from src.backend.app.routes import api
    app.register_blueprint(api.bp)

    # エラーハンドラーの登録
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": str(e)}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(ContentTypeError)
    def handle_content_type_error(e):
        """Content-Typeエラーのハンドラ"""
        return jsonify({'error': str(e)}), 415

    @app.route("/", methods=["GET"])
    def index() -> Response:
        """
        ルートエンドポイント
        
        Returns:
            Response: APIステータス情報
        """
        return cast(Response, jsonify({
            "status": "ok",
            "message": "ManzAI Studio API is running"
        }))

    return app

# アプリケーションインスタンスの作成
app = create_app() 