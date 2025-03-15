from flask import current_app, jsonify
from flask_restful import Resource
from datetime import datetime

@bp.route("/detailed-status", methods=["GET"])
def detailed_status() -> Response:
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
        
        system_info = {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": dict(psutil.disk_usage("/").__dict__)
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