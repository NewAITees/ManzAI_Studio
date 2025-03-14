"""API routes for the backend application."""
from flask import Blueprint, jsonify, request, current_app, send_file
from typing import Dict, Any, Union, Tuple
import os

from src.services.ollama_service import OllamaService
from src.services.voicevox_service import VoiceVoxService
from src.services.audio_manager import AudioManager

bp = Blueprint("api", __name__, url_prefix="/api")

# サービスの初期化
ollama_service = OllamaService()
voicevox_service = VoiceVoxService()
audio_manager = AudioManager()


@bp.route("/health", methods=["GET"])
def health_check() -> Dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict with status message.
    """
    return jsonify({"status": "healthy"})


@bp.route("/generate", methods=["POST"])
def generate_manzai() -> Union[Dict[str, Any], Tuple[Dict[str, Any], int]]:
    """Generate manzai script using Ollama and VoiceVox.

    Returns:
        Dict containing the generated script and audio data paths.
    """
    # リクエストのバリデーション
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415
        
    data = request.get_json()
    if not data or "topic" not in data:
        return jsonify({"error": "No topic provided"}), 400
        
    topic = data.get("topic")
    if not topic or topic.strip() == "":
        return jsonify({"error": "Topic cannot be empty"}), 400
    
    try:
        # 漫才スクリプトを生成
        script_data = ollama_service.generate_manzai_script(topic)
        
        # 音声を生成
        audio_data = []
        for line in script_data["script"]:
            # 音声を生成
            voice_data = voicevox_service.generate_voice(
                line["text"],
                speaker_id=1 if line["role"] == "tsukkomi" else 2
            )
            
            # 音声ファイルを保存
            filename = f"{line['role']}_{len(audio_data)}"
            audio_path = audio_manager.save_audio(voice_data, filename)
            
            audio_data.append({
                "role": line["role"],
                "audio_path": os.path.basename(audio_path)
            })
        
        return jsonify({
            "script": script_data["script"],
            "audio_data": audio_data
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route("/audio/<filename>")
def get_audio(filename: str) -> Union[Any, Tuple[Dict[str, str], int]]:
    """Get audio file.

    Args:
        filename: Name of the audio file to retrieve.

    Returns:
        Audio file or error message.
    """
    try:
        audio_data = audio_manager.get_audio(filename)
        return send_file(
            os.path.join(audio_manager.audio_dir, filename),
            mimetype="audio/wav"
        )
    except FileNotFoundError:
        return jsonify({"error": "Audio file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500 