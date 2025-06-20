import logging
from datetime import datetime

from flask import Blueprint, current_app, jsonify, request

from src.backend.app.utils.error_handlers import APIError, api_error_handler
from src.backend.app.utils.prompt_loader import PromptLoader

# Blueprintの作成
api_bp = Blueprint("api", __name__, url_prefix="/api")

# ロガーの設定
logger = logging.getLogger(__name__)

prompt_loader = PromptLoader()


@api_bp.route("/health", methods=["GET"])
@api_error_handler
def health_check():
    """
    ヘルスチェックエンドポイント

    Returns:
        dict: ヘルスステータス情報
    """
    return jsonify({"status": "healthy"})


@api_bp.route("/detailed-status", methods=["GET"])
@api_error_handler
def detailed_status():
    """
    詳細なサービスステータス情報を返すエンドポイント

    Returns:
        Response: 詳細なシステムステータス情報
    """
    # Ollamaの詳細情報を取得
    ollama_service = current_app.ollama_service
    ollama_detail = ollama_service.get_detailed_status()

    # VoiceVoxのステータスも取得
    voicevox_service = current_app.voicevox_service
    voicevox_detail = voicevox_service.get_detailed_status()

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
            "percent": disk.percent,
        },
    }

    # レスポンス構築
    response_data = {
        "timestamp": datetime.now().isoformat(),
        "ollama": ollama_detail,
        "voicevox": voicevox_detail,
        "system": system_info,
    }

    return jsonify(response_data)


@api_bp.route("/prompts", methods=["GET"])
def get_prompts():
    """プロンプト一覧を取得"""
    try:
        prompts = prompt_loader.get_all_prompts()
        return jsonify(prompts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/prompts/<prompt_id>", methods=["GET"])
def get_prompt_by_id(prompt_id):
    """特定のプロンプトを取得"""
    try:
        prompt = prompt_loader.get_prompt_by_id(prompt_id)
        if not prompt:
            return jsonify({"error": "Prompt not found"}), 404
        return jsonify(prompt), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/prompts", methods=["POST"])
def create_prompt():
    """新しいプロンプトを作成"""
    try:
        data = request.get_json()
        if not data or not all(key in data for key in ["name", "description", "template"]):
            return jsonify({"error": "Invalid request data"}), 400

        new_prompt = prompt_loader.create_prompt(data)
        return jsonify(new_prompt), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/models/register", methods=["POST"])
def register_model():
    """新しいモデルを登録"""
    try:
        if "model_file" not in request.files or "thumbnail" not in request.files:
            return jsonify({"error": "Missing required files"}), 400

        model_file = request.files["model_file"]
        thumbnail = request.files["thumbnail"]

        if not model_file.filename.endswith(".zip"):
            return jsonify({"error": "Invalid model file format"}), 400

        # TODO: Implement model registration logic
        return jsonify({"message": "Model registered successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/generate", methods=["POST"])
@api_error_handler
def generate():
    """漫才スクリプトを生成"""
    data = request.get_json()
    if not data or "topic" not in data:
        raise APIError("Topic is required", 400)

    topic = data.get("topic", "").strip()
    if not topic:
        raise APIError("topic cannot be empty", 400)

    model = data.get("model", current_app.config.get("OLLAMA_MODEL", "gemma3:4b"))
    use_mock = data.get("use_mock", False)

    # モックデータを使用する場合
    if use_mock:
        mock_script = [
            {"role": "tsukkomi", "text": f"今日は{topic}について話しましょう。"},
            {"role": "boke", "text": f"{topic}って面白いですね！"},
            {"role": "tsukkomi", "text": "そうですね、詳しく教えてください。"},
            {"role": "boke", "text": "実は私もよく知らないんです..."},
        ]
        mock_audio = [
            {"role": "tsukkomi", "text": line["text"], "audio_file": f"/api/audio/mock_{i}.wav"}
            for i, line in enumerate(mock_script)
        ]
        return jsonify({"script": mock_script, "audio_data": mock_audio})

    # 実際のスクリプト生成
    ollama_service = current_app.ollama_service
    voicevox_service = current_app.voicevox_service
    audio_manager = current_app.audio_manager

    try:
        # スクリプト生成
        script_lines = ollama_service.generate_manzai_script(topic, model)

        # 音声合成とスクリプト構築
        script_dict = []
        for i, line in enumerate(script_lines):
            speaker_id = 1 if line.role.value == "tsukkomi" else 2
            audio_bytes = voicevox_service.synthesize_voice(line.text, speaker_id)

            # 音声ファイル保存
            audio_filename = audio_manager.save_audio(audio_bytes, f"script_{i}")

            script_dict.append(
                {"role": line.role.value.upper(), "text": line.text, "audio_file": audio_filename}
            )

        return jsonify({"script": script_dict})

    except Exception as e:
        logger.error(f"Error generating script: {e}")
        raise APIError(f"Failed to generate script: {e!s}", 500)


@api_bp.route("/speakers", methods=["GET"])
@api_error_handler
def get_speakers():
    """VoiceVox話者一覧を取得"""
    voicevox_service = current_app.voicevox_service

    try:
        speakers = voicevox_service.list_speakers()
        return jsonify(speakers)
    except Exception as e:
        logger.error(f"Error fetching speakers: {e}")
        raise APIError(f"Failed to fetch speakers: {e!s}", 500)


@api_bp.route("/audio/<filename>", methods=["GET"])
@api_error_handler
def get_audio(filename):
    """音声ファイルを取得"""
    audio_manager = current_app.audio_manager

    try:
        # テストではget_audioメソッドをモックしているのでそれを使用
        audio_data = audio_manager.get_audio(filename)

        from flask import Response

        return Response(
            audio_data,
            mimetype="audio/wav",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except FileNotFoundError:
        raise APIError("Audio file not found", 404)
    except Exception as e:
        logger.error(f"Error serving audio file: {e}")
        raise APIError(f"Failed to serve audio file: {e!s}", 500)


@api_bp.route("/audio/list", methods=["GET"])
@api_error_handler
def list_audio_files():
    """音声ファイル一覧を取得"""
    audio_manager = current_app.audio_manager

    try:
        files = audio_manager.list_audio_files()
        return jsonify(files)
    except Exception as e:
        logger.error(f"Error listing audio files: {e}")
        raise APIError(f"Failed to list audio files: {e!s}", 500)


@api_bp.route("/audio/cleanup", methods=["POST"])
@api_error_handler
def cleanup_audio_files():
    """古い音声ファイルをクリーンアップ"""
    audio_manager = current_app.audio_manager

    try:
        # JSONデータが送信されない場合もある
        try:
            data = request.get_json() or {}
        except Exception:
            data = {}
        max_files = data.get("max_files", 10)

        deleted_count = audio_manager.cleanup_old_files(max_files)
        return jsonify(
            {"message": "Audio files cleaned up successfully", "deleted_files": deleted_count}
        )
    except Exception as e:
        logger.error(f"Error cleaning up audio files: {e}")
        raise APIError(f"Failed to cleanup audio files: {e!s}", 500)


@api_bp.route("/timing", methods=["POST"])
@api_error_handler
def get_timing_data():
    """リップシンク用タイミングデータを取得"""
    data = request.get_json()
    if not data or "text" not in data:
        raise APIError("Text is required", 400)

    text = data.get("text", "").strip()
    speaker_id = data.get("speaker_id", 1)

    if not text:
        raise APIError("Text cannot be empty", 400)

    voicevox_service = current_app.voicevox_service

    try:
        timing_data = voicevox_service.get_timing_data(text, speaker_id)
        return jsonify(timing_data)
    except Exception as e:
        logger.error(f"Error getting timing data: {e}")
        # フォールバック用のモックデータを返す
        mock_timing = {
            "accent_phrases": [
                {
                    "moras": [
                        {"text": char, "start_time": i * 150, "end_time": (i + 1) * 150}
                        for i, char in enumerate(text[:10])  # 最初の10文字分
                    ]
                }
            ]
        }
        return jsonify(mock_timing)


@api_bp.route("/synthesize", methods=["POST"])
@api_error_handler
def synthesize():
    """台本を音声合成"""
    data = request.get_json()
    if not data or "script" not in data:
        raise APIError("Invalid request data", 400)

    voicevox_service = current_app.voicevox_service
    audio_manager = current_app.audio_manager

    # 各台詞を音声合成
    audio_data = []
    for line in data["script"]:
        audio_file = voicevox_service.synthesize(text=line["text"], speaker_id=line["speaker_id"])
        audio_data.append(
            {"speaker": line["speaker"], "text": line["text"], "audio_file": audio_file}
        )

    return jsonify({"audio_data": audio_data})
