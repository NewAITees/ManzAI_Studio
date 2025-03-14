# ManzAI Studio 開発工程書

## 開発ステップ3: VoiceVox連携による音声合成機能の実装

### VoiceVoxサービスの実装

1. **VoiceVoxサービスクラスの作成**
   ```bash
   touch src/backend/app/services/voicevox_service.py
   ```

   ```python
   # src/backend/app/services/voicevox_service.py
   import os
   import subprocess
   import time
   import requests
   import json
   from typing import Dict, Any, List, Optional, Tuple
   from flask import current_app

   class VoiceVoxService:
       """Service for interacting with VoiceVox API."""
       
       def __init__(self, base_url: Optional[str] = None):
           """Initialize VoiceVoxService.
           
           Args:
               base_url: VoiceVox API base URL. Defaults to app config.
           """
           self.base_url = base_url or current_app.config["VOICEVOX_URL"]
           self.process = None
           
       def is_server_running(self) -> bool:
           """Check if VoiceVox server is running.
           
           Returns:
               True if server is running, False otherwise.
           """
           try:
               response = requests.get(f"{self.base_url}/version", timeout=2)
               return response.status_code == 200
           except requests.RequestException:
               return False
               
       def start_server_if_needed(self) -> None:
           """Start VoiceVox server if not already running.
           
           Raises:
               RuntimeError: If server fails to start.
           """
           if self.is_server_running():
               return
               
           # Dockerの場合は不要だが、ローカル実行時のための処理
           try:
               # VoiceVoxバイナリを起動
               self.process = subprocess.Popen(
                   ["voicevox", "--port", "50021", "--device", "cpu"], 
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE
               )
               
               # サーバー起動を待機
               for _ in range(30):  # 30秒タイムアウト
                   if self.is_server_running():
                       return
                   time.sleep(1)
                   
               raise RuntimeError("VoiceVox server failed to start in time")
           except Exception as e:
               raise RuntimeError(f"Failed to start VoiceVox server: {str(e)}")
               
       def get_speakers(self) -> List[Dict[str, Any]]:
           """Get list of available speakers.
           
           Returns:
               List of speaker information.
               
           Raises:
               RuntimeError: If API request fails.
           """
           try:
               response = requests.get(f"{self.base_url}/speakers")
               response.raise_for_status()
               return response.json()
           except requests.RequestException as e:
               raise RuntimeError(f"Failed to get speakers: {str(e)}")
               
       def synthesize_voice(
           self, 
           text: str, 
           speaker_id: int = 1, 
           output_dir: str = "static/audio"
       ) -> Tuple[str, Dict[str, Any]]:
           """Synthesize voice from text.
           
           Args:
               text: Text to synthesize.
               speaker_id: ID of speaker to use.
               output_dir: Directory to save audio file.
               
           Returns:
               Tuple of (audio file path, accent phrases data).
               
           Raises:
               RuntimeError: If API request fails.
           """
           self.start_server_if_needed()
           
           try:
               # アクセント句データ取得（リップシンク用）
               accent_response = requests.post(
                   f"{self.base_url}/audio_query?text={text}&speaker={speaker_id}"
               )
               accent_response.raise_for_status()
               accent_data = accent_response.json()
               
               # 音声合成
               synthesis_response = requests.post(
                   f"{self.base_url}/synthesis?speaker={speaker_id}",
                   json=accent_data
               )
               synthesis_response.raise_for_status()
               
               # 音声ファイル保存
               os.makedirs(output_dir, exist_ok=True)
               filename = f"{int(time.time())}_{speaker_id}.wav"
               file_path = os.path.join(output_dir, filename)
               
               with open(file_path, "wb") as f:
                   f.write(synthesis_response.content)
                   
               return file_path, accent_data
               
       def stop_server(self) -> None:
           """Stop VoiceVox server if it was started by this service."""
           if self.process:
               self.process.terminate()
               self.process = None
   ```

2. **コンテキストマネージャーの追加（サーバー管理用）**
   ```python
   # src/backend/app/services/voicevox_service.py に追加
   class VoiceVoxServerManager:
       """Context manager for VoiceVox server."""
       
       def __init__(self, base_url: Optional[str] = None):
           """Initialize VoiceVoxServerManager.
           
           Args:
               base_url: VoiceVox API base URL.
           """
           self.service = VoiceVoxService(base_url)
           
       def __enter__(self):
           """Start server if needed when entering context."""
           self.service.start_server_if_needed()
           return self.service
           
       def __exit__(self, exc_type, exc_val, exc_tb):
           """Stop server when exiting context."""
           self.service.stop_server()
   ```

### 静的ファイル配信の設定

1. **静的ディレクトリの作成**
   ```bash
   mkdir -p src/backend/app/static/audio
   ```

2. **Flaskアプリに静的ファイル配信を設定**
   ```python
   # src/backend/app/__init__.py を更新
   from flask import Flask, send_from_directory
   from flask_cors import CORS
   import os

   from backend.app.config import Config, DevelopmentConfig

   def create_app(config_object: Config = DevelopmentConfig) -> Flask:
       """Create and configure the Flask application."""
       app = Flask(__name__)
       app.config.from_object(config_object)
       CORS(app)

       # Register blueprints
       from backend.app.routes import api
       app.register_blueprint(api.bp)
       
       # Static files route
       @app.route('/audio/<path:filename>')
       def serve_audio(filename):
           return send_from_directory(
               os.path.join(app.root_path, 'static/audio'), 
               filename
           )

       return app
   ```

### 音声合成APIエンドポイントの実装

1. **APIルートの追加**
   ```python
   # src/backend/app/routes/api.py に追加
   import os
   from backend.app.services.voicevox_service import VoiceVoxService

   @bp.route("/synthesize", methods=["POST"])
   def synthesize_voice() -> Dict[str, Any]:
       """Synthesize voice from text using VoiceVox.
       
       Returns:
           Dict containing audio file path and timing data.
       """
       data = request.get_json()
       if not data or "text" not in data:
           return jsonify({"error": "No text provided"}), 400
           
       text = data["text"]
       speaker_id = data.get("speaker_id", 1)  # デフォルトはずんだもん
       
       try:
           voicevox_service = VoiceVoxService()
           file_path, accent_data = voicevox_service.synthesize_voice(
               text=text,
               speaker_id=speaker_id
           )
           
           # クライアントに返すURLを構築
           filename = os.path.basename(file_path)
           audio_url = request.host_url.rstrip('/') + f"/audio/{filename}"
           
           return jsonify({
               "audio_url": audio_url,
               "timing_data": accent_data
           })
       except Exception as e:
           current_app.logger.error(f"Error synthesizing voice: {str(e)}")
           return jsonify({"error": str(e)}), 500
   ```

2. **複数台詞の一括音声合成APIの追加**
   ```python
   # src/backend/app/routes/api.py に追加
   @bp.route("/synthesize_script", methods=["POST"])
   def synthesize_script() -> Dict[str, Any]:
       """Synthesize voice for a manzai script.
       
       Returns:
           Dict containing audio files and timing data for each line.
       """
       data = request.get_json()
       if not data or "script" not in data:
           return jsonify({"error": "No script provided"}), 400
           
       script = data["script"]
       tsukkomi_id = data.get("tsukkomi_id", 1)  # ツッコミ役の声
       boke_id = data.get("boke_id", 3)         # ボケ役の声
       
       try:
           voicevox_service = VoiceVoxService()
           results = []
           
           for line in script:
               speaker = line.get("speaker", "tsukkomi")
               text = line.get("text", "")
               
               if not text:
                   continue
                   
               # 話者IDを選択
               speaker_id = tsukkomi_id if speaker == "tsukkomi" else boke_id
               
               # 音声合成
               file_path, accent_data = voicevox_service.synthesize_voice(
                   text=text,
                   speaker_id=speaker_id
               )
               
               # URL構築
               filename = os.path.basename(file_path)
               audio_url = request.host_url.rstrip('/') + f"/audio/{filename}"
               
               results.append({
                   "speaker": speaker,
                   "text": text,
                   "audio_url": audio_url,
                   "timing_data": accent_data
               })
               
           return jsonify({
               "results": results
           })
       except Exception as e:
           current_app.logger.error(f"Error synthesizing script: {str(e)}")
           return jsonify({"error": str(e)}), 500
   ```

### 利用可能な話者一覧APIの実装

1. **話者一覧APIエンドポイントの追加**
   ```python
   # src/backend/app/routes/api.py に追加
   @bp.route("/speakers", methods=["GET"])
   def get_speakers() -> Dict[str, Any]:
       """Get list of available VoiceVox speakers.
       
       Returns:
           Dict containing list of speakers.
       """
       try:
           voicevox_service = VoiceVoxService()
           speakers = voicevox_service.get_speakers()
           
           # 簡略化したリストを返す
           simplified = []
           for speaker_info in speakers:
               for style in speaker_info.get("styles", []):
                   simplified.append({
                       "id": style.get("id"),
                       "name": f"{speaker_info.get('name')} ({style.get('name')})"
                   })
                   
           return jsonify({
               "speakers": simplified
           })
       except Exception as e:
           current_app.logger.error(f"Error getting speakers: {str(e)}")
           return jsonify({"error": str(e)}), 500
   ```

### 単体テストの実装

1. **VoiceVoxサービスのモックテスト**
   ```bash
   touch src/backend/tests/test_voicevox_service.py
   ```

   ```python
   # src/backend/tests/test_voicevox_service.py
   import pytest
   from unittest.mock import patch, MagicMock
   import os
   from backend.app.services.voicevox_service import VoiceVoxService

   @patch("backend.app.services.voicevox_service.requests.get")
   def test_is_server_running_true(mock_get):
       # サーバー起動中の状態をモック
       mock_response = MagicMock()
       mock_response.status_code = 200
       mock_get.return_value = mock_response
       
       # サービスをテスト
       service = VoiceVoxService(base_url="http://test")
       result = service.is_server_running()
       
       # 期待される結果を検証
       assert result is True
       mock_get.assert_called_once_with("http://test/version", timeout=2)
       
   @patch("backend.app.services.voicevox_service.requests.get")
   def test_is_server_running_false(mock_get):
       # 接続エラーをモック
       mock_get.side_effect = Exception("Connection error")
       
       # サービスをテスト
       service = VoiceVoxService(base_url="http://test")
       result = service.is_server_running()
       
       # 期待される結果を検証
       assert result is False
       
   @patch("backend.app.services.voicevox_service.requests.post")
   @patch("backend.app.services.voicevox_service.requests.get")
   @patch("backend.app.services.voicevox_service.os.makedirs")
   @patch("builtins.open", new_callable=MagicMock)
   def test_synthesize_voice(mock_open, mock_makedirs, mock_get, mock_post):
       # サーバー起動中の状態をモック
       server_response = MagicMock()
       server_response.status_code = 200
       mock_get.return_value = server_response
       
       # アクセント句応答をモック
       accent_response = MagicMock()
       accent_response.status_code = 200
       accent_response.json.return_value = {"accent_phrases": []}
       
       # 音声合成応答をモック
       synthesis_response = MagicMock()
       synthesis_response.status_code = 200
       synthesis_response.content = b"audio_data"
       
       # requestsのpostメソッドの応答を設定
       mock_post.side_effect = [accent_response, synthesis_response]
       
       # サービスをテスト
       service = VoiceVoxService(base_url="http://test")
       file_path, accent_data = service.synthesize_voice("こんにちは", 1)
       
       # 期待される結果を検証
       assert accent_data == {"accent_phrases": []}
       assert os.path.basename(file_path).endswith("_1.wav")
       mock_makedirs.assert_called_once()
       mock_open.assert_called_once()
   ```

2. **APIエンドポイントのテスト追加**
   ```python
   # src/backend/tests/test_api.py に追加
   @patch("backend.app.routes.api.VoiceVoxService")
   def test_synthesize_voice_success(mock_voicevox_service, client: FlaskClient) -> None:
       # VoiceVoxServiceをモック
       mock_instance = mock_voicevox_service.return_value
       mock_instance.synthesize_voice.return_value = (
           "static/audio/12345_1.wav",
           {"accent_phrases": []}
       )
       
       # APIを呼び出し
       response = client.post("/api/synthesize", json={"text": "こんにちは"})
       
       # 期待される結果を検証
       assert response.status_code == 200
       assert "audio_url" in response.json
       assert "timing_data" in response.json
   ```

### 実装のテストと検証

1. **音声合成テスト用スクリプト**
   ```bash
   touch scripts/test_voice_synthesis.py
   ```

   ```python
   # scripts/test_voice_synthesis.py
   import requests
   import json
   import os
   import time
   from pydub import AudioSegment
   from pydub.playback import play

   def main():
       base_url = "http://localhost:5000/api"
       
       # 話者一覧を取得
       print("Fetching speakers...")
       speakers_response = requests.get(f"{base_url}/speakers")
       
       if speakers_response.status_code == 200:
           speakers = speakers_response.json().get("speakers", [])
           print(f"Available speakers: {len(speakers)}")
           for i, speaker in enumerate(speakers[:5]):  # 最初の5人だけ表示
               print(f"  {speaker['id']}: {speaker['name']}")
       else:
           print(f"Error fetching speakers: {speakers_response.text}")
           return
           
       # 音声合成テスト
       print("\nSynthesizing voice...")
       text = "こんにちは、VoiceVoxのテストです。"
       synthesis_response = requests.post(
           f"{base_url}/synthesize",
           json={"text": text, "speaker_id": 1}
       )
       
       if synthesis_response.status_code == 200:
           result = synthesis_response.json()
           audio_url = result["audio_url"]
           timing_data = result["timing_data"]
           
           print(f"Audio URL: {audio_url}")
           print(f"Accent phrases: {len(timing_data.get('accent_phrases', []))}")
           
           # 音声ファイルをダウンロード
           audio_response = requests.get(audio_url)
           if audio_response.status_code == 200:
               # 一時ファイルに保存
               temp_file = "temp_audio.wav"
               with open(temp_file, "wb") as f:
                   f.write(audio_response.content)
                   
               # 音声を再生
               print("Playing audio...")
               try:
                   audio = AudioSegment.from_file(temp_file)
                   play(audio)
               except Exception as e:
                   print(f"Error playing audio: {str(e)}")
               finally:
                   # 一時ファイルを削除
                   try:
                       os.remove(temp_file)
                   except:
                       pass
           else:
               print(f"Error downloading audio: {audio_response.status_code}")
       else:
           print(f"Error synthesizing voice: {synthesis_response.text}")

   if __name__ == "__main__":
       main()
   ```

2. **テスト実行**
   ```bash
   # 必要なライブラリをインストール（音声再生用）
   poetry add pydub
   
   # テスト用に、必要に応じて以下もインストール
   # macOS: brew install portaudio
   # Ubuntu: sudo apt-get install python3-pyaudio
   poetry add pyaudio
   
   # バックエンドサーバーを起動
   poetry run python -m flask --app backend/app/__init__.py run --debug
   
   # 別のターミナルでテスト実行
   poetry run python scripts/test_voice_synthesis.py
   ```

3. **漫才全体の音声合成テスト**
   ```bash
   touch scripts/test_full_manzai.py
   ```

   ```python
   # scripts/test_full_manzai.py
   import requests
   import json
   import time

   def main():
       base_url = "http://localhost:5000/api"
       
       # 1. 漫才台本生成
       print("Generating manzai script...")
       topic = "スマートフォン"
       script_response = requests.post(
           f"{base_url}/generate",
           json={"topic": topic}
       )
       
       if script_response.status_code != 200:
           print(f"Error generating script: {script_response.text}")
           return
           
       script_data = script_response.json()
       script = script_data["script"]
       
       print(f"Generated {len(script)} lines of dialogue about '{topic}'")
       
       # 2. 音声合成
       print("\nSynthesizing voices for the script...")
       synthesis_response = requests.post(
           f"{base_url}/synthesize_script",
           json={
               "script": script,
               "tsukkomi_id": 1,  # ずんだもん
               "boke_id": 3       # 四国めたん
           }
       )
       
       if synthesis_response.status_code != 200:
           print(f"Error synthesizing script: {synthesis_response.text}")
           return
           
       results = synthesis_response.json().get("results", [])
       
       print(f"Successfully synthesized {len(results)} lines of dialogue")
       print("\nManzai Script with Audio URLs:")
       
       for i, line in enumerate(results):
           speaker = "A" if line["speaker"] == "tsukkomi" else "B"
           print(f"{speaker}: {line['text']}")
           print(f"   Audio: {line['audio_url']}")
           
       print("\nTest completed successfully!")

   if __name__ == "__main__":
       main()
   ```

   ```bash
   # テスト実行
   poetry run python scripts/test_full_manzai.py
   ```

この開発ステップでは、VoiceVoxと連携して漫才の音声合成を行う機能を実装しました。単体の台詞と漫才台本全体の音声合成に対応するAPIエンドポイントを実装し、リップシンク用のタイミングデータも取得できるようになりました。次のステップでは、Live2Dキャラクターの表示と口の動きを音声と同期させる機能を実装します。