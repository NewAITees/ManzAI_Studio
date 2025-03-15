"""
プロンプトテンプレートをロードするユーティリティモジュール
"""
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PromptTemplateNotFoundError(Exception):
    """プロンプトテンプレートが見つからない場合のエラー"""
    pass

def load_prompt(template_name: str, **kwargs: Any) -> str:
    """プロンプトテンプレートをロードして変数を埋め込む
    
    Args:
        template_name: テンプレート名（拡張子なし）
        **kwargs: テンプレート内の変数を置き換えるキーワード引数
        
    Returns:
        変数が埋め込まれたプロンプト
        
    Raises:
        PromptTemplateNotFoundError: テンプレートファイルが見つからない場合
    """
    # テンプレートのパスを構築
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    template_path = os.path.join(template_dir, f"{template_name}.txt")
    
    try:
        # テンプレートを読み込む
        with open(template_path, "r", encoding="utf-8") as file:
            template = file.read()
        
        # 変数を埋め込む
        return template.format(**kwargs)
    except FileNotFoundError:
        error_message = f"プロンプトテンプレートが見つかりません: {template_name}"
        logger.error(error_message)
        raise PromptTemplateNotFoundError(error_message)
    except KeyError as e:
        error_message = f"テンプレート変数が不足しています: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    except ValueError as e:
        error_message = f"テンプレート変数の形式が不正です: {e}"
        logger.error(error_message)
        raise ValueError(error_message)
    except Exception as e:
        error_message = f"テンプレート処理中に予期せぬエラーが発生しました: {e}"
        logger.exception(error_message)
        raise 