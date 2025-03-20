from flask import current_app, jsonify, Blueprint, request
from datetime import datetime
import logging
from src.backend.app.services.voicevox_service import VoiceVoxService
from src.backend.app.utils.prompt_loader import PromptLoader
from werkzeug.exceptions import BadRequest, NotFound
import json

# Blueprintの作成
bp = Blueprint("api", __name__, url_prefix="/api")

# ロガーの設定
logger = logging.getLogger(__name__)

prompt_loader = PromptLoader()

@bp.route("/health", methods=["GET"])
def health_check():
    """
    ヘルスチェックエンドポイント
    
    Returns:
        dict: ヘルスステータス情報
    """
    return jsonify({"status": "healthy"})

@bp.route("/detailed-status", methods=["GET"])
def detailed_status():
    """
    詳細なサービスステータス情報を返すエンドポイント
    
    Returns:
        Response: 詳細なシステムステータス情報
    """
    try:
        # Ollamaの詳細情報を取得
        ollama_service = current_app.ollama_service
        ollama_detail = ollama_service.get_detailed_status()
        
        # VoiceVoxのステータスも取得
        voicevox_available = False
        voicevox_speakers = []
        voicevox_error = None
        
        voicevox_service = current_app.voicevox_service
        try:
            voicevox_speakers = voicevox_service.list_speakers()
            voicevox_available = True
        except Exception as e:
            voicevox_error = str(e)
        
        # システム情報の取得
        import platform
        import psutil
        
        # diskusageの処理を修正
        disk = psutil.disk_usage("/")
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
        }
        
        # レスポンス構築
        response_data = {
            "timestamp": datetime.now().isoformat(),
            "ollama": ollama_detail,
            "voicevox": {
                "available": voicevox_available, 
                "speakers_count": len(voicevox_speakers),
                "error": voicevox_error
            },
            "system": system_info
        }
        
        return jsonify(response_data)
    except Exception as e:
        logger.exception(f"Error getting detailed status: {e}")
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500 

@bp.route('/prompts', methods=['GET'])
def get_prompts():
    """プロンプト一覧を取得"""
    try:
        prompts = prompt_loader.get_all_prompts()
        return jsonify(prompts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/prompts/<prompt_id>', methods=['GET'])
def get_prompt_by_id(prompt_id):
    """特定のプロンプトを取得"""
    try:
        prompt = prompt_loader.get_prompt_by_id(prompt_id)
        if not prompt:
            return jsonify({"error": "Prompt not found"}), 404
        return jsonify(prompt), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/prompts', methods=['POST'])
def create_prompt():
    """新しいプロンプトを作成"""
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ['name', 'description', 'template']):
            return jsonify({"error": "Invalid request data"}), 400
        
        new_prompt = prompt_loader.create_prompt(data)
        return jsonify(new_prompt), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/models/register', methods=['POST'])
def register_model():
    """新しいモデルを登録"""
    try:
        if 'model_file' not in request.files or 'thumbnail' not in request.files:
            return jsonify({"error": "Missing required files"}), 400

        model_file = request.files['model_file']
        thumbnail = request.files['thumbnail']
        
        if not model_file.filename.endswith('.zip'):
            return jsonify({"error": "Invalid model file format"}), 400

        # TODO: Implement model registration logic
        return jsonify({"message": "Model registered successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/synthesize', methods=['POST'])
def synthesize():
    """台本を音声合成"""
    try:
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "Invalid request data"}), 400

        voicevox_service = current_app.voicevox_service
        audio_manager = current_app.audio_manager
        
        # 各台詞を音声合成
        audio_data = []
        for line in data['script']:
            audio_file = voicevox_service.synthesize(
                text=line['text'],
                speaker_id=line['speaker_id']
            )
            audio_data.append({
                'speaker': line['speaker'],
                'text': line['text'],
                'audio_file': audio_file
            })
        
        return jsonify({'audio_data': audio_data}), 200
    except Exception as e:
        logger.exception(f"Error in synthesize endpoint: {e}")
        return jsonify({"error": str(e)}), 500 