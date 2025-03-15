import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import traceback

# サービスのインポート
from src.services.ollama_service import OllamaService
from src.services.voicevox_service import VoiceVoxService
from src.utils.audio_manager import AudioManager
from src.utils.mock_data import get_mock_script

# 開発モードの設定
development_mode = os.environ.get("FLASK_ENV", "development") == "development"

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# アプリケーションの初期化
app = Flask(__name__)
CORS(app)  # クロスオリジンリクエストを許可

# サービスの初期化
ollama_service = OllamaService()
voicevox_service = VoiceVoxService()
audio_manager = AudioManager(os.path.join(os.path.dirname(__file__), '..', 'static', 'audio'))

@app.route("/")
def index():
    """
    ルートエンドポイント
    
    Returns:
        サーバーステータス
    """
    return jsonify({"status": "ManzAI studio server is running"})

@app.route("/api/status")
def status():
    """
    サービスの状態を返すエンドポイント
    
    Returns:
        各サービスの状態を含むJSONレスポンス
    """
    status_info = {
        "status": "ok",
        "services": {
            "ollama": "unknown",
            "voicevox": "unknown",
        },
        "development_mode": development_mode
    }
    
    # Ollamaサービスの状態を確認
    try:
        models = ollama_service.list_models()
        status_info["services"]["ollama"] = {
            "status": "connected",
            "models": models
        }
    except Exception as e:
        logger.error(f"Error checking Ollama service: {e}")
        status_info["services"]["ollama"] = {
            "status": "error",
            "error": str(e)
        }
    
    # VoiceVoxサービスの状態を確認
    try:
        speakers = voicevox_service.list_speakers()
        status_info["services"]["voicevox"] = {
            "status": "connected",
            "speakers": speakers
        }
    except Exception as e:
        logger.error(f"Error checking VoiceVox service: {e}")
        status_info["services"]["voicevox"] = {
            "status": "error",
            "error": str(e)
        }
    
    return jsonify(status_info)

@app.route("/api/generate", methods=["POST"])
def generate_script():
    """
    POSTリクエストからトピックを受け取り、マンザイスクリプトを生成するエンドポイント
    
    Returns:
        JSON形式のレスポンス
    """
    try:
        # リクエストデータの取得と検証
        if not request.is_json:
            return jsonify({
                "error": "Content-Type must be application/json",
                "audio_data": [],
                "script": []
            }), 415
        
        data = request.get_json()
        topic = data.get("topic")
        
        # トピックが提供されているか確認
        if not topic:
            return jsonify({
                "error": "Topic is required",
                "audio_data": [],
                "script": []
            }), 400
            
        # モックデータを使用するかどうか
        use_mock = data.get("use_mock", development_mode)
        
        # モックデータを使用する場合
        if use_mock:
            logger.info(f"Generating mock manzai script for topic: {topic}")
            script_data = get_mock_script(topic)
            return jsonify({
                "script": script_data,
                "audio_data": []
            })
        
        # 実際のスクリプト生成
        logger.info(f"Generating real manzai script for topic: {topic}")
        try:
            # Ollamaサービスを使用してスクリプトを生成
            script = ollama_service.generate_manzai_script(topic)
            
            logger.info(f"Successfully generated manzai script: {len(script)} lines")
            return jsonify({
                "script": script,
                "audio_data": []
            })
        
        except Exception as e:
            # エラー発生時はモックデータにフォールバック（開発モードのみ）
            logger.error(f"Error generating script: {e}")
            
            if development_mode:
                logger.warning("Falling back to mock data due to error")
                script_data = get_mock_script(topic)
                return jsonify({
                    "script": script_data,
                    "audio_data": [],
                    "error": f"サービスエラー（モックデータを使用）: {str(e)}"
                })
            else:
                # 本番環境ではエラーを返す
                return jsonify({
                    "error": f"Failed to generate script: {str(e)}",
                    "audio_data": [],
                    "script": []
                }), 500
                
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "audio_data": [],
            "script": []
        }), 500

@app.route('/api/audio/<filename>')
def get_audio(filename):
    """
    音声ファイルを提供するエンドポイント
    
    Args:
        filename: 音声ファイル名
        
    Returns:
        音声ファイル
    """
    try:
        audio_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'audio')
        return send_from_directory(audio_dir, filename)
    except Exception as e:
        logger.error(f"Error serving audio file {filename}: {e}")
        return jsonify({"error": str(e)}), 404

if __name__ == "__main__":
    # デバッグモードで実行
    app.run(host="0.0.0.0", port=5000, debug=True) 