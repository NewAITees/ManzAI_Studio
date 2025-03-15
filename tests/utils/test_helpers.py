"""
テスト用ヘルパー関数を提供するモジュール。
様々なテストで共通して使用される機能をこのファイルに集約します。
"""
import os
import json
import pytest
from flask import Flask
from unittest.mock import patch, MagicMock

# アプリケーションのインポート
from src.app import app as flask_app


@pytest.fixture
def app():
    """
    テスト用Flaskアプリケーションを提供するフィクスチャ
    
    Returns:
        Flaskアプリケーションのインスタンス
    """
    flask_app.config.update({
        "TESTING": True,
    })
    return flask_app


@pytest.fixture
def client(app):
    """
    テスト用クライアントを提供するフィクスチャ
    
    Args:
        app: Flaskアプリケーションのインスタンス
        
    Returns:
        テスト用クライアント
    """
    return app.test_client()


def create_mock_ollama_service():
    """
    モック化されたOllamaServiceを作成する
    
    Returns:
        OllamaServiceのモックオブジェクト
    """
    mock_service = MagicMock()
    mock_service.generate_script.return_value = {
        "script": [
            {"speaker": "ツッコミ", "text": "こんにちは"},
            {"speaker": "ボケ", "text": "どうも"}
        ]
    }
    mock_service.list_models.return_value = ["llama2", "mistral"]
    return mock_service


def create_mock_voicevox_service():
    """
    モック化されたVoiceVoxServiceを作成する
    
    Returns:
        VoiceVoxServiceのモックオブジェクト
    """
    mock_service = MagicMock()
    mock_service.synthesize.return_value = "test_audio_file.wav"
    mock_service.list_speakers.return_value = [
        {"name": "四国めたん", "styles": [{"id": 2, "name": "ノーマル"}]},
        {"name": "ずんだもん", "styles": [{"id": 3, "name": "ノーマル"}]}
    ]
    return mock_service


def create_mock_audio_manager():
    """
    モック化されたAudioManagerを作成する
    
    Returns:
        AudioManagerのモックオブジェクト
    """
    mock_manager = MagicMock()
    mock_manager.get_audio_file_path.return_value = "/path/to/audio.wav"
    mock_manager.generate_filename.return_value = "test_audio_file.wav"
    return mock_manager


def load_test_data(filename):
    """
    テスト用データファイルを読み込む
    
    Args:
        filename: テストデータファイル名
        
    Returns:
        読み込まれたJSONデータ
    """
    test_data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    with open(os.path.join(test_data_dir, filename), 'r', encoding='utf-8') as f:
        return json.load(f) 