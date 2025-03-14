# ManzAI Studio 開発工程書

## 開発ステップ9: テスト、ドキュメント、デプロイメントプロセスの実装

### テスト拡充

1. **テスト設定とヘルパーの強化**
   ```bash
   # テスト設定とヘルパーを強化
   cat > src/backend/tests/test_helpers.py << 'EOF'
   """テストヘルパー関数"""
   import os
   import json
   import tempfile
   from typing import Dict, Any, List
   from flask import Flask
   from flask.testing import FlaskClient
   
   
   def load_test_data(filename: str) -> Dict[str, Any]:
       """テストデータを読み込む
       
       Args:
           filename: 読み込むファイル名
           
       Returns:
           テストデータ
       """
       base_dir = os.path.dirname(os.path.abspath(__file__))
       data_dir = os.path.join(base_dir, "data")
       file_path = os.path.join(data_dir, filename)
       
       with open(file_path, "r", encoding="utf-8") as f:
           return json.load(f)
   
   
   def create_test_file(content: str, extension: str = ".txt") -> str:
       """テスト用の一時ファイルを作成する
       
       Args:
           content: ファイルの内容
           extension: ファイル拡張子
           
       Returns:
           作成したファイルのパス
       """
       fd, path = tempfile.mkstemp(suffix=extension)
       try:
           with os.fdopen(fd, "w") as f:
               f.write(content)
       except:
           os.unlink(path)
           raise
       
       return path
   
   
   def auth_client(client: FlaskClient, token: str = None) -> FlaskClient:
       """テスト用のクライアントに認証情報を設定する
       
       Args:
           client: テスト用クライアント
           token: 認証トークン
           
       Returns:
           認証情報を設定したクライアント
       """
       # 現在は認証機能がないので、そのままクライアントを返す
       return client
   
   
   def assert_status_code(response, expected_code: int = 200):
       """レスポンスのステータスコードを検証する
       
       Args:
           response: レスポンス
           expected_code: 期待されるステータスコード
       """
       assert response.status_code == expected_code, \
           f"Expected status code {expected_code}, got {response.status_code}"
   
   
   def create_test_app() -> Flask:
       """テスト用のFlaskアプリケーションを作成する
       
       Returns:
           テスト用のFlaskアプリケーション
       """
       from backend.app import create_app
       from backend.app.config import TestConfig
       
       app = create_app(TestConfig())
       
       # テスト用の設定を追加
       app.config["TESTING"] = True
       app.config["SERVER_NAME"] = "localhost.localdomain"
       
       return app
   EOF
   ```

2. **APIテストの拡充**
   ```bash
   # APIテストを拡充
   mkdir -p src/backend/tests/data
   cat > src/backend/tests/data/test_script.json << 'EOF'
   {
     "topic": "スマートフォン",
     "script": [
       {
         "speaker": "tsukkomi",
         "text": "今日はスマートフォンについて話しましょうか！"
       },
       {
         "speaker": "boke",
         "text": "あぁ、あの賢い電話ってやつですね！"
       },
       {
         "speaker": "tsukkomi",
         "text": "そうそう、スマートフォン。もう今や生活に欠かせないアイテムになってるよね。"
       },
       {
         "speaker": "boke",
         "text": "ホント、私なんかもう手放せませんよ！毎朝、枕元にスマホが無いと目覚められないくらいです。"
       },
       {
         "speaker": "tsukkomi",
         "text": "それ依存症じゃない？"
       }
     ]
   }
   EOF
   
   cat > src/backend/tests/test_manzai_api.py << 'EOF'
   """漫才APIのテスト"""
   import json
   import pytest
   from unittest.mock import patch, MagicMock
   from flask.testing import FlaskClient
   
   from backend.app.services.ollama_service import OllamaService
   from backend.app.services.voicevox_service import VoiceVoxService
   from .test_helpers import load_test_data, assert_status_code
   
   
   def test_health_check(client: FlaskClient):
       """ヘルスチェックAPIのテスト"""
       response = client.get("/api/health")
       assert_status_code(response)
       assert response.json["status"] == "healthy"
   
   
   @patch("backend.app.routes.api.OllamaService")
   @patch("backend.app.routes.api.requests.get")
   def test_generate_manzai_success(mock_get, mock_ollama, client: FlaskClient):
       """漫才生成APIの成功テスト"""
       # Ollamaサーバー起動チェックのモック
       mock_get.return_value = MagicMock(status_code=200)
       
       # OllamaServiceのモック
       mock_instance = mock_ollama.return_value
       mock_instance.generate_text.return_value = """
       ```
       A: 今日はスマートフォンについて話しましょうか！
       B: あぁ、あの賢い電話ってやつですね！
       A: そうそう、スマートフォン。もう今や生活に欠かせないアイテムになってるよね。
       B: ホント、私なんかもう手放せませんよ！毎朝、枕元にスマホが無いと目覚められないくらいです。
       A: それ依存症じゃない？
       ```
       """
       
       # APIを呼び出し
       response = client.post("/api/generate", json={"topic": "スマートフォン"})
       
       # 応答を検証
       assert_status_code(response)
       assert "script" in response.json
       assert len(response.json["script"]) == 5
       assert response.json["script"][0]["speaker"] == "tsukkomi"
       assert "今日は" in response.json["script"][0]["text"]
       assert response.json["topic"] == "スマートフォン"
   
   
   @patch("backend.app.routes.api.OllamaService")
   @patch("backend.app.routes.api.requests.get")
   def test_generate_manzai_error(mock_get, mock_ollama, client: FlaskClient):
       """漫才生成APIのエラーテスト - サーバー接続エラー"""
       # Ollamaサーバー起動チェックのモック - 接続エラー
       mock_get.side_effect = Exception("Connection error")
       
       # APIを呼び出し
       response = client.post("/api/generate", json={"topic": "スマートフォン"})
       
       # 応答を検証 - エラーコード503を期待
       assert_status_code(response, 503)
       assert "error" in response.json
   
   
   @patch("backend.app.routes.api.VoiceVoxService")
   @patch("backend.app.routes.api.requests.get")
   def test_synthesize_script(mock_get, mock_voicevox, client: FlaskClient):
       """台本音声合成APIのテスト"""
       # VoiceVoxサーバー起動チェックのモック
       mock_get.return_value = MagicMock(status_code=200)
       
       # VoiceVoxServiceのモック
       mock_instance = mock_voicevox.return_value
       mock_instance.synthesize_voice.return_value = (
           "/path/to/audio.wav",
           {"accent_phrases": []}
       )
       
       # テスト用の台本
       test_script = load_test_data("test_script.json")["script"]
       
       # APIを呼び出し
       response = client.post("/api/synthesize_script", json={
           "script": test_script,
           "tsukkomi_id": 1,
           "boke_id": 3
       })
       
       # 応答を検証
       assert_status_code(response)
       assert "results" in response.json
       assert len(response.json["results"]) == len(test_script)
   
   
   @patch("backend.app.routes.api.VoiceVoxService")
   @patch("backend.app.routes.api.requests.get")
   def test_get_speakers(mock_get, mock_voicevox, client: FliskClient):
       """話者一覧取得APIのテスト"""
       # VoiceVoxサーバー起動チェックのモック
       mock_get.return_value = MagicMock(status_code=200)
       
       # VoiceVoxServiceのモック
       mock_instance = mock_voicevox.return_value
       mock_instance.get_speakers.return_value = [
           {
               "name": "四国めたん",
               "styles": [
                   {"id": 2, "name": "ノーマル"}
               ]
           },
           {
               "name": "ずんだもん",
               "styles": [
                   {"id": 3, "name": "ノーマル"}
               ]
           }
       ]
       
       # APIを呼び出し
       response = client.get("/api/speakers")
       
       # 応答を検証
       assert_status_code(response)
       assert "speakers" in response.json
       assert len(response.json["speakers"]) == 2
   EOF
   ```

3. **モデルテストの追加**
   ```bash
   # モデル管理APIのテスト
   cat > src/backend/tests/test_models_api.py << 'EOF'
   """モデル管理APIのテスト"""
   import json
   import os
   import pytest
   from unittest.mock import patch, MagicMock
   from flask.testing import FlaskClient
   
   from .test_helpers import assert_status_code, create_test_file
   
   
   @patch("backend.app.routes.models.os.path.exists")
   @patch("backend.app.routes.models.glob.glob")
   @patch("backend.app.routes.models.open")
   @patch("backend.app.routes.models.json.load")
   def test_get_live2d_models(mock_json_load, mock_open, mock_glob, mock_exists, client: FlaskClient):
       """Live2Dモデル一覧取得APIのテスト"""
       # ディレクトリ存在確認のモック
       mock_exists.return_value = True
       
       # モデルディレクトリ取得のモック
       mock_glob.return_value = [
           "/app/frontend/public/live2d/models/character1/",
           "/app/frontend/public/live2d/models/character2/"
       ]
       
       # モデルファイルの内容モック
       mock_json_load.side_effect = [
           {"name": "キャラクター1", "type": "tsukkomi"},
           {"name": "キャラクター2", "type": "boke"}
       ]
       
       # ファイル存在確認のモック
       mock_exists.side_effect = lambda path: True
       
       # APIを呼び出し
       response = client.get("/api/models/live2d")
       
       # 応答を検証
       assert_status_code(response)
       assert "models" in response.json
       assert len(response.json["models"]) == 2
       assert response.json["models"][0]["name"] == "キャラクター1"
       assert response.json["models"][1]["type"] == "boke"
   
   
   @patch("backend.app.routes.models.os.makedirs")
   @patch("backend.app.routes.models.open")
   @patch("backend.app.routes.models.json.dump")
   def test_register_model(mock_json_dump, mock_open, mock_makedirs, client: FlaskClient):
       """モデル登録APIのテスト"""
       # APIを呼び出し
       response = client.post("/api/models/live2d/register", json={
           "id": "test_model",
           "name": "テストモデル",
           "path": "/path/to/model3.json",
           "type": "tsukkomi",
           "textures": ["texture.png"]
       })
       
       # 応答を検証
       assert_status_code(response)
       assert response.json["success"] is True
       assert "model" in response.json
       assert response.json["model"]["name"] == "テストモデル"
       
       # モックの呼び出しを検証
       mock_makedirs.assert_called_once()
       mock_open.assert_called_once()
       mock_json_dump.assert_called_once()
   EOF
   ```

4. **プロンプトAPIテスト**
   ```bash
   # プロンプト管理APIのテスト
   cat > src/backend/tests/test_prompts_api.py << 'EOF'
   """プロンプト管理APIのテスト"""
   import json
   import os
   import pytest
   from unittest.mock import patch, MagicMock, mock_open
   from flask.testing import FlaskClient
   
   from .test_helpers import assert_status_code
   
   
   @patch("backend.app.routes.prompts.os.path.exists")
   @patch("backend.app.routes.prompts.os.listdir")
   @patch("backend.app.routes.prompts.open", new_callable=mock_open, read_data="Test prompt content")
   @patch("backend.app.routes.prompts.json.load")
   def test_get_prompts(mock_json_load, mock_file, mock_listdir, mock_exists, client: FlaskClient):
       """プロンプト一覧取得APIのテスト"""
       # ディレクトリ存在確認のモック
       mock_exists.return_value = True
       
       # プロンプトファイル一覧のモック
       mock_listdir.return_value = [
           "manzai_prompt.txt",
           "manzai_prompt.meta.json",
           "custom_prompt.txt"
       ]
       
       # メタデータファイルの内容モック
       mock_json_load.side_effect = [
           {
               "name": "漫才プロンプト",
               "description": "標準の漫才プロンプト",
               "isDefault": True
           },
           {}  # custom_promptにはメタデータなし
       ]
       
       # メタデータファイルの存在確認モック
       mock_exists.side_effect = lambda path: "manzai_prompt.meta.json" in path
       
       # APIを呼び出し
       response = client.get("/api/prompts")
       
       # 応答を検証
       assert_status_code(response)
       assert "prompts" in response.json
       assert len(response.json["prompts"]) == 2
       assert response.json["prompts"][0]["name"] == "漫才プロンプト"
       assert response.json["prompts"][0]["isDefault"] is True
       assert response.json["prompts"][1]["name"] == "custom_prompt"
   
   
   @patch("backend.app.routes.prompts.os.path.exists")
   @patch("backend.app.routes.prompts.open", new_callable=mock_open, read_data="Test prompt content")
   def test_get_prompt(mock_file, mock_exists, client: FlaskClient):
       """プロンプト取得APIのテスト"""
       # ファイル存在確認のモック
       mock_exists.return_value = True
       
       # APIを呼び出し
       response = client.get("/api/prompts/manzai_prompt")
       
       # 応答を検証
       assert_status_code(response)
       assert response.json["id"] == "manzai_prompt"
       assert response.json["content"] == "Test prompt content"
   
   
   @patch("backend.app.routes.prompts.os.path.exists")
   @patch("backend.app.routes.prompts.open", new_callable=mock_open)
   @patch("backend.app.routes.prompts.json.dump")
   def test_create_prompt(mock_json_dump, mock_file, mock_exists, client: FlaskClient):
       """プロンプト作成APIのテスト"""
       # ファイル存在確認のモック - 存在しない設定
       mock_exists.return_value = False
       
       # APIを呼び出し
       response = client.post("/api/prompts", json={
           "id": "new_prompt",
           "name": "新しいプロンプト",
           "description": "テスト用プロンプト",
           "content": "これはテスト用のプロンプトです。",
           "parameters": ["topic"]
       })
       
       # 応答を検証
       assert_status_code(response)
       assert response.json["success"] is True
       assert response.json["prompt"]["name"] == "新しいプロンプト"
       
       # モックの呼び出しを検証
       assert mock_file.call_count == 2  # contentとmetadata
       mock_json_dump.assert_called_once()
   EOF
   ```

5. **E2Eテストスクリプト**
   ```bash
   # E2Eテストスクリプトを作成
   mkdir -p tests
   cat > tests/e2e_tests.py << 'EOF'
   #!/usr/bin/env python3
   """エンドツーエンドテスト"""
   import os
   import sys
   import time
   import argparse
   import requests
   import json
   
   # デフォルトのAPIエンドポイント
   DEFAULT_API_URL = "http://localhost:5000/api"
   
   
   def test_health(api_url):
       """ヘルスチェックAPIのテスト"""
       print("ヘルスチェックテスト...")
       response = requests.get(f"{api_url}/health")
       assert response.status_code == 200, f"ヘルスチェック失敗: {response.status_code}"
       assert response.json()["status"] == "healthy", "ヘルスステータスが不正"
       print("ヘルスチェックテスト成功")
   
   
   def test_manzai_generation(api_url):
       """漫才生成APIのテスト"""
       print("漫才生成テスト...")
       response = requests.post(f"{api_url}/generate", json={"topic": "テスト"})
       assert response.status_code == 200, f"漫才生成失敗: {response.status_code}"
       assert "script" in response.json(), "レスポンスにscriptが含まれていない"
       assert len(response.json()["script"]) > 0, "生成された台本が空"
       print(f"漫才生成テスト成功: {len(response.json()['script'])}行の台本を生成")
       return response.json()["script"]
   
   
   def test_voice_synthesis(api_url, script):
       """音声合成APIのテスト"""
       print("音声合成テスト...")
       response = requests.post(f"{api_url}/synthesize_script", json={
           "script": script,
           "tsukkomi_id": 1,
           "boke_id": 3
       })
       assert response.status_code == 200, f"音声合成失敗: {response.status_code}"
       assert "results" in response.json(), "レスポンスにresultsが含まれていない"
       assert len(response.json()["results"]) > 0, "合成結果が空"
       print(f"音声合成テスト成功: {len(response.json()['results'])}個の音声ファイルを生成")
   
   
   def test_speakers(api_url):
       """話者一覧APIのテスト"""
       print("話者一覧テスト...")
       response = requests.get(f"{api_url}/speakers")
       assert response.status_code == 200, f"話者一覧取得失敗: {response.status_code}"
       assert "speakers" in response.json(), "レスポンスにspeakersが含まれていない"
       assert len(response.json()["speakers"]) > 0, "話者一覧が空"
       print(f"話者一覧テスト成功: {len(response.json()['speakers'])}人の話者を取得")
   
   
   def test_resource_stats(api_url):
       """リソース統計APIのテスト"""
       print("リソース統計テスト...")
       response = requests.get(f"{api_url}/resources/stats")
       assert response.status_code == 200, f"リソース統計取得失敗: {response.status_code}"
       assert "cpu_percent" in response.json(), "レスポンスにcpu_percentが含まれていない"
       print("リソース統計テスト成功")
   
   
   def test_saved_scripts(api_url):
       """保存済み台本APIのテスト"""
       print("保存済み台本テスト...")
       response = requests.get(f"{api_url}/recovery/scripts")
       assert response.status_code == 200, f"保存済み台本取得失敗: {response.status_code}"
       assert "scripts" in response.json(), "レスポンスにscriptsが含まれていない"
       print(f"保存済み台本テスト成功: {len(response.json()['scripts'])}個の台本を取得")
   
   
   def run_all_tests(api_url=DEFAULT_API_URL):
       """全てのテストを実行する"""
       print(f"APIエンドポイント: {api_url}")
       
       try:
           # ヘルスチェック
           test_health(api_url)
           
           # 話者一覧
           test_speakers(api_url)
           
           # 漫才生成
           script = test_manzai_generation(api_url)
           
           # 音声合成
           test_voice_synthesis(api_url, script)
           
           # リソース統計
           test_resource_stats(api_url)
           
           # 保存済み台本
           test_saved_scripts(api_url)
           
           print("\n全てのテストが成功しました！")
           return 0
       except Exception as e:
           print(f"\nテスト失敗: {str(e)}")
           return 1
   
   
   if __name__ == "__main__":
       parser = argparse.ArgumentParser(description="ManzAI Studio E2Eテスト")
       parser.add_argument("--api-url", default=DEFAULT_API_URL, help="APIエンドポイントのURL")
       args = parser.parse_args()
       
       sys.exit(run_all_tests(args.api_url))
   EOF
   
   chmod +x tests/e2e_tests.py
   ```

### ユーザードキュメントの整備

1. **ユーザーガイドの作成**
   ```bash
   # ユーザーガイドを作成
   mkdir -p docs/user_guide
   cat > docs/user_guide/README.md << 'EOF'
   # ManzAI Studio ユーザーガイド
   
   このガイドでは、ManzAI Studioの基本的な使い方を説明します。
   
   ## 目次
   
   1. [はじめに](#はじめに)
   2. [インストール](#インストール)
   3. [基本的な使い方](#基本的な使い方)
   4. [カスタマイズ](#カスタマイズ)
   5. [トラブルシューティング](#トラブルシューティング)
   
   ## はじめに
   
   ManzAI Studioは、完全にローカルで動作する漫才生成・実演Webアプリケーションです。OllamaのLLMを使用して漫才の台本を生成し、Live2Dキャラクターとボイスボックスを使用して、アニメーションと音声で実演します。
   
   ## インストール
   
   詳細なインストール手順については、[インストールガイド](./installation.md)を参照してください。
   
   ## 基本的な使い方
   
   1. **アプリケーションの起動**
   
      ```bash
      # Docker Composeを使用して起動
      docker-compose up -d
      
      # または直接起動
      ./start_dev.sh
      ```
   
   2. **漫才の生成**
   
      - トピックを入力フィールドに入力します（例：「スマートフォン」「旅行」「猫」など）
      - 「漫才を生成」ボタンをクリックします
      - 生成が完了するまで待ちます
   
   3. **漫才の実演**
   
      - 生成が完了したら、ステージ上の「漫才を再生」ボタンをクリックします
      - Live2Dキャラクターがアニメーションと音声で漫才を実演します
   
   詳細な使用方法については、[操作ガイド](./usage.md)を参照してください。
   
   ## カスタマイズ
   
   ManzAI Studioでは、以下の要素をカスタマイズできます：
   
   - **キャラクターモデル**: 設定メニューから、ツッコミ役とボケ役のLive2Dモデルを変更できます
   - **キャラクターボイス**: 設定メニューから、各キャラクターの声を変更できます
   - **プロンプト**: 漫才生成に使用するプロンプトをカスタマイズできます
   
   詳細なカスタマイズ方法については、[カスタマイズガイド](./customization.md)を参照してください。
   
   ## トラブルシューティング
   
   よくある問題と解決方法については、[トラブルシューティングガイド](./troubleshooting.md)を参照してください。
   EOF
   
   # インストールガイド
   cat > docs/user_guide/installation.md << 'EOF'
   # インストールガイド
   
   このガイドでは、ManzAI Studioのインストール方法を説明します。
   
   ## 必要要件
   
   ### システム要件
   - Python 3.10以上
   - Node.js 18.0.0以上
   - Docker（推奨）
   - 4GB以上のRAM
   - 2GB以上の空き容量（モデルファイル用）
   
   ### 必須コンポーネント
   - [Ollama](https://ollama.ai/) - LLM実行環境
   - [VoiceVox](https://voicevox.hiroshiba.jp/) - 音声合成エンジン
   - Live2D Cubism SDK for Web
   
   ## インストール方法
   
   ### 方法1: Docker Composeを使用する（推奨）
   
   1. リポジトリをクローン
      ```bash
      git clone https://github.com/yourusername/manzai-studio.git
      cd manzai-studio
      ```
   
   2. Docker Composeで起動
      ```bash
      docker-compose up -d
      ```
   
   3. ブラウザで以下のURLにアクセス
      ```
      http://localhost:5000
      ```
   
   ### 方法2: 直接インストール
   
   1. リポジトリをクローン
      ```bash
      git clone https://github.com/yourusername/manzai-studio.git
      cd manzai-studio
      ```
   
   2. pyenvとPoetryのインストール
      ```bash
      # macOSの場合
      brew install pyenv poetry
      
      # Linuxの場合
      curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
      curl -sSL https://install.python-poetry.org | python3 -
      ```
   
   3. Pythonのインストールと設定
      ```bash
      pyenv install 3.10.13
      pyenv local 3.10.13
      ```
   
   4. Poetryの依存関係をインストール
      ```bash
      poetry install
      ```
   
   5. Ollamaのインストールと必要なモデルのダウンロード
      ```bash
      # macOSとLinux
      curl -fsSL https://ollama.ai/install.sh | sh
      ollama pull phi
      ```
   
   6. VoiceVoxのインストール
      [VoiceVox公式サイト](https://voicevox.hiroshiba.jp/)からダウンロードしてインストール
   
   7. フロントエンドの依存関係をインストール
      ```bash
      cd frontend
      npm install
      ```
   
   8. 開発サーバーの起動
      ```bash
      cd ..
      ./start_dev.sh
      ```
   
   9. ブラウザで以下のURLにアクセス
      ```
      http://localhost:3000
      ```
   
   ## トラブルシューティング
   
   インストール中に問題が発生した場合は、以下を確認してください：
   
   1. **Ollamaが起動しない場合**
      - Ollamaが正しくインストールされているか確認
      - `ollama serve`コマンドを実行してサーバーを手動で起動
   
   2. **VoiceVoxが起動しない場合**
      - VoiceVoxアプリケーションを手動で起動
      - ポート50021が利用可能か確認
   
   3. **Pythonバージョンの問題**
      - `python --version`で正しいバージョン（3.10以上）が使用されているか確認
      - pyenvが正しく設定されているか確認
   
   4. **依存関係のエラー**
      - `poetry install --verbose`を実行して詳細なエラーメッセージを確認
   
   詳細なトラブルシューティングについては、[トラブルシューティングガイド](./troubleshooting.md)を参照してください。
   EOF
   
   # 操作ガイド
   cat > docs/user_guide/usage.md << 'EOF'
   # 操作ガイド
   
   このガイドでは、ManzAI Studioの基本的な操作方法を説明します。
   
   ## 基本操作
   
   ### 1. アプリケーションへのアクセス
   
   ブラウザで以下のURLにアクセスします：
   
   - Docker Compose使用時: `http://localhost:5000`
   - 直接起動時: `http://localhost:3000`
   
   ### 2. 漫才の生成
   
   1. メイン画面の右側にある入力フォームを使用します
   2. 「トピック」欄に漫才のテーマを入力します（例：「スマートフォン」「旅行」「猫」など）
   3. 必要に応じて、ツッコミ役とボケ役の声を選択します
   4. 「漫才を生成」ボタンをクリックします
   5. 生成処理中はプログレスバーが表示されます
   6. 生成が完了すると、左側のステージに「漫才を再生」ボタンが表示されます
   
   ### 3. 漫才の実演
   
   1. 生成が完了したら、ステージ上の「漫才を再生」ボタンをクリックします
   2. Live2Dキャラクターがアニメーションと音声で漫才を実演します
   3. 画面下部に現在のセリフが表示されます
   4. 全ての台詞が終了すると、再度「漫才を再生」ボタンが表示されます
   
   ### 4. 設定へのアクセス
   
   1. 画面右上の「設定」ボタンをクリックします
   2. 設定画面では以下の項目を変更できます：
      - キャラクターモデル設定
      - プロンプト設定
   3. 設定を完了したら、「ホームに戻る」ボタンをクリックしてメイン画面に戻ります
   
   ## キャラクターモデルの設定
   
   1. 設定画面の「キャラクターモデル」タブをクリックします
   2. 「ツッコミ役」または「ボケ役」のタブを選択します
   3. 利用可能なモデル一覧から使用したいモデルをクリックして選択します
   4. 設定は自動的に保存され、次回の漫才生成時に適用されます
   
   ## プロンプト設定
   
   1. 設定画面の「プロンプト設定」タブをクリックします
   2. 既存のプロンプトを選択して「編集」ボタンをクリックすると、内容を編集できます
   3. 「新規プロンプト」を選択すると、新しいプロンプトを作成できます
   4. プロンプト編集画面では以下の項目を設定できます：
      - プロンプト名
      - 説明
      - プロンプト内容（`{{topic}}`などのパラメータを使用可能）
   5. 「保存」ボタンをクリックして変更を保存します
   
   ## ヒントとコツ
   
   - **トピックの選び方**: 具体的なトピックほど面白い漫才が生成されやすいです
   - **キャラクターボイスの組み合わせ**: 声の特徴が異なる組み合わせを選ぶと聞き分けやすくなります
   - **カスタムプロンプト**: プロンプトをカスタマイズすることで、特定のスタイルの漫才を生成できます
   - **定期的な実行**: サーバーを長時間起動したままにすると、パフォーマンスが低下する場合があります。定期的に再起動することをお勧めします
   EOF
   
   # カスタマイズガイド
   cat > docs/user_guide/customization.md << 'EOF'
   # カスタマイズガイド
   
   このガイドでは、ManzAI Studioのカスタマイズ方法について説明します。
   
   ## Live2Dモデルのカスタマイズ
   
   ### 独自のLive2Dモデルを追加する
   
   1. モデルファイルの準備:
      - Live2D Cubism Viewerなどでエクスポートしたモデルファイル（.model3.json）
      - テクスチャファイル（.png）
      - サムネイル画像（thumbnail.png、オプション）
   
   2. モデルを配置:
      ```
      frontend/public/live2d/models/[モデル名]/
      ```
   
   3. メタデータファイルの作成:
      - 以下のコマンドを実行してメタデータファイルを作成します
      ```bash
      node scripts/create_model_metadata.js
      ```
      - または手動で`model.json`ファイルを以下の内容で作成します
      ```json
      {
        "name": "モデル名",
        "type": "tsukkomi", // または "boke"
        "model": "model3.json", // モデルファイル名
        "textures": ["texture.png"], // テクスチャファイル名の配列
        "version": "1.0.0"
      }
      ```
   
   4. アプリケーションを再起動すると、新しいモデルが設定画面に表示されます
   
   詳細な手順については、[モデル設定ガイド](../model_setup.md)を参照してください。
   
   ## プロンプトのカスタマイズ
   
   ### プロンプトを編集する
   
   1. 設定メニューから「プロンプト設定」タブを選択
   2. 編集したいプロンプトを選択して「編集」ボタンをクリック
   3. プロンプト内容を編集
   4. 「保存」ボタンをクリック
   
   ### 新しいプロンプトを作成する
   
   1. 設定メニューから「プロンプト設定」タブを選択
   2. 「+ 新規プロンプト」をクリック
   3. 以下の情報を入力:
      - プロンプトID: 英数字とアンダースコアのみ使用可能
      - プロンプト名: 表示名
      - 説明: プロンプトの説明
      - プロンプト内容: 実際のプロンプトテキスト
   4. パラメータの使用: `{{topic}}`などのパラメータを使用して動的な内容を指定可能
   5. 「保存」ボタンをクリック
   
   ### プロンプトの例
   
   ```
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
   
   ## 音声設定のカスタマイズ
   
   ### 話者の変更
   
   1. メイン画面またはキャラクター設定画面で、各キャラクターの「キャラクターボイス」ドロップダウンから話者を選択
   2. 選択は自動的に保存され、次回の漫才生成時に適用されます
   
   ### 利用可能な話者一覧
   
   VoiceVoxの音声モデルが自動的に一覧表示されます。以下のような話者が利用可能です：
   
   - 四国めたん（ノーマル）
   - ずんだもん（ノーマル）
   - 春日部つむぎ
   - 雨晴はう
   - 波音リツ
   - など
   
   ## システム設定のカスタマイズ
   
   ### 環境変数の設定
   
   Dockerを使用する場合は、`docker-compose.yml`ファイルを編集します：
   
   ```yaml
   services:
     web:
       environment:
         - FLASK_APP=backend/app/__init__.py
         - FLASK_ENV=development
         - VOICEVOX_URL=http://voicevox:50021
         - OLLAMA_URL=http://ollama:11434
         - OLLAMA_MODEL=phi  # 使用するモデルを変更できます
   ```
   
   直接起動する場合は、`.env`ファイルを作成または編集します：
   
   ```
   FLASK_APP=backend/app/__init__.py
   FLASK_ENV=development
   VOICEVOX_URL=http://localhost:50021
   OLLAMA_URL=http://localhost:11434
   OLLAMA_MODEL=phi
   ```
   
   ### 使用するLLMモデルの変更
   
   1. Ollamaで別のモデルをダウンロード:
      ```bash
      ollama pull mistral  # または他のモデル
      ```
   
   2. 環境変数を変更:
      ```
      OLLAMA_MODEL=mistral  # ダウンロードしたモデル名に変更
      ```
   
   3. アプリケーションを再起動
   EOF
   
   # トラブルシューティングガイド
   cat > docs/user_guide/troubleshooting.md << 'EOF'
   # トラブルシューティングガイド
   
   このガイドでは、ManzAI Studioの使用中に発生する可能性のある一般的な問題とその解決方法を説明します。
   
   ## 起動時の問題
   
   ### アプリケーションが起動しない
   
   1. **Docker Compose使用時**
      
      ```bash
      # ログを確認
      docker-compose logs
      
      # コンテナの状態を確認
      docker-compose ps
      ```
      
      - すべてのサービスが`Up`状態になっているか確認
      - `web`サービスがエラーで終了している場合、ログを確認
   
   2. **直接起動時**
      
      ```bash
      # デバッグモードで起動
      ./start_dev.sh
      ```
      
      - エラーメッセージを確認
      - Python環境が正しく設定されているか確認
   
   ### 「Ollamaサーバーに接続できません」エラー
   
   1. Ollamaが起動しているか確認:
      
      ```bash
      # ステータスをチェック
      curl http://localhost:11434/api/tags
      
      # サーバーを手動で起動
      ollama serve
      ```
   
   2. Ollamaのインストール状態を確認:
      
      ```bash
      # バージョン確認
      ollama --version
      
      # 再インストール
      curl -fsSL https://ollama.ai/install.sh | sh
      ```
   
   ### 「VoiceVoxサーバーに接続できません」エラー
   
   1. VoiceVoxが起動しているか確認:
      
      - VoiceVoxアプリケーションを手動で起動
      - Docker使用時は`docker-compose ps`でvoicevoxサービスの状態を確認
   
   2. ポートが利用可能か確認:
      
      ```bash
      # ポート50021が使用されているか確認
      netstat -tuln | grep 50021
      ```
   
   ## 漫才生成の問題
   
   ### 生成に失敗する
   
   1. **「台本の生成中にエラーが発生しました」エラー**
      
      - OllamaのLLMモデルがインストールされているか確認:
        ```bash
        ollama list
        ```
      
      - 必要なモデルがない場合はダウンロード:
        ```bash
        ollama pull phi
        ```
   
   2. **生成が途中で止まる**
      
      - システムリソースが不足している可能性があります
      - 実行中の他のアプリケーションを閉じてリソースを解放
      - Docker使用時はコンテナにより多くのリソースを割り当て
   
   ### 生成された漫才の質が低い
   
   1. **トピックの改善**
      
      - より具体的なトピックを使用してみる（例：「猫」→「猫の寝る場所の選び方」）
      - サンプルトピックから選択してみる
   
   2. **プロンプトのカスタマイズ**
      
      - 設定メニューからプロンプトを編集
      - より詳細な指示や例を追加
   
   3. **異なるLLMモデルを試す**
      
      - 環境変数でOLLAMA_MODELを変更
      - 他のモデル（mistral, llama2など）をダウンロードして試す
   
   ## 音声・アニメーションの問題
   
   ### 音声が再生されない
   
   1. **ブラウザの設定**
      
      - ブラウザの音声設定を確認
      - サイトの権限で音声再生が許可されているか確認
   
   2. **音声ファイルの確認**
      
      - 開発者ツールのNetworkタブでaudioファイルがロードされているか確認
      - サーバーのログでファイル生成エラーがないか確認
   
   ### キャラクターが表示されない
   
   1. **Live2Dモデルの確認**
      
      - モデルファイルが正しく配置されているか確認
      - 開発者ツールのConsoleタブでエラーメッセージを確認
   
   2. **WebGLの確認**
      
      - ブラウザがWebGLをサポートしているか確認:
        ```
        chrome://gpu/
        ```
      - 別のブラウザ（Chrome, Firefoxなど）を試す
   
   ### 口の動きと音声が同期していない
   
   1. **リソース不足**
      
      - システムリソースが不足している可能性があります
      - 実行中の他のアプリケーションを閉じてリソースを解放
      - より軽量なLive2Dモデルを使用する
   
   2. **ブラウザの問題**
      
      - ブラウザを再起動
      - 異なるブラウザを試す
   
   ## システムの問題
   
   ### アプリケーションが遅い
   
   1. **キャッシュのクリーンアップ**
      
      ```bash
      # 古い音声キャッシュを削除
      python scripts/cleanup_cache.py
      ```
   
   2. **リソースの確認**
      
      - アプリケーションのリソース使用状況を確認:
        ```
        http://localhost:5000/api/resources/stats
        ```
      - メモリやCPUが不足している場合は、他のアプリケーションを閉じるか、リソース制限を緩和
   
   ### ディスク容量の問題
   
   1. **音声ファイルのクリーンアップ**
      
      ```bash
      # 一時ファイルとキャッシュのクリーンアップ
      curl -X POST http://localhost:5000/api/resources/cleanup -H "Content-Type: application/json" -d '{"cleanup_temp": true, "cleanup_cache": true}'
      ```
   
   2. **Ollamaモデルの管理**
      
      - 使用していないモデルを削除:
        ```bash
        ollama rm [モデル名]
        ```
   
   ## バグの報告
   
   問題が解決しない場合は、以下の情報を含めてバグを報告してください：
   
   1. 使用している環境（OS、ブラウザ、Dockerの有無）
   2. 問題の再現手順
   3. エラーメッセージ（ある場合）
   4. ログ情報（ある場合）
   
   バグ報告は以下の方法で行えます：
   
   - GitHubのIssuesに登録
   - プロジェクトの連絡先にメール
   EOF
   ```

2. **READMEの更新**
   ```bash
   # READMEを更新
   cat > README.md << 'EOF'
   # ManzAI Studio
   
   ローカルで動作する漫才生成・実演Webアプリケーション
   
   ![ManzAI Studio Screenshot](docs/images/screenshot.png)
   
   ## 概要
   
   ManzAI Studioは、OllamaのLLMを使用して漫才の台本を生成し、Live2Dキャラクターとボイスボックスを使用してアニメーションと音声で実演する、完全ローカルで動作するWebアプリケーションです。
   
   ## 特徴
   
   - **完全ローカル動作**: インターネット接続なしで動作（初期設定後）
   - **LLMによる漫才生成**: Ollamaの軽量LLMで高品質な漫才台本を生成
   - **音声合成**: VoiceVoxによる自然な日本語音声合成
   - **キャラクターアニメーション**: Live2Dモデルによるリアルタイムアニメーション
   - **カスタマイズ**: キャラクターモデル、音声、プロンプトをカスタマイズ可能
   
   ## 必要要件
   
   ### システム要件
   - pyenv
   - Poetry
   - Node.js 18.0.0以上
   - 2GB以上の空き容量（モデルファイル用）
   
   ### 必須コンポーネント
   - [Ollama](https://ollama.ai/) - LLM実行環境
   - [VoiceVox](https://voicevox.hiroshiba.jp/) - 音声合成エンジン
   - Live2D Cubism SDK for Web
   
   ## クイックスタート
   
   ### Dockerを使用する場合（推奨）
   
   ```bash
   # リポジトリをクローン
   git clone https://github.com/yourusername/manzai-studio.git
   cd manzai-studio
   
   # Docker Composeで起動
   docker-compose up -d
   
   # ブラウザでアクセス
   # http://localhost:5000
   ```
   
   ### 直接インストールする場合
   
   ```bash
   # リポジトリをクローン
   git clone https://github.com/yourusername/manzai-studio.git
   cd manzai-studio
   
   # 必要なPythonバージョンをインストール
   pyenv install 3.10.13
   pyenv local 3.10.13
   
   # Poetryで依存関係をインストール
   poetry install
   
   # フロントエンドの依存関係をインストール
   cd frontend
   npm install
   cd ..
   
   # Ollamaをインストールしてモデルをダウンロード
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama pull phi
   
   # VoiceVoxをインストール（公式サイトからダウンロード）
   # https://voicevox.hiroshiba.jp/
   
   # 開発サーバーを起動
   ./start_dev.sh
   
   # ブラウザでアクセス
   # http://localhost:3000
   ```
   
   ## 詳細なドキュメント
   
   詳細な使用方法やカスタマイズについては、以下のドキュメントを参照してください：
   
   - [ユーザーガイド](docs/user_guide/README.md)
   - [開発者ガイド](docs/developer_guide.md)
   - [API仕様](docs/api_spec.md)
   
   ## ライセンス
   
   MIT License
   
   ## 貢献について
   
   プルリクエストは大歓迎です。大きな変更を加える場合は、まずissueを作成して変更内容を議論してください。
   EOF
   ```

### デプロイメントプロセスの整備

1. **Dockerfileの完成**
   ```bash
   # 本番用Dockerfileを作成
   cat > Dockerfile << 'EOF'
   FROM python:3.10-slim as builder
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       curl \
       build-essential \
       && rm -rf /var/lib/apt/lists/*
   
   # Install Poetry
   RUN curl -sSL https://install.python-poetry.org | python3 -
   ENV PATH="${PATH}:/root/.local/bin"
   
   # Copy poetry files
   COPY pyproject.toml poetry.lock ./
   
   # Configure poetry
   RUN poetry config virtualenvs.create false
   
   # Install only runtime dependencies
   RUN poetry install --no-dev --no-root
   
   # Node.js setup for frontend
   FROM node:18-slim as frontend
   
   WORKDIR /app
   
   COPY frontend/package.json frontend/package-lock.json ./
   
   RUN npm install
   
   COPY frontend/ ./
   
   RUN npm run build
   
   # Final stage
   FROM python:3.10-slim
   
   WORKDIR /app
   
   # Copy Python dependencies from builder stage
   COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
   COPY --from=builder /usr/local/bin /usr/local/bin
   
   # Copy frontend build
   COPY --from=frontend /app/build /app/frontend/build
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       curl \
       && rm -rf /var/lib/apt/lists/*
   
   # Copy application code
   COPY src/ /app/src/
   COPY scripts/ /app/scripts/
   COPY pyproject.toml poetry.lock ./
   
   # Create directories for data
   RUN mkdir -p /app/data/audio /app/data/cache /app/data/state
   
   # Environment variables
   ENV FLASK_APP=src/backend/app/__init__.py
   ENV FLASK_ENV=production
   ENV PYTHONPATH=/app
   
   # Expose port
   EXPOSE 5000
   
   # Run the application
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.backend.app:create_app()"]
   EOF
   ```

2. **docker-compose.ymlの更新**
   ```bash
   # docker-compose.ymlを本番環境用に更新
   cat > docker-compose.yml << 'EOF'
   version: '3.8'
   
   services:
     voicevox:
       image: voicevox/voicevox_engine:cpu-ubuntu20.04-latest
       ports:
         - "50021:50021"
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:50021/docs"]
         interval: 10s
         timeout: 10s
         retries: 3
   
     ollama:
       image: ollama/ollama:latest
       ports:
         - "11434:11434"
       volumes:
         - ollama_data:/root/.ollama
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
         interval: 10s
         timeout: 10s
         retries: 3
   
     web:
       build:
         context: .
       ports:
         - "5000:5000"
       environment:
         - FLASK_APP=src/backend/app/__init__.py
         - FLASK_ENV=production
         - VOICEVOX_URL=http://voicevox:50021
         - OLLAMA_URL=http://ollama:11434
         - OLLAMA_MODEL=phi
       volumes:
         - app_data:/app/data
       restart: unless-stopped
       depends_on:
         voicevox:
           condition: service_healthy
         ollama:
           condition: service_healthy
   
   volumes:
   # 前略...
   EOF
   ```

3. **docker-compose.dev.yml の作成**
   ```bash
   # 開発環境用のdocker-compose.dev.ymlを作成
   cat > docker-compose.dev.yml << 'EOF'
   version: '3.8'
   
   services:
     voicevox:
       image: voicevox/voicevox_engine:cpu-ubuntu20.04-latest
       ports:
         - "50021:50021"
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:50021/docs"]
         interval: 5s
         timeout: 10s
         retries: 5
   
     ollama:
       image: ollama/ollama:latest
       ports:
         - "11434:11434"
       volumes:
         - ollama_data:/root/.ollama
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
         interval: 5s
         timeout: 10s
         retries: 5
   
     web:
       build:
         context: .
         dockerfile: Dockerfile.dev
       volumes:
         - .:/app
         - poetry_cache:/root/.cache/pypoetry
       ports:
         - "5000:5000"
       environment:
         - FLASK_APP=src/backend/app/__init__.py
         - FLASK_ENV=development
         - VOICEVOX_URL=http://voicevox:50021
         - OLLAMA_URL=http://ollama:11434
         - OLLAMA_MODEL=phi
       depends_on:
         voicevox:
           condition: service_healthy
         ollama:
           condition: service_healthy
   
   volumes:
     ollama_data:
     poetry_cache:
   EOF
   ```

4. **デプロイスクリプトの作成**
   ```bash
   # デプロイスクリプトを作成
   mkdir -p scripts
   cat > scripts/deploy.sh << 'EOF'
   #!/bin/bash
   
   # ManzAI Studio デプロイスクリプト
   
   set -e
   
   # 色の定義
   GREEN='\033[0;32m'
   BLUE='\033[0;34m'
   RED='\033[0;31m'
   NC='\033[0m' # No Color
   
   # 使用法
   usage() {
     echo "使用法: $0 [オプション]"
     echo ""
     echo "オプション:"
     echo "  -e, --env ENV     デプロイ環境 (production, development)"
     echo "  -r, --rebuild     イメージを再ビルド"
     echo "  -h, --help        このヘルプを表示"
     echo ""
     exit 1
   }
   
   # 引数の解析
   ENVIRONMENT="production"
   REBUILD=false
   
   while [[ $# -gt 0 ]]; do
     case $1 in
       -e|--env)
         ENVIRONMENT="$2"
         shift 2
         ;;
       -r|--rebuild)
         REBUILD=true
         shift
         ;;
       -h|--help)
         usage
         ;;
       *)
         echo "不明なオプション: $1"
         usage
         ;;
     esac
   done
   
   # 環境に基づいてdocker-composeファイルを選択
   if [ "$ENVIRONMENT" == "production" ]; then
     COMPOSE_FILE="docker-compose.yml"
   elif [ "$ENVIRONMENT" == "development" ]; then
     COMPOSE_FILE="docker-compose.dev.yml"
   else
     echo -e "${RED}不正な環境: $ENVIRONMENT${NC}"
     usage
   fi
   
   echo -e "${BLUE}ManzAI Studioを${ENVIRONMENT}環境にデプロイします...${NC}"
   
   # 必要なファイルを確認
   if [ ! -f "$COMPOSE_FILE" ]; then
     echo -e "${RED}エラー: ${COMPOSE_FILE}が見つかりません${NC}"
     exit 1
   fi
   
   # Ollamaが起動していることを確認
   echo -e "${BLUE}Ollamaの状態を確認しています...${NC}"
   if curl -s http://localhost:11434/api/tags > /dev/null; then
     echo -e "${GREEN}Ollamaは起動しています${NC}"
   else
     echo -e "${BLUE}Ollamaを起動します...${NC}"
   fi
   
   # VoiceVoxが起動していることを確認
   echo -e "${BLUE}VoiceVoxの状態を確認しています...${NC}"
   if curl -s http://localhost:50021/version > /dev/null; then
     echo -e "${GREEN}VoiceVoxは起動しています${NC}"
   else
     echo -e "${BLUE}VoiceVoxを起動します...${NC}"
   fi
   
   # 必要なモデルがインストールされているか確認
   if grep -q "OLLAMA_MODEL" "$COMPOSE_FILE"; then
     MODEL=$(grep -o "OLLAMA_MODEL=[a-zA-Z0-9]*" "$COMPOSE_FILE" | cut -d'=' -f2)
     echo -e "${BLUE}必要なモデル '$MODEL' を確認しています...${NC}"
     
     if curl -s http://localhost:11434/api/tags | grep -q "$MODEL"; then
       echo -e "${GREEN}モデル '$MODEL' はインストール済みです${NC}"
     else
       echo -e "${BLUE}モデル '$MODEL' をインストールします...${NC}"
       docker-compose exec -T ollama ollama pull "$MODEL"
     fi
   fi
   
   # イメージの再ビルド
   if [ "$REBUILD" = true ]; then
     echo -e "${BLUE}イメージを再ビルドしています...${NC}"
     docker-compose -f "$COMPOSE_FILE" build
   fi
   
   # デプロイの実行
   echo -e "${BLUE}コンテナを起動しています...${NC}"
   docker-compose -f "$COMPOSE_FILE" up -d
   
   # 状態確認
   echo -e "${BLUE}コンテナの状態:${NC}"
   docker-compose -f "$COMPOSE_FILE" ps
   
   echo -e "${GREEN}デプロイが完了しました！${NC}"
   echo -e "${BLUE}アプリケーションには http://localhost:5000 でアクセスできます${NC}"
   
   exit 0
   EOF
   
   chmod +x scripts/deploy.sh
   ```

5. **CI/CD設定ファイルの作成**
   ```bash
   # GitHub Actionsのワークフローファイルを作成
   mkdir -p .github/workflows
   cat > .github/workflows/build_test.yml << 'EOF'
   name: Build and Test
   
   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]
   
   jobs:
     build_and_test:
       runs-on: ubuntu-latest
   
       steps:
       - uses: actions/checkout@v3
   
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.10'
   
       - name: Install Poetry
         run: |
           curl -sSL https://install.python-poetry.org | python3 -
   
       - name: Install dependencies
         run: |
           poetry install
   
       - name: Lint with flake8
         run: |
           poetry run flake8 src
   
       - name: Check types with mypy
         run: |
           poetry run mypy src
   
       - name: Test with pytest
         run: |
           poetry run pytest
   
       - name: Build Docker image
         run: |
           docker build -t manzai-studio:test .
   
     frontend:
       runs-on: ubuntu-latest
   
       steps:
       - uses: actions/checkout@v3
   
       - name: Set up Node.js
         uses: actions/setup-node@v3
         with:
           node-version: '18'
   
       - name: Install dependencies
         run: |
           cd frontend
           npm install
   
       - name: Run ESLint
         run: |
           cd frontend
           npm run lint
   
       - name: Build frontend
         run: |
           cd frontend
           npm run build
   EOF
   ```

### ライセンスとドキュメント

1. **ライセンスファイルの追加**
   ```bash
   # MITライセンスファイルを作成
   cat > LICENSE << 'EOF'
   MIT License
   
   Copyright (c) 2025
   
   Permission is hereby granted, free of charge, to any person obtaining a copy
   of this software and associated documentation files (the "Software"), to deal
   in the Software without restriction, including without limitation the rights
   to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
   copies of the Software, and to permit persons to whom the Software is
   furnished to do so, subject to the following conditions:
   
   The above copyright notice and this permission notice shall be included in all
   copies or substantial portions of the Software.
   
   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
   SOFTWARE.
   EOF
   ```

2. **APIドキュメントの作成**
   ```bash
   # API仕様ドキュメントを作成
   cat > docs/api_spec.md << 'EOF'
   # ManzAI Studio API仕様
   
   このドキュメントでは、ManzAI StudioのREST APIについて説明します。
   
   ## ベースURL
   
   ```
   http://localhost:5000/api
   ```
   
   ## 認証
   
   現在、認証は実装されていません。APIはローカルでのみ利用可能です。
   
   ## レスポンスフォーマット
   
   すべてのレスポンスはJSON形式で返されます。成功した場合は要求されたデータが、失敗した場合はエラーメッセージが含まれます。
   
   エラーレスポンスの例:
   
   ```json
   {
     "error": "エラーメッセージ"
   }
   ```
   
   ## エンドポイント
   
   ### ヘルスチェック
   
   ```
   GET /health
   ```
   
   アプリケーションの状態を確認します。
   
   レスポンス例:
   
   ```json
   {
     "status": "healthy"
   }
   ```
   
   ### 漫才生成
   
   ```
   POST /generate
   ```
   
   トピックに基づいて漫才台本を生成します。
   
   **リクエスト本文**:
   
   ```json
   {
     "topic": "スマートフォン",
     "temperature": 0.7
   }
   ```
   
   **パラメータ**:
   
   - `topic` (必須): 漫才のトピック
   - `temperature` (任意): 生成のランダム性（デフォルト: 0.7）
   
   **レスポンス例**:
   
   ```json
   {
     "topic": "スマートフォン",
     "script": [
       {
         "speaker": "tsukkomi",
         "text": "今日はスマートフォンについて話しましょうか！"
       },
       {
         "speaker": "boke",
         "text": "あぁ、あの賢い電話ってやつですね！"
       }
     ]
   }
   ```
   
   ### 音声合成
   
   ```
   POST /synthesize
   ```
   
   テキストから音声を合成します。
   
   **リクエスト本文**:
   
   ```json
   {
     "text": "こんにちは、世界！",
     "speaker_id": 1
   }
   ```
   
   **パラメータ**:
   
   - `text` (必須): 合成するテキスト
   - `speaker_id` (任意): 話者ID（デフォルト: 1）
   
   **レスポンス例**:
   
   ```json
   {
     "audio_url": "http://localhost:5000/audio/1234567890_1.wav",
     "timing_data": {
       "accent_phrases": [...]
     }
   }
   ```
   
   ### 台本音声合成
   
   ```
   POST /synthesize_script
   ```
   
   漫才台本の音声を合成します。
   
   **リクエスト本文**:
   
   ```json
   {
     "script": [
       {
         "speaker": "tsukkomi",
         "text": "今日はスマートフォンについて話しましょうか！"
       },
       {
         "speaker": "boke",
         "text": "あぁ、あの賢い電話ってやつですね！"
       }
     ],
     "tsukkomi_id": 1,
     "boke_id": 3
   }
   ```
   
   **パラメータ**:
   
   - `script` (必須): 漫才台本
   - `tsukkomi_id` (任意): ツッコミ役の話者ID（デフォルト: 1）
   - `boke_id` (任意): ボケ役の話者ID（デフォルト: 3）
   
   **レスポンス例**:
   
   ```json
   {
     "results": [
       {
         "speaker": "tsukkomi",
         "text": "今日はスマートフォンについて話しましょうか！",
         "audio_url": "http://localhost:5000/audio/1234567890_1.wav",
         "timing_data": {
           "accent_phrases": [...]
         }
       },
       {
         "speaker": "boke",
         "text": "あぁ、あの賢い電話ってやつですね！",
         "audio_url": "http://localhost:5000/audio/1234567891_3.wav",
         "timing_data": {
           "accent_phrases": [...]
         }
       }
     ]
   }
   ```
   
   ### 話者一覧
   
   ```
   GET /speakers
   ```
   
   利用可能な話者一覧を取得します。
   
   **レスポンス例**:
   
   ```json
   {
     "speakers": [
       {
         "id": 1,
         "name": "四国めたん (ノーマル)"
       },
       {
         "id": 3,
         "name": "ずんだもん (ノーマル)"
       }
     ]
   }
   ```
   
   ### Live2Dモデル一覧
   
   ```
   GET /models/live2d
   ```
   
   利用可能なLive2Dモデル一覧を取得します。
   
   **レスポンス例**:
   
   ```json
   {
     "models": [
       {
         "id": "character1",
         "name": "キャラクター1",
         "path": "/live2d/models/character1/model.json",
         "type": "tsukkomi",
         "thumbnail": "/live2d/models/character1/thumbnail.png"
       },
       {
         "id": "character2",
         "name": "キャラクター2",
         "path": "/live2d/models/character2/model.json",
         "type": "boke",
         "thumbnail": "/live2d/models/character2/thumbnail.png"
       }
     ]
   }
   ```
   
   ### プロンプト一覧
   
   ```
   GET /prompts
   ```
   
   利用可能なプロンプト一覧を取得します。
   
   **レスポンス例**:
   
   ```json
   {
     "prompts": [
       {
         "id": "manzai_prompt",
         "name": "漫才プロンプト",
         "description": "標準の漫才プロンプト",
         "content": "あなたは熟練した漫才作家です...",
         "parameters": ["topic"],
         "isDefault": true
       }
     ]
   }
   ```
   
   ### プロンプト詳細
   
   ```
   GET /prompts/{prompt_id}
   ```
   
   特定のプロンプト詳細を取得します。
   
   **レスポンス例**:
   
   ```json
   {
     "id": "manzai_prompt",
     "name": "漫才プロンプト",
     "description": "標準の漫才プロンプト",
     "content": "あなたは熟練した漫才作家です...",
     "parameters": ["topic"],
     "isDefault": true
   }
   ```
   
   ### プロンプト作成
   
   ```
   POST /prompts
   ```
   
   新しいプロンプトを作成します。
   
   **リクエスト本文**:
   
   ```json
   {
     "id": "custom_prompt",
     "name": "カスタムプロンプト",
     "description": "ユーザー定義プロンプト",
     "content": "あなたはユーモアのセンスがある漫才作家です...",
     "parameters": ["topic"]
   }
   ```
   
   **レスポンス例**:
   
   ```json
   {
     "success": true,
     "message": "プロンプト custom_prompt が作成されました",
     "prompt": {
       "id": "custom_prompt",
       "name": "カスタムプロンプト",
       "description": "ユーザー定義プロンプト",
       "content": "あなたはユーモアのセンスがある漫才作家です...",
       "parameters": ["topic"],
       "isDefault": false
     }
   }
   ```
   
   ### リソース統計
   
   ```
   GET /resources/stats
   ```
   
   システムリソースの統計情報を取得します。
   
   **レスポンス例**:
   
   ```json
   {
     "cpu_percent": 35.2,
     "memory_percent": 48.7,
     "disk_percent": 62.1,
     "memory_available_mb": 3584.5
   }
   ```
   
   ### リソースクリーンアップ
   
   ```
   POST /resources/cleanup
   ```
   
   一時ファイルとキャッシュをクリーンアップします。
   
   **リクエスト本文**:
   
   ```json
   {
     "cleanup_temp": true,
     "cleanup_cache": true,
     "cache_age_days": 30
   }
   ```
   
   **レスポンス例**:
   
   ```json
   {
     "success": true,
     "results": {
       "temp_files_removed": 15,
       "cache_files_removed": 42
     }
   }
   ```
   
   ### 保存済み台本一覧
   
   ```
   GET /recovery/scripts
   ```
   
   保存された台本一覧を取得します。
   
   **レスポンス例**:
   
   ```json
   {
     "scripts": [
       {
         "id": 1679395200,
         "topic": "スマートフォン",
         "script": [...],
         "timestamp": 1679395200
       }
     ]
   }
   ```
   
   ### 保存済み台本詳細
   
   ```
   GET /recovery/scripts/{script_id}
   ```
   
   特定の保存済み台本詳細を取得します。
   
   **レスポンス例**:
   
   ```json
   {
     "id": 1679395200,
     "topic": "スマートフォン",
     "script": [
       {
         "speaker": "tsukkomi",
         "text": "今日はスマートフォンについて話しましょうか！"
       },
       {
         "speaker": "boke",
         "text": "あぁ、あの賢い電話ってやつですね！"
       }
     ],
     "timestamp": 1679395200
   }
   ```
   EOF
   ```

この開発ステップでは、テスト、ドキュメント、デプロイメントプロセスを整備しました。具体的には以下の内容を実装しました：

1. **テスト拡充**: バックエンドとフロントエンドのユニットテストとE2Eテストを拡充し、コードの品質を確保しました。
2. **ユーザードキュメント**: インストール方法、使用方法、カスタマイズ、トラブルシューティングなどを含む包括的なユーザードキュメントを作成しました。
3. **デプロイメントプロセス**: 本番環境と開発環境に対応したDockerfile、docker-compose設定、デプロイスクリプトを整備しました。
4. **CI/CD設定**: GitHub Actionsを使用した継続的インテグレーション・デプロイメントのワークフローを設定しました。
5. **ライセンスとAPI仕様**: MITライセンスの追加とAPIエンドポイントの詳細な仕様書を作成しました。

これらの整備により、アプリケーションのデプロイが容易になり、ユーザーがシステムを理解・使用・カスタマイズするための十分な情報が提供されるようになりました。次のステップでは、これまでの実装の最終確認と改善を行います。