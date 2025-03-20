"""
ManzAI Studioのメインアプリケーションモジュール
"""
import os
import logging
from typing import Dict, Any, cast
from flask import Flask, Response, jsonify
from flask_cors import CORS

from src.backend.app.config import Config
from src.backend.app.services.ollama_service import OllamaService
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.utils.audio_manager import AudioManager
from src.backend.app.utils.exceptions import ContentTypeError

# 開発モードの設定
development_mode = os.environ.get("FLASK_ENV", "development") == "development"
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

def create_app():
    """アプリケーションファクトリ関数"""
    app = Flask(__name__)
    CORS(app)

    # 開発モードの設定
    app.config['DEVELOPMENT'] = development_mode
    app.config['TESTING'] = testing_mode

    # 設定の読み込み
    app.config.from_object('src.backend.app.config.Config')

    # サービスの初期化
    app.ollama_service = OllamaService()
    app.voicevox_service = VoiceVoxService()
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