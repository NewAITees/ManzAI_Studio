import os
from datetime import datetime


class AudioManager:
    """音声ファイルの管理を担当するクラス"""

    def __init__(self, audio_dir: str = "audio") -> None:
        """AudioManagerの初期化

        Args:
            audio_dir (str): 音声ファイルを保存するディレクトリ
        """
        self.audio_dir = audio_dir
        os.makedirs(audio_dir, exist_ok=True)

    def save_audio(self, audio_data: bytes, filename: str) -> str:
        """音声データをファイルとして保存

        Args:
            audio_data (bytes): 保存する音声データ
            filename (str): ファイル名

        Returns:
            str: 保存されたファイルのパス

        Raises:
            ValueError: 音声データがNoneの場合、またはファイル名が空の場合
        """
        if audio_data is None:
            raise ValueError("invalid audio data")

        if not filename:
            raise ValueError("invalid filename")

        # タイムスタンプを付加したファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{filename}.wav"
        file_path = os.path.join(self.audio_dir, safe_filename)

        # 音声データを保存
        with open(file_path, "wb") as f:
            f.write(audio_data)

        return file_path

    def get_audio(self, filename: str) -> bytes:
        """指定されたファイル名の音声データを取得

        Args:
            filename (str): 取得する音声ファイルのファイル名

        Returns:
            bytes: 音声データ

        Raises:
            FileNotFoundError: 指定されたファイルが存在しない場合
        """
        # ファイル名に.wavが含まれていない場合は追加
        if not filename.endswith(".wav"):
            filename = f"{filename}.wav"

        file_path = os.path.join(self.audio_dir, filename)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {filename}")

        with open(file_path, "rb") as f:
            return f.read()

    def cleanup_old_files(self, max_files: int = 10) -> None:
        """古い音声ファイルを削除

        Args:
            max_files (int): 保持する最大ファイル数
        """
        # ディレクトリ内のファイル一覧を取得
        files = os.listdir(self.audio_dir)

        # ファイルの作成時刻でソート
        file_paths = [os.path.join(self.audio_dir, f) for f in files]
        file_paths.sort(key=os.path.getctime, reverse=True)

        # 古いファイルを削除
        for file_path in file_paths[max_files:]:
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Failed to remove file {file_path}: {e}")
