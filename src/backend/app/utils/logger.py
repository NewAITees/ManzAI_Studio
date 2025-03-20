"""
Logging utility for the application with emoji support and structured logging
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# Emojiとログレベルのマッピング
EMOJI_MAP = {
    'DEBUG': '🔍',
    'INFO': '📝',
    'WARNING': '⚠️',
    'ERROR': '❌',
    'CRITICAL': '🚨',
    'TEST': '🧪',
    'DATA': '📊',
    'API': '🌐',
}

class EmojiFormatter(logging.Formatter):
    """カスタムフォーマッタでemoji付きログを生成"""
    
    def format(self, record):
        emoji = EMOJI_MAP.get(record.levelname, '📌')
        record.emoji = emoji
        return super().format(record)

def setup_logger(name: str = __name__) -> logging.Logger:
    """
    アプリケーション用のロガーをセットアップ
    
    Args:
        name: ロガーの名前（デフォルトは呼び出し元モジュール名）
    
    Returns:
        設定済みのロガーインスタンス
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # ログ出力フォーマットの定義
    fmt = '%(emoji)s %(asctime)s [%(name)s] %(levelname)s: %(message)s'
    formatter = EmojiFormatter(fmt, datefmt='%Y-%m-%d %H:%M:%S')

    # コンソール出力用ハンドラ
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# デフォルトロガーのインスタンス化
logger = setup_logger() 