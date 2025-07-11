"""
LLMとの通信を担当するサービス
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Union, cast

import requests

from src.backend.app.models.script import Role, ScriptLine
from src.backend.app.utils.prompt_loader import PromptLoader

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ログディレクトリの作成
os.makedirs("logs", exist_ok=True)

# ファイルハンドラーの設定
fh = logging.FileHandler(
    f"logs/ollama_client_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"
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

    def __init__(self, base_url: str | None = None, instance_type: str = "local") -> None:
        """OllamaClientの初期化

        Args:
            base_url: Ollama APIのベースURL
            instance_type: Ollamaのインスタンスタイプ ("local" または "docker")
        """
        # 環境変数から設定を読み込む（引数が指定されていない場合）
        if base_url is None:
            base_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

        self.base_url = base_url
        self.instance_type = instance_type
        logger.info(
            f"OllamaClient initialized with base URL: {base_url} (instance: {instance_type})"
        )

    def _prepare_request_data(
        self, prompt: str, model_name: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
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
            "stream": False,
        }

        if options:
            request_data["options"] = options

        return request_data

    def generate_text_sync(
        self,
        prompt: str,
        model_name: str = "gemma3:4b",
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
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

        # Ollamaサーバーの状態とモデルの可用性を確認
        status = self.check_ollama_availability()
        if not status["available"]:
            raise OllamaServiceError(f"Ollama server is not available: {status['error']}")

        # モデルの存在確認
        if model_name not in status["models"]:
            available_models = ", ".join(status["models"]) if status["models"] else "none"
            error_message = (
                f"Requested model '{model_name}' is not available. "
                f"Available models: {available_models}"
            )
            logger.error(error_message)
            raise OllamaServiceError(error_message)

        # テキスト生成リクエスト
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=request_data, timeout=60)
            response.raise_for_status()
            response_data = response.json()

            if "error" in response_data:
                raise OllamaServiceError(f"Ollama API error: {response_data['error']}")

            generated_text: str = response_data.get("response", "")
            return generated_text

        except requests.exceptions.ConnectionError as e:
            error_message = f"Connection error with Ollama API: {e!s}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except requests.exceptions.Timeout as e:
            error_message = f"Timeout error with Ollama API: {e!s}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with Ollama API: {e!s}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except json.JSONDecodeError:
            error_message = "Invalid JSON response from Ollama API"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except Exception as e:
            error_message = f"Unexpected error calling Ollama API: {e!s}"
            logger.exception(error_message)
            raise OllamaServiceError(error_message)

    def generate_json_sync(
        self,
        prompt: str,
        model_name: str = "gemma3:4b",
        options: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
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

        options.update(
            {
                "temperature": options.get("temperature", 0.7),
                "top_p": options.get("top_p", 0.9),
                "format": "json",
            }
        )

        raw_text = self.generate_text_sync(prompt, model_name, options)

        try:
            # JSONブロックを抽出
            json_block = self._extract_json_block(raw_text)
            json_data: Dict[str, Any] = json.loads(json_block)
            return json_data
        except json.JSONDecodeError as e:
            error_message = f"Failed to parse JSON from response: {e!s}"
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
                return text[start : end + 1]

        # 特殊なケース: テキスト全体がJSONとして解析可能な場合はそのまま返す
        try:
            json.loads(text)
            return text
        except (json.JSONDecodeError, ValueError):
            pass

        raise OllamaServiceError("Could not extract JSON block from response")

    def list_models(self) -> List[Dict[str, Any]]:
        """利用可能なモデルのリストを取得

        Returns:
            モデル情報のリスト

        Raises:
            OllamaServiceError: API呼び出しに失敗した場合
        """
        try:
            # 最初に新しいAPI（/api/models）を試す
            try:
                response = requests.get(f"{self.base_url}/api/models", timeout=10)
                response.raise_for_status()
                response_data = response.json()

                if "models" in response_data:
                    return cast(List[Dict[str, Any]], response_data["models"])
            except (requests.exceptions.RequestException, json.JSONDecodeError):
                # エラーがあれば古いAPIを試す
                logger.info("Falling back to /api/tags endpoint")

            # 古いAPI（/api/tags）を試す
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            response_data = response.json()

            if "error" in response_data:
                raise OllamaServiceError(f"Ollama API error: {response_data['error']}")

            models = response_data.get("models", [])
            return cast(List[Dict[str, Any]], models)

        except requests.exceptions.ConnectionError as e:
            error_message = f"Connection error with Ollama API: {e!s}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except requests.exceptions.Timeout as e:
            error_message = f"Timeout error with Ollama API: {e!s}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with Ollama API: {e!s}"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except json.JSONDecodeError:
            error_message = "Invalid JSON response from Ollama API"
            logger.error(error_message)
            raise OllamaServiceError(error_message)
        except Exception as e:
            error_message = f"Unexpected error calling Ollama API: {e!s}"
            logger.exception(error_message)
            raise OllamaServiceError(error_message)

    def check_ollama_availability(self) -> Dict[str, Any]:
        """Ollamaサーバーの状態と利用可能なモデルを確認

        Returns:
            状態情報の辞書:
            - "available": bool
            - "models": List[str]
            - "error": Optional[str]
            - "instance_type": str

        Note:
            このメソッドは例外を発生させず、状態情報を返す
        """
        result = {
            "available": False,
            "models": [],
            "error": None,
            "instance_type": self.instance_type,
        }

        # 複数のエンドポイントを試す
        endpoints = [
            ("api/tags", "models"),  # 一般的なエンドポイント
            ("api/models", "models"),  # 新しいバージョンのAPI
        ]

        last_error = None

        for endpoint, key in endpoints:
            try:
                # サーバーの状態確認
                response = requests.get(f"{self.base_url}/{endpoint}", timeout=5)
                response.raise_for_status()
                data = response.json()

                # 利用可能なモデルを取得
                if key in data and isinstance(data[key], list):
                    models = data[key]
                    model_names = [model.get("name") for model in models]

                    result["available"] = True
                    result["models"] = model_names
                    result["instance_info"] = f"{self.instance_type} ({endpoint})"
                    return result
                else:
                    logger.debug(
                        f"Endpoint {endpoint} responded but did not contain valid models data"
                    )
                    continue
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error on {endpoint}: {e!s}"
                logger.warning(f"Ollama server connection error on {endpoint}: {e!s}")
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout error on {endpoint}: {e!s}"
                logger.warning(f"Ollama server timeout on {endpoint}: {e!s}")
            except requests.exceptions.RequestException as e:
                last_error = f"Request error on {endpoint}: {e!s}"
                logger.warning(f"Ollama server request error on {endpoint}: {e!s}")
            except json.JSONDecodeError as e:
                last_error = f"Invalid JSON response from {endpoint}: {e!s}"
                logger.warning(f"Ollama server returned invalid JSON from {endpoint}: {e!s}")
            except Exception as e:
                last_error = f"Unexpected error on {endpoint}: {e!s}"
                logger.warning(
                    f"Unexpected error checking Ollama availability on {endpoint}: {e!s}"
                )

        # すべてのエンドポイントが失敗した場合
        result["error"] = last_error or "All endpoints failed"
        return result

    def get_detailed_status(self) -> Dict[str, Any]:
        """詳細なステータス情報を取得

        Returns:
            詳細なステータス情報の辞書
        """
        status = {
            "instance_type": self.instance_type,
            "base_url": self.base_url,
            "available": False,
            "api_version": None,
            "models": [],
            "error": None,
            "response_time_ms": 0,
        }

        # 可用性チェック
        availability = self.check_ollama_availability()
        status.update(
            {
                "available": availability["available"],
                "models": availability["models"],
                "error": availability["error"],
            }
        )

        # APIバージョンの取得を試みる
        if status["available"]:
            try:
                start_time = datetime.now()
                response = requests.get(f"{self.base_url}/api/version", timeout=5)
                end_time = datetime.now()

                if response.status_code == 200:
                    version_data = response.json()
                    status["api_version"] = version_data.get("version", "unknown")

                # レスポンス時間を計測
                response_time = (end_time - start_time).total_seconds() * 1000
                status["response_time_ms"] = round(response_time)
            except Exception as e:
                logger.warning(f"Failed to get API version: {e!s}")

        return status


class OllamaService:
    """OllamaサービスのインターフェースとなるクラスでLLMとの通信を行う"""

    def __init__(self, base_url: str | None = None, instance_type: str = "auto") -> None:
        """OllamaServiceの初期化

        Args:
            base_url: Ollama APIのベースURL
            instance_type: Ollamaのインスタンスタイプ ("local", "docker", または "auto")
                           "auto"の場合はURLに基づいて自動検出
        """
        # 環境変数から設定を読み込む（引数が指定されていない場合）
        if base_url is None:
            base_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

        if instance_type == "auto":
            instance_type = os.environ.get("OLLAMA_INSTANCE_TYPE", "auto")

        # インスタンスタイプを自動検出
        detected_type = instance_type
        if instance_type == "auto":
            if "localhost" in base_url or "127.0.0.1" in base_url:
                detected_type = "local"
            else:
                detected_type = "docker"
            logger.info(f"Auto-detected Ollama instance type: {detected_type} from URL: {base_url}")

        self.client = OllamaClient(base_url, detected_type)
        self.instance_type = detected_type
        self.base_url = base_url
        self.prompts: Dict[str, str] = {}  # プロンプトキャッシュ
        self.prompt_loader = PromptLoader()
        logger.info(f"OllamaService initialized with {detected_type} instance at {base_url}")

    def _parse_manzai_script(self, data: Union[str, Dict[str, Any]]) -> List[ScriptLine]:
        """漫才スクリプトを解析してScriptLineのリストを返す

        Args:
            data: 解析対象のデータ（文字列またはdict）

        Returns:
            ScriptLineのリスト
        """
        if isinstance(data, dict):
            if "script" not in data:
                raise OllamaServiceError("Script not found in response")
            script_data = data["script"]
            if isinstance(script_data, list):
                script_items = []
                for item in script_data:
                    if not isinstance(item, dict) or "speaker" not in item or "text" not in item:
                        continue
                    speaker = item["speaker"].strip()
                    text = item["text"].strip()
                    if not speaker or not text:
                        continue
                    role = Role.TSUKKOMI if speaker == "A" else Role.BOKE
                    script_items.append(ScriptLine(role=role, text=text))
                return script_items
            text = script_data
        else:
            text = data

        # コードブロックの抽出
        if "```" in text:
            blocks = text.split("```")
            # 奇数番目のブロック（コードブロック内）を探す
            for i, block in enumerate(blocks):
                if i % 2 == 1 and block.strip():  # コードブロック内（1, 3, 5...）
                    text = block.strip()
                    break

        # 行ごとに分割して解析
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        script_items = []

        for line in lines:
            if ":" not in line:
                continue

            speaker, content = line.split(":", 1)
            speaker = speaker.strip()
            content = content.strip()

            if not speaker or not content:
                continue

            # 話者に応じてロールを割り当て
            role = Role.TSUKKOMI if speaker == "A" else Role.BOKE
            script_items.append(ScriptLine(role=role, text=content))

        return script_items

    def check_availability(self) -> Dict[str, Any]:
        """Ollamaサービスの可用性を確認

        Returns:
            状態情報の辞書
        """
        return self.client.check_ollama_availability()

    def perform_health_check(self) -> Dict[str, Any]:
        """詳細なヘルスチェックを実行

        Returns:
            ヘルスチェック結果の辞書
            {
                "status": "healthy" | "unhealthy",
                "instance_type": str,
                "available_models": List[str],
                "latency_ms": int,
                "error": Optional[str]
            }
        """
        result = {
            "status": "unhealthy",
            "instance_type": self.instance_type,
            "available_models": [],
            "latency_ms": 0,
            "error": None,
        }

        start_time = datetime.now()
        availability = self.check_availability()
        end_time = datetime.now()

        # レイテンシを計算（ミリ秒）
        latency = (end_time - start_time).total_seconds() * 1000
        result["latency_ms"] = round(latency)

        if availability["available"]:
            result["status"] = "healthy"
            result["available_models"] = availability["models"]
        else:
            result["error"] = availability["error"]

        return result

    def generate_manzai_script(self, topic: str, model_name: str = "gemma3:4b") -> List[ScriptLine]:
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

        # Ollamaサーバーの可用性確認（詳細なヘルスチェック）
        health_check = self.perform_health_check()
        if health_check["status"] == "unhealthy":
            raise OllamaServiceError(
                f"Ollama server ({self.instance_type}) is not available: {health_check['error']}"
            )

        # 指定されたモデルが利用可能か確認
        if model_name not in health_check["available_models"]:
            available_models = (
                ", ".join(health_check["available_models"])
                if health_check["available_models"]
                else "none"
            )
            error_msg = (
                f"Model '{model_name}' not available on {self.instance_type} instance. "
                f"Available: {available_models}"
            )
            raise OllamaServiceError(error_msg)

        prompt = self.prompt_loader.load_template("manzai_prompt", topic=topic)

        try:
            logger.info(f"Generating manzai script for topic: {topic} with model: {model_name}")
            json_response = self.client.generate_json_sync(prompt, model_name)

            script = self._parse_manzai_script(json_response)
            logger.info(f"Successfully generated manzai script with {len(script)} lines")

            return script

        except (OllamaServiceError, ValueError):
            # 既存のエラーをそのまま再送出
            raise
        except Exception as e:
            error_message = f"Error generating manzai script: {e!s}"
            logger.exception(error_message)
            raise OllamaServiceError(error_message)

    def list_models(self) -> List[Dict[str, Any]]:
        """利用可能なモデルのリストを取得

        Returns:
            モデル情報のリスト

        Raises:
            OllamaServiceError: API呼び出しに失敗した場合
        """
        return self.client.list_models()

    def get_detailed_status(self) -> Dict[str, Any]:
        """Ollamaサービスの詳細なステータス情報を取得

        Returns:
            詳細なステータス情報
        """
        return self.client.get_detailed_status()

    def get_fallback_response(self, topic: str) -> List[ScriptLine]:
        """フォールバック用の応答を生成

        Args:
            topic: 話題

        Returns:
            ScriptLineのリスト
        """
        return [
            ScriptLine(
                role=Role.TSUKKOMI,
                text=f"申し訳ありません。{topic}についての漫才を生成できませんでした。",
            ),
            ScriptLine(role=Role.BOKE, text="また後で試してみましょう。"),
        ]
