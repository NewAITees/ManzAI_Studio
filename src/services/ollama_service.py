"""
LLMとの通信を担当するサービス
"""
import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, List, Any, NoReturn, Union, cast, TypedDict

import requests
from requests.exceptions import RequestException, ConnectionError, Timeout

from src.models.script import ManzaiScript, ScriptLine, Role
from src.models.service import OllamaModel
from src.utils.prompt_loader import load_prompt

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ログディレクトリの作成
os.makedirs('logs', exist_ok=True)

# ファイルハンドラーの設定
fh = logging.FileHandler(
    f'logs/ollama_client_{datetime.now().strftime("%Y%m%d")}.log',
    encoding="utf-8"
)
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


class OllamaServiceError(Exception):
    """OllamaサービスのAPIエラーを表す例外クラス"""
    pass


class ScriptItem(TypedDict):
    """台本の項目を表す型"""
    role: str
    text: str


class OllamaClient:
    """Ollama APIとの通信を行うクライアント"""
    
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        """OllamaClientの初期化
        
        Args:
            base_url: Ollama APIのベースURL
        """
        self.base_url = base_url
        logger.info(f"OllamaClient initialized with base URL: {base_url}")
    
    def _prepare_request_data(self, prompt: str, model_name: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """APIリクエスト用のデータを準備
        
        Args:
            prompt: プロンプト
            model_name: モデル名
            options: 生成オプション
            
        Returns:
            リクエストデータの辞書
        """
        request_data: Dict[str, Any] = {
            "model": model_name,
            "prompt": prompt,
            "stream": False
        }
        
        if options:
            request_data["options"] = options
        
        return request_data
    
    def generate_text_sync(self, prompt: str, model_name: str = "llama3", options: Optional[Dict[str, Any]] = None) -> str:
        """テキスト生成を同期的に実行
        
        Args:
            prompt: プロンプト
            model_name: モデル名
            options: 生成オプション
            
        Returns:
            生成されたテキスト
            
        Raises:
            OllamaServiceError: API呼び出しに失敗した場合
        """
        request_data = self._prepare_request_data(prompt, model_name, options)
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=request_data,
                timeout=60
            )
            response.raise_for_status()
            response_data = response.json()
            
            if "error" in response_data:
                raise OllamaServiceError(f"Ollama API error: {response_data['error']}")
            
            generated_text: str = response_data.get("response", "")
            return generated_text
            
        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with Ollama API: {str(e)}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except json.JSONDecodeError:
            error_message = "Invalid JSON response from Ollama API"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except Exception as e:
            error_message = f"Unexpected error calling Ollama API: {str(e)}"
            logger.exception(error_message)
            raise OllamaServiceError(error_message)
    
    def generate_json_sync(self, prompt: str, model_name: str = "llama3", options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """JSONレスポンスを生成
        
        Args:
            prompt: プロンプト
            model_name: モデル名
            options: 生成オプション
            
        Returns:
            生成されたJSONオブジェクト
            
        Raises:
            OllamaServiceError: API呼び出しに失敗した場合、またはJSONのパースに失敗した場合
        """
        # JSONフォーマットを強制するオプションを追加
        if not options:
            options = {}
        
        options.update({
            "temperature": options.get("temperature", 0.7),
            "top_p": options.get("top_p", 0.9),
            "format": "json"
        })
        
        raw_text = self.generate_text_sync(prompt, model_name, options)
        
        try:
            # JSONブロックを抽出
            json_block = self._extract_json_block(raw_text)
            json_data: Dict[str, Any] = json.loads(json_block)
            return json_data
        except json.JSONDecodeError as e:
            error_message = f"Failed to parse JSON from response: {str(e)}"
            logger.error(f"{error_message}\nRaw text: {raw_text}")
            raise OllamaServiceError(error_message)
    
    def _extract_json_block(self, text: str) -> str:
        """テキストからJSONブロックを抽出
        
        Args:
            text: 抽出元テキスト
            
        Returns:
            JSONブロック
            
        Raises:
            OllamaServiceError: JSONブロックが見つからない場合
        """
        # JSONブロックを抽出（```json～```の形式を想定）
        if "```json" in text and "```" in text.split("```json", 1)[1]:
            return text.split("```json", 1)[1].split("```", 1)[0].strip()
        
        # 単純な中括弧のブロックを探す
        if "{" in text and "}" in text:
            start = text.find("{")
            # 最後の閉じ括弧を見つける（ネストされたJSONを考慮）
            end = text.rfind("}")
            if start < end:
                return text[start:end+1]
        
        # 特殊なケース: テキスト全体がJSONとして解析可能な場合はそのまま返す
        try:
            json.loads(text)
            return text
        except:
            pass
        
        raise OllamaServiceError(f"Could not extract JSON block from response")
    
    def list_models(self) -> List[Dict[str, Any]]:
        """利用可能なモデルのリストを取得
        
        Returns:
            モデル情報のリスト
            
        Raises:
            OllamaServiceError: API呼び出しに失敗した場合
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            response_data = response.json()
            
            if "error" in response_data:
                raise OllamaServiceError(f"Ollama API error: {response_data['error']}")
            
            models = response_data.get("models", [])
            return cast(List[Dict[str, Any]], models)
            
        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with Ollama API: {str(e)}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except json.JSONDecodeError:
            error_message = "Invalid JSON response from Ollama API"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except Exception as e:
            error_message = f"Unexpected error calling Ollama API: {str(e)}"
            logger.exception(error_message)
            raise OllamaServiceError(error_message)


class OllamaService:
    """OllamaサービスのインターフェースとなるクラスでLLMとの通信を行う"""
    
    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        """OllamaServiceの初期化
        
        Args:
            base_url: Ollama APIのベースURL
        """
        self.client = OllamaClient(base_url)
        self.prompts: Dict[str, str] = {}  # プロンプトキャッシュ
        logger.info("OllamaService initialized")
    
    def _parse_manzai_script(self, data: Dict[str, Any]) -> List[ScriptItem]:
        """生成されたJSONから台本データを抽出
        
        Args:
            data: 生成されたJSONデータ
            
        Returns:
            台本のリスト
            
        Raises:
            OllamaServiceError: データの形式が不正な場合
        """
        # スクリプトの取得
        script = data.get("script", [])
        
        # 形式の検証
        if not isinstance(script, list):
            raise OllamaServiceError("Generated script is not a list")
        
        if not script:
            raise OllamaServiceError("Generated script is empty")
        
        # 各行のvalidation
        validated_script: List[ScriptItem] = []
        
        for i, line in enumerate(script):
            if not isinstance(line, dict):
                raise OllamaServiceError(f"Script line {i} is not a dictionary")
            
            role = line.get("role", "")
            text = line.get("text", "")
            
            if not role or not text:
                raise OllamaServiceError(f"Script line {i} is missing role or text")
            
            # 役割の正規化
            if role.lower() in ["boke", "ボケ"]:
                normalized_role = "boke"
            elif role.lower() in ["tsukkomi", "つっこみ"]:
                normalized_role = "tsukkomi"
            else:
                normalized_role = role.lower()
            
            validated_script.append({"role": normalized_role, "text": text})
        
        return validated_script
    
    def generate_manzai_script(self, topic: str, model_name: str = "llama3") -> List[ScriptItem]:
        """指定されたトピックの漫才台本を生成
        
        Args:
            topic: 台本のトピック
            model_name: 使用するLLMモデル名
            
        Returns:
            生成された台本
            
        Raises:
            OllamaServiceError: 台本生成に失敗した場合
        """
        if not topic:
            raise ValueError("Topic cannot be empty")
        
        prompt = (
            f"日本の漫才の台本を作成してください。トピックは「{topic}」です。\n"
            "台本は「ボケ」と「ツッコミ」の2人の会話で構成してください。\n"
            "以下のJSON形式で出力してください：\n\n"
            "```json\n"
            "{\n"
            '  "script": [\n'
            '    {"role": "boke", "text": "ボケのセリフ"},\n'
            '    {"role": "tsukkomi", "text": "ツッコミのセリフ"},\n'
            "    ...\n"
            "  ]\n"
            "}\n"
            "```\n\n"
            "・ボケ役は面白いことや間違ったことを言います。\n"
            "・ツッコミ役はボケに対して突っ込みを入れたり、話を進行します。\n"
            "・最低10往復以上の会話を作成してください。\n"
            "・日本語で作成してください。\n"
            "・必ず指定されたJSON形式で出力してください。"
        )
        
        try:
            logger.info(f"Generating manzai script for topic: {topic} with model: {model_name}")
            json_response = self.client.generate_json_sync(prompt, model_name)
            
            script = self._parse_manzai_script(json_response)
            logger.info(f"Successfully generated manzai script with {len(script)} lines")
            
            return script
            
        except (OllamaServiceError, ValueError) as e:
            # 既存のエラーをそのまま再送出
            raise
        except Exception as e:
            error_message = f"Error generating manzai script: {str(e)}"
            logger.exception(error_message)
            raise OllamaServiceError(error_message)
    
    def list_models(self) -> List[Dict[str, Any]]:
        """利用可能なモデルのリストを取得
        
        Returns:
            モデル情報のリスト
            
        Raises:
            OllamaServiceError: モデルの取得に失敗した場合
        """
        return self.client.list_models() 