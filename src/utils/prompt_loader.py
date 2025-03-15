import os
from typing import Dict, Any

def load_prompt(template_name: str, **kwargs: Any) -> str:
    """プロンプトテンプレートをロードして変数を埋め込む
    
    Args:
        template_name (str): テンプレート名（拡張子なし）
        **kwargs: テンプレート内の変数を置き換えるキーワード引数
        
    Returns:
        str: 変数が埋め込まれたプロンプト
        
    Raises:
        FileNotFoundError: テンプレートファイルが見つからない場合
    """
    # テンプレートのパスを構築
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    template_path = os.path.join(template_dir, f"{template_name}.txt")
    
    # テンプレートを読み込む
    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()
    
    # 変数を埋め込む
    return template.format(**kwargs) 