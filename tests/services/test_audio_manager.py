import pytest
import os
import tempfile
from src.services.audio_manager import AudioManager

@pytest.fixture
def audio_manager():
    """テスト用のAudioManagerインスタンスを作成"""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = AudioManager(audio_dir=temp_dir)
        yield manager

@pytest.fixture
def sample_audio_data():
    """テスト用の音声データを作成"""
    return b'test audio data'

def test_save_audio_file(audio_manager, sample_audio_data):
    """音声ファイルが正しく保存されることを確認"""
    file_path = audio_manager.save_audio(sample_audio_data, "test_audio")
    
    assert os.path.exists(file_path)
    with open(file_path, 'rb') as f:
        saved_data = f.read()
    assert saved_data == sample_audio_data

def test_get_audio_file(audio_manager, sample_audio_data):
    """音声ファイルが正しく取得できることを確認"""
    file_path = audio_manager.save_audio(sample_audio_data, "test_audio")
    
    retrieved_data = audio_manager.get_audio("test_audio")
    assert retrieved_data == sample_audio_data

def test_get_audio_file_not_found(audio_manager):
    """存在しない音声ファイルを要求した場合にエラーを返すことを確認"""
    with pytest.raises(FileNotFoundError) as exc_info:
        audio_manager.get_audio("non_existent_audio")
    
    assert "audio file not found" in str(exc_info.value).lower()

def test_save_audio_file_with_invalid_data(audio_manager):
    """不正なデータで音声ファイルを保存しようとした場合にエラーを返すことを確認"""
    with pytest.raises(ValueError) as exc_info:
        audio_manager.save_audio(None, "test_audio")
    
    assert "invalid audio data" in str(exc_info.value).lower()

def test_save_audio_file_with_invalid_filename(audio_manager, sample_audio_data):
    """不正なファイル名で音声ファイルを保存しようとした場合にエラーを返すことを確認"""
    with pytest.raises(ValueError) as exc_info:
        audio_manager.save_audio(sample_audio_data, "")
    
    assert "invalid filename" in str(exc_info.value).lower()

def test_cleanup_old_audio_files(audio_manager, sample_audio_data):
    """古い音声ファイルが正しく削除されることを確認"""
    # 複数の音声ファイルを作成
    file_paths = []
    for i in range(3):
        file_path = audio_manager.save_audio(sample_audio_data, f"test_audio_{i}")
        file_paths.append(file_path)
    
    # すべてのファイルが存在することを確認
    for file_path in file_paths:
        assert os.path.exists(file_path)
    
    # クリーンアップを実行
    audio_manager.cleanup_old_files(max_files=2)
    
    # 最新の2つのファイルのみが残っていることを確認
    remaining_files = os.listdir(audio_manager.audio_dir)
    assert len(remaining_files) == 2 