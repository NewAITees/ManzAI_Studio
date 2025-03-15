from flask import current_app, jsonify, Blueprint
from datetime import datetime
import logging

# Blueprintの作成
bp = Blueprint("api", __name__, url_prefix="/api")

# ロガーの設定
logger = logging.getLogger(__name__)

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