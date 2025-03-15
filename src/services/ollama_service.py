"""Ollama APIクライアントを実装するモジュール。"""

import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, List, Any, NoReturn, Union
import requests
from requests.exceptions import RequestException
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
    """Ollamaサービスのエラーを表す例外クラス"""
    pass


class OllamaClient:
    """Ollamaサービスと通信するためのクライアントクラス"""

    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        OllamaClientを初期化します。
        
        Args:
            base_url: OllamaサービスのベースURL
        """
        self.base_url = base_url.rstrip('/')
        logger.info(f"OllamaClient initialized with base URL: {self.base_url}")

    def _prepare_request_data(self, model: str, prompt: str, format: Optional[str] = None) -> Dict[str, Any]:
        """
        APIリクエスト用のデータを準備します。
        
        Args:
            model: 使用するモデル名
            prompt: 入力プロンプト
            format: 出力フォーマット（例: "json"）
            
        Returns:
            リクエストボディとして使用するデータ辞書
        """
        # チャットエンドポイント用のデータ構造に変更
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False  # ストリーミングを明示的に無効化
        }
        
        # JSONフォーマットが指定されている場合、それを含める
        if format == "json":
            data["format"] = "json"
            
        logger.debug(f"Prepared request data: {data}")
        return data

    def generate_text_sync(self, model: str, prompt: str) -> str:
        """
        同期的にテキストを生成します。
        
        Args:
            model: 使用するモデル名
            prompt: 入力プロンプト
            
        Returns:
            生成されたテキスト
        """
        data = self._prepare_request_data(model, prompt)
        logger.info(f"Generating text with model: {model}, prompt length: {len(prompt)}")
        
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=data)
            response.raise_for_status()
            
            response_data = response.json()
            if "message" in response_data and "content" in response_data["message"]:
                generated_text = response_data["message"]["content"]
                logger.info(f"Successfully generated text, length: {len(generated_text)}")
                return generated_text
            else:
                logger.error(f"Unexpected response format: {response_data}")
                return ""
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during text generation: {e}")
            raise Exception(f"Connection error: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during text generation: {e}")
            raise Exception(f"Connection error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during text generation: {e}")
            raise Exception(f"Connection timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception during text generation: {e}")
            raise Exception(f"Request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during text generation: {e}")
            raise Exception(f"Unexpected error: {e}")

    def generate_json_sync(self, model: str, prompt: str, json_schema: Optional[str] = None) -> Dict[str, Any]:
        """
        同期的にJSON形式のレスポンスを生成します。
        
        Args:
            model: 使用するモデル名
            prompt: 入力プロンプト
            json_schema: JSONスキーマ（オプション）
            
        Returns:
            生成されたJSONオブジェクト
        """
        # JSONフォーマットを指定
        data = self._prepare_request_data(model, prompt, format="json")
        logger.info(f"Generating JSON with model: {model}, prompt length: {len(prompt)}")
        
        try:
            response = requests.post(f"{self.base_url}/api/chat", json=data)
            response.raise_for_status()
            
            response_data = response.json()
            if "message" in response_data and "content" in response_data["message"]:
                content = response_data["message"]["content"]
                try:
                    # JSONテキストとして解析
                    json_response = json.loads(content)
                    logger.info(f"Successfully generated JSON response")
                    return json_response
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}, content: {content[:100]}...")
                    raise Exception(f"Invalid JSON response: {e}")
            else:
                logger.error(f"Unexpected response format: {response_data}")
                raise Exception("Invalid response format from Ollama service")
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error during JSON generation: {e}")
            raise Exception(f"Connection error: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error during JSON generation: {e}")
            raise Exception(f"Connection error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during JSON generation: {e}")
            raise Exception(f"Connection timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception during JSON generation: {e}")
            raise Exception(f"Request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during JSON generation: {e}")
            raise Exception(f"Unexpected error: {e}")

    # 従来のOllamaServiceとの互換性を維持するためのメソッド
    def generate_manzai_script(self, topic: str) -> Dict[str, List[Dict[str, str]]]:
        """指定されたトピックに基づいて漫才スクリプトを生成
        
        Args:
            topic (str): 漫才のトピック
            
        Returns:
            Dict[str, List[Dict[str, str]]]: 生成された漫才スクリプト
            
        Raises:
            ValueError: トピックが空の場合
            OllamaServiceError: サービスとの通信に失敗した場合
        """
        if not topic:
            raise ValueError("topic cannot be empty")
        
        try:
            # プロンプトテンプレートをロード
            prompt = load_prompt("manzai_prompt", topic=topic)
            
            # JSON形式で出力するためのスキーマ
            additional_options = {
                "format": "json",
                "temperature": 0.8,
                "system": "あなたは漫才のスクリプトを生成するアシスタントです。与えられたトピックに基づいて、ツッコミとボケの会話形式の漫才を作成してください。"
            }
            
            logger.info(f"Generating manzai script for topic: {topic}")
            
            # まずJSONとして取得を試みる
            try:
                result = {}
                # 直接テキスト生成APIを使用
                generated_text = self.generate_text_sync(topic, prompt)
                
                # JSONを抽出
                try:
                    # コードブロックから抽出を試みる
                    import re
                    json_pattern = r"```json\s*([\s\S]*?)\s*```"
                    match = re.search(json_pattern, generated_text)
                    if match:
                        json_str = match.group(1)
                        result = json.loads(json_str)
                    else:
                        # 単純なJSONとして解析を試みる
                        result = json.loads(generated_text)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON, falling back to text parsing", extra={"text": generated_text})
                
                if "script" in result and isinstance(result["script"], list):
                    return result
                    
                # JSON解析に失敗した場合のフォールバック
                script = self._parse_manzai_script(generated_text)
                return {"script": script}
                
            except OllamaServiceError as e:
                logger.warning(f"Failed to generate JSON response, falling back to text: {str(e)}")
                
                # テキストとして取得して解析
                generated_text = self.generate_text_sync(topic, prompt)
                script = self._parse_manzai_script(generated_text)
                
                return {"script": script}
                
        except OllamaServiceError as e:
            logger.error(f"Failed to generate manzai script: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise OllamaServiceError(f"Unexpected error: {str(e)}")

    def _parse_manzai_script(self, raw_script: str) -> List[Dict[str, str]]:
        """生成された漫才スクリプトを解析して構造化されたフォーマットに変換
        
        Args:
            raw_script (str): 生のスクリプトテキスト
            
        Returns:
            List[Dict[str, str]]: 解析されたスクリプト
        """
        import re
        
        # コードブロックがある場合、内部のテキストのみを抽出
        code_block_pattern = r"```(.*?)```"
        code_block_match = re.search(code_block_pattern, raw_script, re.DOTALL)
        
        if code_block_match:
            script_content = code_block_match.group(1).strip()
        else:
            script_content = raw_script.strip()
        
        # 各行をパース
        result = []
        for line in script_content.splitlines():
            line = line.strip()
            if not line:
                continue
            
            # A: またはB: のパターンを検出
            match = re.match(r"([AB]):\s+(.*)", line)
            if match:
                speaker, text = match.groups()
                role = "tsukkomi" if speaker == "A" else "boke"
                result.append({
                    "role": role,
                    "text": text
                })
        
        return result


# OllamaServiceは互換性のためにOllamaClientを使用する
class OllamaService:
    """Ollamaサービスを使用してマンザイスクリプトを生成するサービスクラス"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "yuma/DeepSeek-R1-Distill-Qwen-Japanese:14b"):
        """
        OllamaServiceを初期化します。
        
        Args:
            base_url: OllamaサービスのベースURL
            model: 使用するモデル名
        """
        self.base_url = base_url
        self.model = model
        self.client = OllamaClient(base_url=base_url)
        logger.info(f"OllamaService initialized with model: {model}")
        
    def generate_manzai_script(self, topic: str) -> List[Dict[str, Any]]:
        """
        指定されたトピックに基づいてマンザイスクリプトを生成します。
        
        Args:
            topic: スクリプトのトピック
            
        Returns:
            生成されたマンザイスクリプト（役割と台詞のリスト）
        """
        try:
            logger.info(f"Generating manzai script for topic: {topic}")
            
            # プロンプトを構築
            prompt = self._create_prompt(topic)
            
            # JSONプロンプトを試みる
            try:
                # JSON形式で直接出力を試みる
                prompt_json = self._create_json_prompt(topic)
                result = self.client.generate_json_sync(self.model, prompt_json)
                
                if isinstance(result, dict) and "script" in result:
                    script = result.get("script", [])
                    if script and isinstance(script, list):
                        logger.info(f"Successfully generated manzai script with JSON output: {len(script)} lines")
                        return script
            except Exception as e:
                logger.warning(f"JSON generation failed, falling back to text: {e}")
                
                # テキスト生成にフォールバック
                result = {}
                # 直接テキスト生成APIを使用
                generated_text = self.client.generate_text_sync(self.model, prompt)
                
                # JSONを抽出
                script = self._parse_manzai_script(generated_text)
                if script:
                    logger.info(f"Successfully parsed manzai script from text: {len(script)} lines")
                    return script
            
            # どちらの方法も失敗した場合、シンプルなテキスト生成を使用
            logger.warning("Both JSON and structured text parsing failed, using simple text extraction")
            
            # テキストとして取得して解析
            generated_text = self.client.generate_text_sync(self.model, prompt)
            script = self._parse_manzai_script(generated_text)
            
            logger.info(f"Final fallback generated manzai script: {len(script)} lines")
            return script
            
        except Exception as e:
            logger.error(f"Error generating manzai script: {e}")
            # 空のスクリプトを返す代わりにエラーを発生させる
            raise Exception(f"Failed to generate manzai script: {e}")
    
    def _create_prompt(self, topic: str) -> str:
        """
        マンザイスクリプト生成用のプロンプトを作成します。
        
        Args:
            topic: スクリプトのトピック
            
        Returns:
            生成用プロンプト
        """
        return f"""
あなたは日本の漫才コンテンツを作成する専門家です。トピック「{topic}」に関する面白い漫才の台本を作成してください。
以下の条件に従ってください：

1. ボケとツッコミの2人で構成される漫才
2. ボケ役は「boke」、ツッコミ役は「tsukkomi」と表記
3. トピックに関連した面白いやり取りを含める
4. 最低10往復（計20行以上）のやり取り
5. 各行は200文字以内に収める
6. 出力形式は以下のようにしてください：

```
tsukkomi: （台詞）
boke: （台詞）
tsukkomi: （台詞）
...
```

トピック「{topic}」に関する漫才台本を作成してください。
"""

    def _create_json_prompt(self, topic: str) -> str:
        """
        JSON形式のマンザイスクリプト生成用プロンプトを作成します。
        
        Args:
            topic: スクリプトのトピック
            
        Returns:
            JSON生成用プロンプト
        """
        return f"""
あなたは日本の漫才コンテンツを作成する専門家です。トピック「{topic}」に関する面白い漫才の台本をJSON形式で作成してください。
以下の条件に従ってください：

1. ボケとツッコミの2人で構成される漫才
2. ボケ役は「boke」、ツッコミ役は「tsukkomi」と表記
3. トピックに関連した面白いやり取りを含める
4. 最低10往復（計20行以上）のやり取り
5. 各行は200文字以内に収める

出力は以下のようなJSON形式にしてください。追加のテキストや説明は含めず、有効なJSONのみを返してください：

{{
  "script": [
    {{
      "role": "tsukkomi",
      "text": "（台詞）"
    }},
    {{
      "role": "boke",
      "text": "（台詞）"
    }},
    ...
  ]
}}

トピック「{topic}」に関する漫才台本を作成してください。
"""

    def _parse_manzai_script(self, text: str) -> List[Dict[str, str]]:
        """
        生成されたテキストからマンザイスクリプトを解析します。
        
        Args:
            text: 生成されたテキスト
            
        Returns:
            解析されたマンザイスクリプト
        """
        script = []
        lines = text.strip().split('\n')
        
        # JSON文字列がある場合は抽出を試みる
        json_start = text.find('{')
        json_end = text.rfind('}')
        if json_start >= 0 and json_end > json_start:
            try:
                potential_json = text[json_start:json_end+1]
                parsed = json.loads(potential_json)
                if isinstance(parsed, dict) and "script" in parsed:
                    return parsed["script"]
            except:
                logger.warning("JSON extraction failed, falling back to line parsing")
        
        # 行ごとに解析
        for line in lines:
            line = line.strip()
            if not line or line.startswith('```') or line.startswith('#'):
                continue
                
            # 「tsukkomi: text」または「boke: text」形式の行を探す
            if ':' in line:
                parts = line.split(':', 1)
                role = parts[0].lower().strip()
                if role in ['tsukkomi', 'boke']:
                    script.append({
                        "role": role,
                        "text": parts[1].strip()
                    })
        
        return script

    def list_models(self) -> List[Dict[str, Any]]:
        """
        Ollamaサービスで利用可能なモデルのリストを取得します。
        
        Returns:
            利用可能なモデルのリスト
        
        Raises:
            Exception: APIリクエストに失敗した場合
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models_data = response.json()
            if "models" in models_data:
                models = models_data["models"]
                logger.info(f"Successfully retrieved {len(models)} models from Ollama service")
                return models
            else:
                logger.warning("No models found in Ollama service response")
                return []
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error listing models: {e}")
            raise Exception(f"Connection error: {e}")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error listing models: {e}")
            raise Exception(f"Connection error: {e}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout listing models: {e}")
            raise Exception(f"Connection timeout: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception listing models: {e}")
            raise Exception(f"Request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error listing models: {e}")
            raise Exception(f"Unexpected error: {e}") 