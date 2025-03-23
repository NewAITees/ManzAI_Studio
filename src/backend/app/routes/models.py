"""Model management routes."""
from flask import Blueprint, jsonify, current_app, request
from typing import Dict, Any, List
import os
import json
import glob

from src.backend.app.utils.error_handlers import api_error_handler, APIError
from src.backend.app.routes.api import api_bp

# モデルディレクトリパス（開発環境と本番環境で異なる可能性あり）
LIVE2D_BASE_DIR = os.path.join(os.getcwd(), "frontend", "public", "live2d", "models")

@api_bp.route("/models/live2d", methods=["GET"])
@api_error_handler
def get_live2d_models() -> Dict[str, Any]:
    """Get available Live2D models.
    
    Returns:
        Dict containing models list.
    """
    try:
        # モデルディレクトリの存在確認
        if not os.path.exists(LIVE2D_BASE_DIR):
            return jsonify({
                "models": [],
                "message": "モデルディレクトリが存在しません。"
            })
        
        # モデルを検索
        models = []
        for model_dir in glob.glob(os.path.join(LIVE2D_BASE_DIR, "*/")):
            model_name = os.path.basename(os.path.dirname(model_dir))
            
            # model.json ファイルの検索
            model_json_path = os.path.join(model_dir, "model.json")
            
            if os.path.exists(model_json_path):
                try:
                    with open(model_json_path, 'r', encoding='utf-8') as f:
                        model_data = json.load(f)
                        
                    # モデル情報を構築
                    model_info = {
                        "id": model_name,
                        "name": model_data.get("name", model_name),
                        "path": f"/live2d/models/{model_name}/model.json",
                        "type": model_data.get("type", "unknown"),
                        "thumbnail": f"/live2d/models/{model_name}/thumbnail.png" if os.path.exists(os.path.join(model_dir, "thumbnail.png")) else None
                    }
                    
                    models.append(model_info)
                except json.JSONDecodeError:
                    # JSON解析エラーは無視してスキップ
                    continue
        
        return jsonify({
            "models": models
        })
    except Exception as e:
        raise APIError(f"モデル一覧の取得中にエラーが発生しました: {str(e)}", 500)


@api_bp.route("/models/live2d/register", methods=["POST"])
@api_error_handler
def register_model() -> Dict[str, Any]:
    """Register a new Live2D model with metadata.
    
    Returns:
        Dict containing registration result.
    """
    data = request.get_json()
    if not data or "id" not in data or "path" not in data:
        raise APIError("モデルIDとパスが必要です", 400)
        
    model_id = data["id"]
    model_path = data["path"]
    
    # モデルディレクトリの作成
    model_dir = os.path.join(LIVE2D_BASE_DIR, model_id)
    os.makedirs(model_dir, exist_ok=True)
    
    # メタデータの作成
    metadata = {
        "name": data.get("name", model_id),
        "type": data.get("type", "character"),
        "model": os.path.basename(model_path),
        "textures": data.get("textures", []),
        "version": "1.0.0"
    }
    
    # メタデータをファイルに保存
    with open(os.path.join(model_dir, "model.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        "success": True,
        "message": f"モデル {model_id} が登録されました",
        "model": {
            "id": model_id,
            "name": metadata["name"],
            "path": f"/live2d/models/{model_id}/model.json",
            "type": metadata["type"]
        }
    }) 