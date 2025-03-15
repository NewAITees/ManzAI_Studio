import os

class Config:
    """アプリケーション設定クラス"""
    # Flask設定
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-for-development')
    DEBUG = os.environ.get('FLASK_DEBUG', '1') == '1'
    
    # サービス接続先設定
    VOICEVOX_URL = os.environ.get('VOICEVOX_URL', 'http://voicevox:50021')
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://ollama:11434')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'gemma3:4b')
    OLLAMA_INSTANCE_TYPE = os.environ.get('OLLAMA_INSTANCE_TYPE', 'docker')
    
    # ファイルパス設定
    AUDIO_DIR = os.environ.get('AUDIO_DIR', 'audio') 