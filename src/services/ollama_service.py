import requests
from typing import Dict, List, Any
import re
from src.utils.prompt_loader import load_prompt

class OllamaServiceError(Exception):
    """Ollamaサービスのエラーを表す例外クラス"""
    pass

class OllamaService:
    """Ollamaサービスとの通信を担当するクラス"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        """OllamaServiceの初期化
        
        Args:
            base_url (str): OllamaサービスのベースURL
            model (str): 使用するモデル名
        """
        self.base_url = base_url
        self.model = model
    
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
            
            # Ollamaに生成リクエストを送信
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                raise OllamaServiceError(f"Invalid response from Ollama service: {response.status_code}")
            
            # 生成されたテキストを取得
            generated_text = response.json().get("response", "")
            
            # スクリプトを解析
            script = self._parse_manzai_script(generated_text)
            
            return {"script": script}
            
        except requests.exceptions.ConnectionError:
            raise OllamaServiceError("Connection error: Failed to connect to Ollama service")
        except OllamaServiceError:
            raise
        except Exception as e:
            raise OllamaServiceError(f"Unexpected error: {str(e)}")
    
    def _parse_manzai_script(self, raw_script: str) -> List[Dict[str, str]]:
        """生成された漫才スクリプトを解析して構造化されたフォーマットに変換
        
        Args:
            raw_script (str): 生のスクリプトテキスト
            
        Returns:
            List[Dict[str, str]]: 解析されたスクリプト
        """
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