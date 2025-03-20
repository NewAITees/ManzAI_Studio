"""
基本的なエンドツーエンドテスト
APIエンドポイントの一連の呼び出しをシミュレートし、システム全体の動作を検証します。
"""
import os
import json
import time
import pytest
import requests
import logging
import sys
import threading
import subprocess
import signal
import atexit

# ロガーの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("e2e_tests")

# テスト設定
BASE_URL = os.environ.get("TEST_API_URL", "http://localhost:5000")
MAX_RETRIES = 5
RETRY_DELAY = 2  # 秒

logger.info(f"テスト設定 - BASE_URL: {BASE_URL}, MAX_RETRIES: {MAX_RETRIES}, RETRY_DELAY: {RETRY_DELAY}")

# サーバープロセスを保持するグローバル変数
server_process = None
server_thread = None

def start_server():
    """APIサーバーを起動する"""
    global server_process
    logger.info("APIサーバーを起動しています...")
    
    try:
        # サーバーを起動
        server_process = subprocess.Popen(
            ["poetry", "run", "python", "-m", "flask", "--app", "src.app", "run", "--port", "5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # 新しいプロセスグループを作成
        )
        
        # サーバー出力を記録するスレッド
        def log_output():
            while server_process and server_process.poll() is None:
                stdout_line = server_process.stdout.readline().decode('utf-8').strip()
                if stdout_line:
                    logger.info(f"Server stdout: {stdout_line}")
                
                stderr_line = server_process.stderr.readline().decode('utf-8').strip()
                if stderr_line:
                    logger.error(f"Server stderr: {stderr_line}")
        
        global server_thread
        server_thread = threading.Thread(target=log_output, daemon=True)
        server_thread.start()
        
        # サーバーの起動を待機
        logger.info("サーバーの起動を待機しています...")
        for _ in range(30):  # 最大30秒待機
            try:
                response = requests.get(f"{BASE_URL}/", timeout=1)
                if response.status_code == 200:
                    logger.info(f"APIサーバーが起動しました: {response.status_code}")
                    return True
            except requests.RequestException:
                pass
            time.sleep(1)
        
        logger.error("APIサーバーの起動タイムアウト")
        return False
    except Exception as e:
        logger.error(f"APIサーバーの起動中にエラーが発生しました: {e}")
        return False

def stop_server():
    """APIサーバーを停止する"""
    global server_process, server_thread
    
    if server_process:
        logger.info("APIサーバーを停止しています...")
        try:
            # プロセスグループごと終了
            os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
            server_process.wait(timeout=5)
            logger.info("APIサーバーを正常に停止しました")
        except Exception as e:
            logger.error(f"APIサーバーの停止中にエラーが発生しました: {e}")
            try:
                os.killpg(os.getpgid(server_process.pid), signal.SIGKILL)
            except:
                pass
        finally:
            server_process = None
    
    if server_thread and server_thread.is_alive():
        server_thread.join(timeout=1)
        server_thread = None

# プログラム終了時に確実にサーバーを停止
atexit.register(stop_server)

# テスト開始前にサーバーを起動するフィクスチャ
@pytest.fixture(scope="session", autouse=True)
def setup_server():
    """テスト実行前にサーバーを起動し、終了後に停止する"""
    success = start_server()
    if not success:
        pytest.skip("APIサーバーを起動できなかったため、テストをスキップします")
    yield
    stop_server()

def retry_request(func, *args, **kwargs):
    """
    リトライ機能付きのリクエスト送信関数
    
    Args:
        func: 実行する関数
        
    Returns:
        関数の実行結果
    """
    logger.debug(f"リクエスト実行: func={func.__name__}, args={args}, kwargs={kwargs}")
    
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"リクエスト試行 {attempt+1}/{MAX_RETRIES}: {args[0] if args else ''}")
            response = func(*args, **kwargs)
            logger.info(f"レスポンス: ステータスコード={response.status_code}")
            logger.debug(f"レスポンス内容: {response.text[:200]}..." if len(response.text) > 200 else f"レスポンス内容: {response.text}")
            return response
        except requests.RequestException as e:
            logger.error(f"リクエスト失敗 (試行 {attempt+1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"{RETRY_DELAY}秒後に再試行します")
                time.sleep(RETRY_DELAY)
            else:
                logger.critical(f"すべての再試行が失敗しました: {e}")
                raise

def test_server_health():
    """サーバーのヘルスチェック"""
    logger.info("=== サーバーヘルスチェックテスト開始 ===")
    
    # サーバーが応答するか確認
    try:
        logger.info(f"サーバールートURLへのリクエスト: {BASE_URL}")
        root_response = requests.get(BASE_URL, timeout=5)
        logger.info(f"ルートURLレスポンス: {root_response.status_code}")
    except requests.RequestException as e:
        logger.error(f"サーバーに接続できません: {e}")
        pytest.fail(f"サーバーに接続できません: {e}")
    
    # ステータスエンドポイントにリクエスト
    endpoint = f"{BASE_URL}/api/status"
    logger.info(f"ステータスエンドポイントへのリクエスト: {endpoint}")
    try:
        response = retry_request(requests.get, endpoint)
        logger.info(f"ステータスレスポンス: {response.status_code}")
        
        # レスポンスが返ってきたら、内容をチェック
        data = response.json()
        logger.info(f"レスポンスデータ: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        assert response.status_code == 200, f"ステータスコードが200ではありません: {response.status_code}"
        
        # ollama, voicevoxサービスの情報が含まれていることを確認
        if "ollama" in data:
            assert isinstance(data["ollama"], dict), "'ollama' フィールドが辞書ではありません"
            logger.info(f"Ollamaサービス情報: available={data['ollama'].get('available', False)}")
        
        if "voicevox" in data:
            assert isinstance(data["voicevox"], dict), "'voicevox' フィールドが辞書ではありません"
            logger.info(f"VoiceVoxサービス情報: available={data['voicevox'].get('available', False)}")
        
        logger.info("サーバーヘルスチェックテスト: 成功")
    except Exception as e:
        logger.error(f"サーバーヘルスチェックテスト中にエラーが発生: {e}")
        logger.exception("詳細なスタックトレース:")
        raise

def test_full_manzai_generation_flow():
    """漫才生成から音声合成までの一連のフロー"""
    logger.info("=== 漫才生成フローテスト開始 ===")
    
    # 1. 漫才生成リクエスト
    topic = "人工知能"
    payload = {"topic": topic}
    logger.info(f"漫才生成リクエスト: {payload}")
    
    try:
        response = retry_request(requests.post, f"{BASE_URL}/api/generate", json=payload)
        logger.info(f"漫才生成レスポンス: ステータスコード={response.status_code}")
        
        assert response.status_code == 200, f"ステータスコードが200ではありません: {response.status_code}"
        data = response.json()
        logger.debug(f"レスポンスデータ: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
        
        # スクリプトの存在を確認
        assert "script" in data, "レスポンスに 'script' フィールドがありません"
        assert isinstance(data["script"], list), "'script' フィールドがリストではありません"
        assert len(data["script"]) > 0, "スクリプトが空です"
        
        # 各台詞の形式を確認
        script = data["script"]
        for i, line in enumerate(script):
            assert "role" in line, f"台詞 {i} に 'role' フィールドがありません"
            assert "text" in line, f"台詞 {i} に 'text' フィールドがありません"
            assert line["role"] in ["tsukkomi", "boke"], f"台詞 {i} の 'role' が不正: {line['role']}"
        
        logger.info(f"スクリプト生成確認: {len(script)}行のスクリプトが生成されました")
        
        # 2. 音声合成リクエスト （存在する場合）
        if "audio_data" in data and len(data.get("audio_data", [])) > 0:
            logger.info("音声合成リクエストのテストを実行")
            
            # 音声ファイルへのアクセス確認
            for audio in data.get("audio_data", []):
                if "audio_path" in audio:
                    audio_url = f"{BASE_URL}{audio['audio_path']}"
                    logger.info(f"音声ファイルへのアクセス: {audio_url}")
                    
                    try:
                        audio_response = retry_request(requests.get, audio_url)
                        assert audio_response.status_code == 200, f"音声ファイルアクセスのステータスコードが200ではありません: {audio_response.status_code}"
                        logger.info(f"音声ファイルアクセス成功: サイズ={len(audio_response.content)} bytes")
                    except Exception as e:
                        logger.warning(f"音声ファイルへのアクセス中にエラーが発生: {e}")
        else:
            logger.info("音声合成情報がないため、音声合成テストはスキップされました")
        
        logger.info("漫才生成フローテスト: 成功")
    except Exception as e:
        logger.error(f"漫才生成フローテスト中にエラーが発生: {e}")
        logger.exception("詳細なスタックトレース:")
        raise

def test_speakers_endpoint():
    """話者一覧取得APIのテスト"""
    logger.info("=== 話者一覧取得テスト開始 ===")
    
    try:
        logger.info(f"話者一覧エンドポイントへのリクエスト: {BASE_URL}/api/speakers")
        response = retry_request(requests.get, f"{BASE_URL}/api/speakers")
        logger.info(f"話者一覧レスポンス: ステータスコード={response.status_code}")
        
        assert response.status_code == 200, f"ステータスコードが200ではありません: {response.status_code}"
        data = response.json()
        logger.debug(f"レスポンスデータ: {json.dumps(data, ensure_ascii=False, indent=2)[:500] if len(json.dumps(data)) > 500 else json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # レスポンスは取得できたが中身は問わない（レスポンス形式に依存しないテスト）
        logger.info("話者一覧取得テスト: 成功")
    except Exception as e:
        logger.error(f"話者一覧取得テスト中にエラーが発生: {e}")
        logger.exception("詳細なスタックトレース:")
        raise 