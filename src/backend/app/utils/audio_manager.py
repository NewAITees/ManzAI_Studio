import os
import time
import logging
from typing import List, Optional
from datetime import datetime

from src.backend.app.models.audio import AudioFile

logger = logging.getLogger(__name__)

class AudioFileNotFoundError(Exception):
    """音声ファイルが見つからない場合のエラー"""
    pass

class AudioManager:
    """音声ファイルの管理を担当するクラス"""
    
    def __init__(self, audio_dir: str = "audio") -> None:
        """AudioManagerの初期化
        
        Args:
            audio_dir: 音声ファイルを保存するディレクトリ
        """
        self.audio_dir = audio_dir
        os.makedirs(audio_dir, exist_ok=True)
        logger.info(f"AudioManager initialized with directory: {audio_dir}")
    
    def save_audio(self, audio_data: bytes, filename: str) -> AudioFile:
        """音声データをファイルとして保存
        
        Args:
            audio_data: 保存する音声データ
            filename: ファイル名
            
        Returns:
            AudioFile: 保存された音声ファイルの情報
            
        Raises:
            ValueError: 音声データがNoneの場合、またはファイル名が空の場合
        """
        if audio_data is None:
            raise ValueError("音声データがありません")
        
        if not filename:
            raise ValueError("ファイル名が無効です")
        
        # タイムスタンプを付加したファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}.wav"
        file_path = os.path.join(self.audio_dir, safe_filename)
        
        # 音声データを保存
        with open(file_path, 'wb') as f:
            f.write(audio_data)
        
        # ファイルサイズを取得
        file_size = os.path.getsize(file_path)
        
        # AudioFileモデルを作成して返す
        return AudioFile(
            path=file_path,
            filename=safe_filename,
            created_at=datetime.now(),
            size_bytes=file_size
        )
    
    def get_audio(self, filename: str) -> bytes:
        """指定されたファイル名の音声データを取得
        
        Args:
            filename: 取得する音声ファイルのファイル名
            
        Returns:
            bytes: 音声データ
            
        Raises:
            AudioFileNotFoundError: 指定されたファイルが存在しない場合
        """
        # ファイル名に.wavが含まれていない場合は追加
        if not filename.endswith('.wav'):
            filename = f"{filename}.wav"
        
        file_path = os.path.join(self.audio_dir, filename)
        
        if not os.path.exists(file_path):
            raise AudioFileNotFoundError(f"音声ファイルが見つかりません: {filename}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    def list_audio_files(self) -> List[AudioFile]:
        """利用可能な音声ファイルの一覧を取得
        
        Returns:
            List[AudioFile]: 音声ファイル情報のリスト
        """
        # ディレクトリ内のWAVファイル一覧を取得
        files = [f for f in os.listdir(self.audio_dir) if f.endswith('.wav')]
        
        # AudioFileモデルのリストに変換
        audio_files = []
        for filename in files:
            file_path = os.path.join(self.audio_dir, filename)
            file_size = os.path.getsize(file_path)
            created_time = datetime.fromtimestamp(os.path.getctime(file_path))
            
            audio_files.append(AudioFile(
                path=file_path,
                filename=filename,
                created_at=created_time,
                size_bytes=file_size
            ))
        
        # 作成日時の新しい順にソート
        audio_files.sort(key=lambda x: x.created_at, reverse=True)
        return audio_files
    
    def cleanup_old_files(self, max_files: int = 10) -> int:
        """古い音声ファイルを削除
        
        Args:
            max_files: 保持する最大ファイル数
            
        Returns:
            int: 削除されたファイル数
        """
        # 全ファイルをリスト化
        audio_files = self.list_audio_files()
        
        # max_filesを超えるファイルを削除
        deleted_count = 0
        for audio_file in audio_files[max_files:]:
            try:
                os.remove(audio_file.path)
                deleted_count += 1
                logger.info(f"Deleted old audio file: {audio_file.filename}")
            except OSError as e:
                logger.error(f"Failed to remove file {audio_file.path}: {e}")
        
        return deleted_count 