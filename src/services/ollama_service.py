import requests
from typing import Dict, List, Any

class OllamaServiceError(Exception):
    """Ollamaサービスのエラーを表す例外クラス"""
    pass

class OllamaService:
    """Ollamaサービスとの通信を担当するクラス"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        """OllamaServiceの初期化
        
        Args:
            base_url (str): OllamaサービスのベースURL
        """
        self.base_url = base_url
    
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
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"Create a manzai script about {topic}",
                    "stream": False
                }
            )
            
            if response.status_code != 200:
                raise OllamaServiceError(f"Invalid response from Ollama service: {response.status_code}")
            
            data = response.json()
            if 'script' not in data:
                raise OllamaServiceError("Invalid script format in response")
            
            return data
            
        except requests.exceptions.ConnectionError:
            raise OllamaServiceError("Connection error: Failed to connect to Ollama service")
        except OllamaServiceError:
            raise
        except Exception as e:
            raise OllamaServiceError(f"Unexpected error: {str(e)}") 