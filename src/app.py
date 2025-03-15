"""
ManzAI Studioのメインアプリケーションモジュール
"""
import os
import json
import logging
import subprocess
import threading
import time
from typing import Dict, List, Any, Optional, Tuple, Union, cast

from flask import Flask, request, jsonify, send_from_directory, Response, send_file, redirect
from flask_cors import CORS
import traceback
from pydantic import ValidationError, BaseModel
from werkzeug.exceptions import BadRequest

# サービスのインポート
from src.services.ollama_service import OllamaService, OllamaServiceError
from src.services.voicevox_service import VoiceVoxService, VoiceVoxServiceError
from src.utils.audio_manager import AudioManager, AudioFileNotFoundError
from src.utils.mock_data import get_mock_script, get_mock_script_model
from src.models.script import GenerateScriptRequest, GenerateScriptResponse, ManzaiScript
from src.models.service import ServiceStatus, OllamaStatus, VoiceVoxStatus
from src.models.script import ScriptLine, Role
from src.routes import api as api_routes

# 開発モードの設定
development_mode = os.environ.get("FLASK_ENV", "development") == "development"
# テスト用のフラグ
testing_mode = False

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# モデル定義
class OllamaModel(BaseModel):
    name: str
    modified_at: int
    size: int
    digest: str
    details: Dict[str, Any] = {}

def create_app():
    """Flaskアプリケーションを作成する"""
    app = Flask(__name__)
    
    # 環境変数から設定を読み込む
    app.config.from_object('src.config.Config')
    
    # 環境変数から接続先URLを取得
    voicevox_url = os.environ.get('VOICEVOX_URL', 'http://localhost:50021')
    ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
    ollama_model = os.environ.get('OLLAMA_MODEL', 'gemma3:4b')
    ollama_instance_type = os.environ.get('OLLAMA_INSTANCE_TYPE', 'auto')
    
    # サービスの初期化
    voicevox_service = VoiceVoxService(base_url=voicevox_url)
    ollama_service = OllamaService(
        base_url=ollama_url,
        instance_type=ollama_instance_type
    )
    audio_manager = AudioManager(audio_dir=app.config['AUDIO_DIR'])
    
    # サービスをアプリケーションに保存
    app.voicevox_service = voicevox_service
    app.ollama_service = ollama_service
    app.audio_manager = audio_manager
    
    # APIルートを登録
    app.register_blueprint(api_routes.bp)
    
    CORS(app)  # クロスオリジンリクエストを許可

    # サービスの初期化
    audio_manager = AudioManager(audio_dir="audio")

    # テスト用の設定の初期化関数
    def init_testing_mode():
        """テストモードを有効化"""
        global testing_mode
        testing_mode = True
        return True

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

    @app.route("/api/status", methods=["GET"])
    def status() -> Response:
        """
        サービスのステータス情報を返すエンドポイント
        
        Returns:
            Response: OllamaとVoiceVoxのステータス情報
        """
        try:
            # Ollamaのステータスチェック
            ollama_available = False
            ollama_models: List[OllamaModel] = []
            ollama_error = None
            ollama_details = {}
            
            try:
                # 詳細情報を取得
                ollama_status = ollama_service.get_detailed_status()
                ollama_available = ollama_status.get("available", False)
                
                # モデルリストを取得
                ollama_models_data = ollama_service.list_models()
                
                # モデルリストをOllamaModelに変換
                ollama_models = [
                    OllamaModel(
                        name=model.get("name", ""),
                        modified_at=model.get("modified_at", 0),
                        size=model.get("size", 0),
                        digest=model.get("digest", ""),
                        details=model
                    )
                    for model in ollama_models_data
                ]
                
                # 詳細情報を追加
                ollama_details = {
                    "instance_type": ollama_status.get("instance_type"),
                    "api_version": ollama_status.get("api_version"),
                    "base_url": ollama_status.get("base_url"),
                    "response_time_ms": ollama_status.get("response_time_ms")
                }
                
            except OllamaServiceError as e:
                ollama_error = str(e)
                logger.error(f"Ollama status check failed: {e}")
            
            # VoiceVoxのステータスチェック
            voicevox_available = False
            voicevox_speakers = []
            voicevox_error = None
            voicevox_details = {}
            
            try:
                # 詳細情報を取得
                voicevox_status = voicevox_service.get_detailed_status()
                voicevox_available = voicevox_status.get("available", False)
                
                # 話者リストを取得
                voicevox_speakers = voicevox_service.list_speakers()
                
                # 詳細情報を追加
                voicevox_details = {
                    "version": voicevox_status.get("version"),
                    "base_url": voicevox_status.get("base_url"),
                    "response_time_ms": voicevox_status.get("response_time_ms")
                }
                
            except VoiceVoxServiceError as e:
                voicevox_error = str(e)
                logger.error(f"VoiceVox status check failed: {e}")
            
            # レスポンスの構築
            status_data = ServiceStatus(
                ollama=OllamaStatus(
                    available=ollama_available,
                    models=ollama_models,
                    error=ollama_error,
                    instance_type=ollama_details.get("instance_type"),
                    api_version=ollama_details.get("api_version"),
                    base_url=ollama_details.get("base_url"),
                    response_time_ms=ollama_details.get("response_time_ms")
                ),
                voicevox=VoiceVoxStatus(
                    available=voicevox_available,
                    speakers=voicevox_speakers,
                    error=voicevox_error,
                    version=voicevox_details.get("version"),
                    base_url=voicevox_details.get("base_url"),
                    response_time_ms=voicevox_details.get("response_time_ms")
                )
            )
            
            return cast(Response, jsonify(status_data.model_dump()))
        except Exception as e:
            logger.exception(f"Error getting status: {e}")
            return cast(Response, jsonify({
                "error": str(e)
            }))

    @app.route("/api/generate-script", methods=["POST"])
    def generate_script() -> Tuple[Response, int]:
        """
        漫才台本生成エンドポイント
        
        Returns:
            Tuple[Response, int]: 生成された台本とステータスコード
        """
        try:
            # リクエストデータの取得と検証
            if not request.is_json:
                raise BadRequest("Request must be JSON")
            
            data = request.get_json()
            
            # Pydanticモデルを使用してリクエストを検証
            try:
                script_request = GenerateScriptRequest(**data)
            except Exception as e:
                logger.error(f"Invalid request data: {e}")
                return jsonify({"error": f"Invalid request data: {e}"}), 400
            
            # 台本生成の実行
            try:
                topic = script_request.topic
                model = script_request.model
                
                # 開発モードまたはテストモードの場合はモックデータを返す
                if development_mode or testing_mode:
                    logger.info("Using mock data in development/testing mode")
                    mock_script = get_mock_script_model(topic=script_request.topic)
                    
                    response = GenerateScriptResponse(
                        topic=script_request.topic,
                        model=script_request.model,
                        script=mock_script.script,
                        error=None
                    )
                    
                    return jsonify(response.model_dump()), 200
                    
                script_items = ollama_service.generate_manzai_script(topic, model_name=model)
                
                # ScriptLineのリストに変換
                script_lines = [
                    ScriptLine(
                        role=Role(item["role"]),
                        text=item["text"]
                    )
                    for item in script_items
                ]
                
                response = GenerateScriptResponse(
                    topic=topic,
                    model=model,
                    script=script_lines,
                    error=None
                )
                
                return jsonify(response.model_dump()), 200
                
            except Exception as e:
                logger.error(f"Error generating script: {e}")
                
                # 開発モードの場合はモックデータを返す
                if development_mode:
                    logger.info("Using mock data in development mode")
                    mock_script = get_mock_script_model(topic=script_request.topic)
                    
                    response = GenerateScriptResponse(
                        topic=script_request.topic,
                        model=script_request.model,
                        script=mock_script.script,
                        error=str(e)
                    )
                    
                    return jsonify(response.model_dump()), 200
                else:
                    return jsonify({"error": str(e)}), 500
        
        except BadRequest as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/audio/<filename>", methods=["GET"])
    def get_audio(filename: str) -> Union[Response, Tuple[Response, int]]:
        """
        音声ファイルを提供するエンドポイント
        
        Args:
            filename: 音声ファイル名
            
        Returns:
            Response: 音声ファイルまたはエラーレスポンス
        """
        try:
            file_path = audio_manager.get_audio(filename)
            return send_file(file_path, mimetype="audio/wav")
        except AudioFileNotFoundError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            logger.exception(f"Error serving audio file: {e}")
            return jsonify({"error": str(e)}), 500

    @app.route("/api/generate", methods=["POST"])
    def generate_redirect() -> Response:
        """
        /api/generateへのリクエストを/api/generate-scriptにリダイレクト
        
        Returns:
            Response: リダイレクトレスポンス
        """
        return generate_script()

    @app.route("/api/speakers", methods=["GET"])
    def speakers() -> Response:
        """
        話者一覧を提供するエンドポイント
        
        Returns:
            Response: 利用可能な話者一覧
        """
        try:
            status_data = status()
            if isinstance(status_data, tuple):
                return status_data
            
            # statusレスポンスからvoicevoxの話者情報を抽出
            response_data = json.loads(status_data.data)
            speakers_data = response_data.get("voicevox", {}).get("speakers", [])
            
            return cast(Response, jsonify(speakers_data))
        except Exception as e:
            logger.exception(f"Error getting speakers: {e}")
            return cast(Response, jsonify({
                "error": str(e)
            })), 500

    def start_frontend():
        """フロントエンド開発サーバーを別スレッドで起動する"""
        frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
        
        # ポート3000が既に使用中かチェック
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port_in_use = False
        try:
            sock.bind(('localhost', 3000))
        except socket.error:
            port_in_use = True
        finally:
            sock.close()
        
        # 既にフロントエンドサーバーが起動している場合は何もしない
        if port_in_use:
            logger.info("フロントエンド開発サーバーは既に実行中です")
            return
        
        def run_frontend_server():
            try:
                # 環境変数PATHを継承しつつnpmコマンドを実行
                env = os.environ.copy()
                subprocess.run(["npm", "start"], cwd=frontend_dir, env=env)
            except Exception as e:
                logger.error(f"フロントエンドサーバーの起動に失敗しました: {e}")
        
        # 別スレッドでフロントエンドサーバーを起動
        frontend_thread = threading.Thread(target=run_frontend_server)
        frontend_thread.daemon = True  # メインプロセスが終了したら子プロセスも終了
        frontend_thread.start()
        logger.info("フロントエンド開発サーバーを起動しました")

    def run() -> None:
        """アプリケーションを実行する"""
        # 開発モードの場合はフロントエンドサーバーも起動
        if os.environ.get("FLASK_ENV") == "development" or app.config["DEBUG"]:
            start_frontend()
        
        app.run(host="0.0.0.0", port=5000)

    return app

if __name__ == "__main__":
    # 直接実行された場合
    app = create_app()
    app.run() 