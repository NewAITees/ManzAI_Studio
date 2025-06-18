"""
プロンプトテンプレートをロードするユーティリティモジュール
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class PromptTemplateNotFoundError(Exception):
    """プロンプトテンプレートが見つからない場合のエラー"""

    pass


class PromptLoader:
    """プロンプトローダークラス"""

    def __init__(
        self, prompts_dir: Optional[str] = None, templates_dir: Optional[str] = None
    ) -> None:
        """
        Args:
            prompts_dir: JSONプロンプトファイルのディレクトリパス
            templates_dir: テキストテンプレートファイルのディレクトリパス
        """
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.prompts_dir = prompts_dir or os.path.join(base_dir, "templates", "prompts")
        self.templates_dir = templates_dir or os.path.join(base_dir, "templates")
        os.makedirs(self.prompts_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)

    def get_all_prompts(self) -> List[Dict[str, Any]]:
        """全プロンプトを取得"""
        prompts = []
        for filename in os.listdir(self.prompts_dir):
            if filename.endswith(".json"):
                with open(os.path.join(self.prompts_dir, filename), "r", encoding="utf-8") as f:
                    prompt = json.load(f)
                    prompts.append(prompt)
        return prompts

    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """IDでプロンプトを取得"""
        try:
            with open(
                os.path.join(self.prompts_dir, f"{prompt_id}.json"),
                "r",
                encoding="utf-8",
            ) as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def create_prompt(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """新しいプロンプトを作成"""
        prompt_id = str(uuid4())
        prompt_data["id"] = prompt_id

        with open(os.path.join(self.prompts_dir, f"{prompt_id}.json"), "w", encoding="utf-8") as f:
            json.dump(prompt_data, f, ensure_ascii=False, indent=2)

        return prompt_data

    def load_template(self, template_name: str, **kwargs: Any) -> str:
        """プロンプトテンプレートをロードして変数を埋め込む

        Args:
            template_name: テンプレート名（拡張子なし）
            **kwargs: テンプレート内の変数を置き換えるキーワード引数

        Returns:
            変数が埋め込まれたプロンプト

        Raises:
            PromptTemplateNotFoundError: テンプレートファイルが見つからない場合
        """
        # まずJSONプロンプトを探す
        json_path = os.path.join(self.prompts_dir, f"{template_name}.json")
        txt_path = os.path.join(self.templates_dir, f"{template_name}.txt")

        try:
            # JSONプロンプトがある場合はそちらを優先
            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    prompt_data = json.load(f)
                    template = prompt_data.get("template", "")
            # なければテキストテンプレートを使用
            else:
                with open(txt_path, "r", encoding="utf-8") as f:
                    template = f.read()

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
            error_message = f"プロンプトのロード中にエラーが発生しました: {e}"
            logger.error(error_message)
            raise
