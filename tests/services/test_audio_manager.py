"""AudioManagerのテスト"""
import pytest
import os
import tempfile
from typing import Generator

from src.backend.app.services.audio_manager import AudioManager

@pytest.fixture
def audio_manager() -> Generator[AudioManager, None, None]:
    """テスト用のAudioManagerインスタンスを作成"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield AudioManager(audio_dir=temp_dir)

@pytest.fixture
def sample_audio_data() -> bytes:
    """テスト用の音声データを作成"""
    # WAVファイルのヘッダーを含むテストデータ
    return b'RIFF' + b'\x00' * 36 + b'data' + b'\x00' * 4 + b'test audio data'

class TestAudioManagerBasics:
    """基本機能のテストスイート"""
    
    def test_save_and_get_audio(self, audio_manager: AudioManager, sample_audio_data: bytes):
        """音声ファイルの保存と取得の基本機能"""
        file_path = audio_manager.save_audio(sample_audio_data, "test_audio")
        
        # ファイルが正しく保存されていることを確認
        assert os.path.exists(file_path)
        assert file_path.endswith(".wav")  # 拡張子の確認
        with open(file_path, 'rb') as f:
            saved_data = f.read()
            assert saved_data == sample_audio_data
            assert saved_data.startswith(b'RIFF')  # WAVファイルのヘッダーを確認
        
        # ファイルが正しく取得できることを確認
        actual_filename = os.path.basename(file_path)
        retrieved_data = audio_manager.get_audio(actual_filename)
        assert retrieved_data == sample_audio_data
        assert retrieved_data.startswith(b'RIFF')  # 取得したデータもWAVファイルであることを確認

class TestAudioManagerErrorHandling:
    """エラー処理のテストスイート"""
    
    def test_file_not_found(self, audio_manager: AudioManager):
        """存在しないファイルの取得時のエラー処理"""
        with pytest.raises(FileNotFoundError, match="Audio file 'non_existent_audio' not found"):
            audio_manager.get_audio("non_existent_audio")
    
    def test_invalid_data(self, audio_manager: AudioManager):
        """不正なデータでの保存時のエラー処理"""
        with pytest.raises(ValueError, match="Invalid audio data: data cannot be None"):
            audio_manager.save_audio(None, "test_audio")  # type: ignore
    
    def test_invalid_filename(self, audio_manager: AudioManager, sample_audio_data: bytes):
        """不正なファイル名での保存時のエラー処理"""
        with pytest.raises(ValueError, match="Invalid filename: filename cannot be empty"):
            audio_manager.save_audio(sample_audio_data, "")

class TestAudioManagerMaintenance:
    """メンテナンス機能のテストスイート"""
    
    def test_cleanup_old_files(self, audio_manager: AudioManager, sample_audio_data: bytes):
        """古いファイルのクリーンアップ機能"""
        # テストファイルの作成
        file_paths = [
            audio_manager.save_audio(sample_audio_data, f"test_audio_{i}")
            for i in range(3)
        ]
        
        # クリーンアップ前の確認
        assert all(os.path.exists(path) for path in file_paths)
        assert all(path.endswith(".wav") for path in file_paths)
        
        # クリーンアップの実行と確認
        audio_manager.cleanup_old_files(max_files=2)
        remaining_files = os.listdir(audio_manager.audio_dir)
        assert len(remaining_files) == 2
        # 最新のファイルが残っていることを確認
        assert all(file.endswith(".wav") for file in remaining_files)
        assert all(os.path.getsize(os.path.join(audio_manager.audio_dir, file)) > 0 for file in remaining_files) 