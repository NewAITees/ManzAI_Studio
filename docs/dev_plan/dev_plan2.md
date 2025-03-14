# ManzAI Studio 開発工程書

## 開発ステップ2: Ollama連携による漫才生成機能の実装

### Ollamaサービスの実装

1. **Ollamaサービスクラスの作成**
   ```bash
   mkdir -p src/backend/app/services
   touch src/backend/app/services/__init__.py
   touch src/backend/app/services/ollama_service.py
   ```

2. **Ollamaサービスの基本実装**
   ```python
   # src/backend/app/services/ollama_service.py
   import json
   import requests
   from typing import Dict, Any, Optional
   from flask import current_app

   class OllamaService:
       """Service for interacting with Ollama API."""
       
       def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
           """Initialize OllamaService.
           
           Args:
               base_url: Ollama API base URL. Defaults to app config.
               model: Ollama model to use. Defaults to app config.
           """
           self.base_url = base_url or current_app.config["OLLAMA_URL"]
           self.model = model or current_app.config["OLLAMA_MODEL"]
           
       def generate_text(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
           """Generate text using Ollama API.
           
           Args:
               prompt: The prompt to generate text from.
               temperature: Controls randomness. Higher is more random.
               max_tokens: Maximum number of tokens to generate.
               
           Returns:
               Generated text.
               
           Raises:
               RuntimeError: If the API request fails.
           """
           endpoint = f"{self.base_url}/api/generate"
           
           payload = {
               "model": self.model,
               "prompt": prompt,
               "temperature": temperature,
               "max_tokens": max_tokens
           }
           
           try:
               response = requests.post(endpoint, json=payload)
               response.raise_for_status()
               return response.json().get("response", "")
           except requests.RequestException as e:
               raise RuntimeError(f"Failed to generate text: {str(e)}")
   ```

### 漫才生成プロンプトの設計

1. **プロンプトテンプレートの作成**
   ```bash
   mkdir -p src/backend/app/templates
   touch src/backend/app/templates/manzai_prompt.txt
   ```

2. **漫才生成用プロンプトの実装**
   ```
   # src/backend/app/templates/manzai_prompt.txt
   あなたは熟練した漫才作家です。以下のトピックに基づいて、ツッコミとボケの二人組による約2分間の漫才の台本を作成してください。

   トピック: {{topic}}

   以下の形式で出力してください:
   ```
   A: (ツッコミ役の台詞)
   B: (ボケ役の台詞)
   A: (ツッコミ役の台詞)
   ...
   ```

   注意点:
   - 「A」はツッコミ役、「B」はボケ役を表します
   - 各台詞は1行ずつ、A: またはB: の形式で記述してください
   - コロンの後には必ず半角スペースを入れてください
   - 台詞以外の説明や補足は含めないでください
   - 適度なテンポで漫才を進行させてください
   - 日本語で作成してください
   ```

3. **プロンプトローダーユーティリティの作成**
   ```bash
   mkdir -p src/backend/app/utils
   touch src/backend/app/utils/__init__.py
   touch src/backend/app/utils/prompt_loader.py
   ```

   ```python
   # src/backend/app/utils/prompt_loader.py
   import os
   from typing import Dict, Any
   
   def load_prompt(template_name: str, **kwargs: Any) -> str:
       """Load a prompt template and format it with the given kwargs.
       
       Args:
           template_name: Name of the template file without extension.
           **kwargs: Variables to format the template with.
           
       Returns:
           Formatted prompt.
       """
       template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
       template_path = os.path.join(template_dir, f"{template_name}.txt")
       
       with open(template_path, "r", encoding="utf-8") as file:
           template = file.read()
           
       return template.format(**{k: v for k, v in kwargs.items()})
   ```

### 漫才生成APIエンドポイントの実装

1. **APIルートの実装**
   ```python
   # src/backend/app/routes/api.py の generate_manzai 関数を更新
   from flask import Blueprint, jsonify, request, current_app
   from typing import Dict, Any
   import re

   from backend.app.services.ollama_service import OllamaService
   from backend.app.utils.prompt_loader import load_prompt

   bp = Blueprint("api", __name__, url_prefix="/api")

   # health_check関数は既存のまま

   @bp.route("/generate", methods=["POST"])
   def generate_manzai() -> Dict[str, Any]:
       """Generate manzai script using Ollama.
       
       Returns:
           Dict containing the generated script.
       """
       data = request.get_json()
       if not data or "topic" not in data:
           return jsonify({"error": "No topic provided"}), 400
           
       topic = data["topic"]
       temperature = data.get("temperature", 0.7)
       
       try:
           # Load prompt template
           prompt = load_prompt("manzai_prompt", topic=topic)
           
           # Generate script
           ollama_service = OllamaService()
           raw_response = ollama_service.generate_text(
               prompt=prompt,
               temperature=temperature,
               max_tokens=1500
           )
           
           # Parse the script
           script_lines = parse_manzai_script(raw_response)
           
           return jsonify({
               "topic": topic,
               "script": script_lines
           })
       except Exception as e:
           current_app.logger.error(f"Error generating manzai: {str(e)}")
           return jsonify({"error": str(e)}), 500
   ```

2. **スクリプト解析関数の追加**
   ```python
   # src/backend/app/routes/api.py に追加
   def parse_manzai_script(raw_script: str) -> list[Dict[str, str]]:
       """Parse raw manzai script into structured format.
       
       Args:
           raw_script: Raw script from Ollama.
           
       Returns:
           List of dialogue lines with speaker and text.
       """
       # コードブロックから内容を抽出
       code_block_pattern = r"```(.*?)```"
       match = re.search(code_block_pattern, raw_script, re.DOTALL)
       if match:
           script_content = match.group(1)
       else:
           script_content = raw_script
           
       # 各行をパース
       result = []
       pattern = r"([AB]):\s+(.*)"
       
       for line in script_content.splitlines():
           match = re.match(pattern, line.strip())
           if match:
               speaker, text = match.groups()
               result.append({
                   "speaker": "tsukkomi" if speaker == "A" else "boke",
                   "text": text
               })
               
       return result
   ```

### 単体テストの実装

1. **Ollamaサービスのモックテスト**
   ```bash
   touch src/backend/tests/test_ollama_service.py
   ```

   ```python
   # src/backend/tests/test_ollama_service.py
   import pytest
   from unittest.mock import patch, MagicMock
   from backend.app.services.ollama_service import OllamaService

   @patch("backend.app.services.ollama_service.requests.post")
   def test_generate_text_success(mock_post):
       # Requestsの応答をモック
       mock_response = MagicMock()
       mock_response.json.return_value = {"response": "Generated text"}
       mock_post.return_value = mock_response
       
       # サービスをテスト
       service = OllamaService(base_url="http://test", model="test-model")
       result = service.generate_text("Test prompt")
       
       # 期待される結果を検証
       assert result == "Generated text"
       mock_post.assert_called_once()
       
   @patch("backend.app.services.ollama_service.requests.post")
   def test_generate_text_error(mock_post):
       # 例外をスロー
       mock_post.side_effect = Exception("API error")
       
       # サービスをテスト
       service = OllamaService(base_url="http://test", model="test-model")
       
       # 例外が発生するか検証
       with pytest.raises(RuntimeError):
           service.generate_text("Test prompt")
   ```

2. **APIエンドポイントのテスト拡張**
   ```python
   # src/backend/tests/test_api.py に追加
   @patch("backend.app.routes.api.OllamaService")
   def test_generate_manzai_success(mock_ollama_service, client: FlaskClient) -> None:
       # OllamaServiceをモック
       mock_instance = mock_ollama_service.return_value
       mock_instance.generate_text.return_value = """
       ```
       A: こんにちは、今日のお題は「猫」ですね！
       B: そうそう、猫といえば最近うちで飼い始めたんだよ
       A: へー、どんな猫なの？
       ```
       """
       
       # APIを呼び出し
       response = client.post("/api/generate", json={"topic": "猫"})
       
       # 期待される結果を検証
       assert response.status_code == 200
       assert "script" in response.json
       assert len(response.json["script"]) == 3
       assert response.json["script"][0]["speaker"] == "tsukkomi"
       assert "こんにちは" in response.json["script"][0]["text"]
   ```

### 実装のテストと検証

1. **ユニットテストの実行**
   ```bash
   poetry run pytest
   ```

2. **手動テスト用スクリプト**
   ```bash
   mkdir -p scripts
   touch scripts/test_manzai_generation.py
   ```

   ```python
   # scripts/test_manzai_generation.py
   import requests
   import json

   def main():
       url = "http://localhost:5000/api/generate"
       payload = {
           "topic": "スマートフォン"
       }
       
       response = requests.post(url, json=payload)
       print(f"Status Code: {response.status_code}")
       
       if response.status_code == 200:
           data = response.json()
           print("\nGenerated Manzai Script:")
           for line in data["script"]:
               speaker = "A" if line["speaker"] == "tsukkomi" else "B"
               print(f"{speaker}: {line['text']}")
       else:
           print(f"Error: {response.text}")

   if __name__ == "__main__":
       main()
   ```

3. **手動テスト実行**
   ```bash
   # バックエンドサーバーを起動
   poetry run python -m flask --app backend/app/__init__.py run --debug
   
   # 別のターミナルで
   poetry run python scripts/test_manzai_generation.py
   ```

この開発ステップでは、Ollamaと連携して漫才台本を生成する機能を実装しました。LLMを使用して自然な漫才の会話を生成し、それを構造化されたデータとして提供するAPIエンドポイントが完成しました。次のステップでは、VoiceVoxを使用して生成された台本から音声を合成する機能を実装します。