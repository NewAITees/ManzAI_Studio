"""API routes for the backend application."""
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/health", methods=["GET"])
def health_check() -> Dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict with status message.
    """
    return jsonify({"status": "healthy"})


@bp.route("/generate", methods=["POST"])
def generate_manzai() -> Dict[str, Any]:
    """Generate manzai script using Ollama.

    Returns:
        Dict containing the generated script.
    """
    data = request.get_json()
    if not data or "topic" not in data:
        return jsonify({"error": "No topic provided"}), 400

    # TODO: Implement manzai generation logic
    return jsonify({"message": "Not implemented yet"}), 501 