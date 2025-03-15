"""Prompt management routes."""
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any, List
import os
import json

from src.backend.app.utils.error_handlers import api_error_handler, APIError

bp = Blueprint("prompts", __name__, url_prefix="/api/prompts")

# プロンプトディレクトリパス
PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


@bp.route("", methods=["GET"])
@api_error_handler
def get_prompts() -> Dict[str, Any]:
    """Get available prompt templates.
    
    Returns:
        Dict containing prompts list.
    """
    try:
        prompts = []
        
        # プロンプトディレクトリの存在確認
        if not os.path.exists(PROMPT_DIR):
            return jsonify({
                "prompts": [],
                "message": "プロンプトディレクトリが存在しません。"
            })
        
        # プロンプト一覧を取得
        for filename in os.listdir(PROMPT_DIR):
            if filename.endswith(".txt"):
                prompt_id = filename[:-4]
                
                # メタデータファイルを探す
                metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
                metadata = {}
                
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                    except json.JSONDecodeError:
                        pass
                
                # プロンプトファイルを読み込む
                with open(os.path.join(PROMPT_DIR, filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                
                prompt_info = {
                    "id": prompt_id,
                    "name": metadata.get("name", prompt_id),
                    "description": metadata.get("description", ""),
                    "content": content,
                    "parameters": metadata.get("parameters", []),
                    "isDefault": metadata.get("isDefault", False)
                }
                
                prompts.append(prompt_info)
        
        return jsonify({
            "prompts": prompts
        })
    except Exception as e:
        raise APIError(f"プロンプト一覧の取得中にエラーが発生しました: {str(e)}", 500)


@bp.route("/<prompt_id>", methods=["GET"])
@api_error_handler
def get_prompt(prompt_id: str) -> Dict[str, Any]:
    """Get a specific prompt template.
    
    Args:
        prompt_id: ID of the prompt template.
        
    Returns:
        Dict containing prompt information.
    """
    try:
        # プロンプトファイルパス
        prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
        
        if not os.path.exists(prompt_path):
            raise APIError(f"プロンプト {prompt_id} が見つかりません", 404)
        
        # メタデータファイルを探す
        metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
        metadata = {}
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            except json.JSONDecodeError:
                pass
        
        # プロンプトファイルを読み込む
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        prompt_info = {
            "id": prompt_id,
            "name": metadata.get("name", prompt_id),
            "description": metadata.get("description", ""),
            "content": content,
            "parameters": metadata.get("parameters", []),
            "isDefault": metadata.get("isDefault", False)
        }
        
        return jsonify(prompt_info)
    except APIError:
        raise
    except Exception as e:
        raise APIError(f"プロンプトの取得中にエラーが発生しました: {str(e)}", 500)


@bp.route("", methods=["POST"])
@api_error_handler
def create_prompt() -> Dict[str, Any]:
    """Create a new prompt template.
    
    Returns:
        Dict containing creation result.
    """
    data = request.get_json()
    if not data or "id" not in data or "content" not in data:
        raise APIError("プロンプトIDと内容が必要です", 400)
        
    prompt_id = data["id"]
    content = data["content"]
    
    # プロンプトファイルパス
    prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
    
    # 既存のプロンプトを上書きしないよう確認
    if os.path.exists(prompt_path) and not data.get("overwrite", False):
        raise APIError(f"プロンプト {prompt_id} は既に存在します", 409)
    
    # プロンプト内容を保存
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # メタデータを保存
    metadata = {
        "name": data.get("name", prompt_id),
        "description": data.get("description", ""),
        "parameters": data.get("parameters", []),
        "isDefault": data.get("isDefault", False)
    }
    
    with open(os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json"), 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        "success": True,
        "message": f"プロンプト {prompt_id} が作成されました",
        "prompt": {
            "id": prompt_id,
            "name": metadata["name"],
            "description": metadata["description"],
            "content": content,
            "parameters": metadata["parameters"],
            "isDefault": metadata["isDefault"]
        }
    })


@bp.route("/<prompt_id>", methods=["PUT"])
@api_error_handler
def update_prompt(prompt_id: str) -> Dict[str, Any]:
    """Update a prompt template.
    
    Args:
        prompt_id: ID of the prompt template to update.
        
    Returns:
        Dict containing update result.
    """
    data = request.get_json()
    if not data or "content" not in data:
        raise APIError("プロンプト内容が必要です", 400)
        
    content = data["content"]
    
    # プロンプトファイルパス
    prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
    
    # プロンプトの存在確認
    if not os.path.exists(prompt_path):
        raise APIError(f"プロンプト {prompt_id} が見つかりません", 404)
    
    # プロンプト内容を保存
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # メタデータを更新
    metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
    
    # 既存のメタデータを読み込む
    existing_metadata = {}
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                existing_metadata = json.load(f)
        except json.JSONDecodeError:
            pass
    
    # メタデータを更新
    metadata = {
        "name": data.get("name", existing_metadata.get("name", prompt_id)),
        "description": data.get("description", existing_metadata.get("description", "")),
        "parameters": data.get("parameters", existing_metadata.get("parameters", [])),
        "isDefault": data.get("isDefault", existing_metadata.get("isDefault", False))
    }
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    return jsonify({
        "success": True,
        "message": f"プロンプト {prompt_id} が更新されました",
        "prompt": {
            "id": prompt_id,
            "name": metadata["name"],
            "description": metadata["description"],
            "content": content,
            "parameters": metadata["parameters"],
            "isDefault": metadata["isDefault"]
        }
    })


@bp.route("/<prompt_id>", methods=["DELETE"])
@api_error_handler
def delete_prompt(prompt_id: str) -> Dict[str, Any]:
    """Delete a prompt template.
    
    Args:
        prompt_id: ID of the prompt template to delete.
        
    Returns:
        Dict containing deletion result.
    """
    # デフォルトプロンプトは削除できない
    if prompt_id == "manzai_prompt":
        raise APIError("デフォルトプロンプトは削除できません", 403)
    
    # プロンプトファイルパス
    prompt_path = os.path.join(PROMPT_DIR, f"{prompt_id}.txt")
    metadata_path = os.path.join(PROMPT_DIR, f"{prompt_id}.meta.json")
    
    # プロンプトの存在確認
    if not os.path.exists(prompt_path):
        raise APIError(f"プロンプト {prompt_id} が見つかりません", 404)
    
    # ファイルの削除
    try:
        os.remove(prompt_path)
        if os.path.exists(metadata_path):
            os.remove(metadata_path)
    except Exception as e:
        raise APIError(f"プロンプトの削除中にエラーが発生しました: {str(e)}", 500)
    
    return jsonify({
        "success": True,
        "message": f"プロンプト {prompt_id} が削除されました"
    }) 