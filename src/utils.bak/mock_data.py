"""
モックデータを提供するユーティリティモジュール
"""
import logging
from typing import List, Dict, Any, Optional

from src.models.script import ScriptLine, ManzaiScript, Role

# ロガーの設定
logger = logging.getLogger(__name__)

# デフォルトのモックスクリプト（スクリプトラインのリスト）
DEFAULT_MOCK_SCRIPT = [
    ScriptLine(role=Role.TSUKKOMI, text="今日のテーマは何だっけ？"),
    ScriptLine(role=Role.BOKE, text="今日のテーマは「旅行」だよ！最近どこか行った？"),
    ScriptLine(role=Role.TSUKKOMI, text="いや、行ってないよ。コロナ禍から..."),
    ScriptLine(role=Role.BOKE, text="僕はこの前、海外旅行に行ってきたよ！"),
    ScriptLine(role=Role.TSUKKOMI, text="へー、どこに行ったの？"),
    ScriptLine(role=Role.BOKE, text="グーグルアースで世界一周！"),
    ScriptLine(role=Role.TSUKKOMI, text="それ旅行じゃないから！"),
    ScriptLine(role=Role.BOKE, text="でもね、飛行機代も宿泊費もかからないよ！"),
    ScriptLine(role=Role.TSUKKOMI, text="だからそれは旅行じゃなくて、ただの検索だって！"),
    ScriptLine(role=Role.BOKE, text="じゃあ、君はどんな旅行がしたいの？"),
    ScriptLine(role=Role.TSUKKOMI, text="そうだな、やっぱり温泉とかいいよな。"),
    ScriptLine(role=Role.BOKE, text="僕も温泉好き！特に源泉かけ流しの..."),
    ScriptLine(role=Role.TSUKKOMI, text="お前、本当に温泉入ったことあるの？"),
    ScriptLine(role=Role.BOKE, text="もちろん！家のお風呂に入浴剤入れたよ！"),
    ScriptLine(role=Role.TSUKKOMI, text="だからそれは温泉じゃないって！"),
    ScriptLine(role=Role.BOKE, text="でもパッケージに「温泉気分」って書いてあったよ？"),
    ScriptLine(role=Role.TSUKKOMI, text="気分だけだろ！実際の温泉とは全然違うわ！")
]

# APIレスポンス用の辞書形式に変換したモックスクリプト
DEFAULT_MOCK_SCRIPT_DICT = [
    {"role": "tsukkomi", "text": "今日のテーマは何だっけ？"},
    {"role": "boke", "text": "今日のテーマは「旅行」だよ！最近どこか行った？"},
    {"role": "tsukkomi", "text": "いや、行ってないよ。コロナ禍から..."},
    {"role": "boke", "text": "僕はこの前、海外旅行に行ってきたよ！"},
    {"role": "tsukkomi", "text": "へー、どこに行ったの？"},
    {"role": "boke", "text": "グーグルアースで世界一周！"},
    {"role": "tsukkomi", "text": "それ旅行じゃないから！"},
    {"role": "boke", "text": "でもね、飛行機代も宿泊費もかからないよ！"},
    {"role": "tsukkomi", "text": "だからそれは旅行じゃなくて、ただの検索だって！"},
    {"role": "boke", "text": "じゃあ、君はどんな旅行がしたいの？"},
    {"role": "tsukkomi", "text": "そうだな、やっぱり温泉とかいいよな。"},
    {"role": "boke", "text": "僕も温泉好き！特に源泉かけ流しの..."},
    {"role": "tsukkomi", "text": "お前、本当に温泉入ったことあるの？"},
    {"role": "boke", "text": "もちろん！家のお風呂に入浴剤入れたよ！"},
    {"role": "tsukkomi", "text": "だからそれは温泉じゃないって！"},
    {"role": "boke", "text": "でもパッケージに「温泉気分」って書いてあったよ？"},
    {"role": "tsukkomi", "text": "気分だけだろ！実際の温泉とは全然違うわ！"}
]

def get_mock_script(topic: Optional[str] = None) -> List[Dict[str, str]]:
    """
    指定されたトピックに基づいたモックスクリプトを取得します。
    現在はトピックに関係なく同じスクリプトを返します。
    
    Args:
        topic: スクリプトのトピック（現在は無視される）
        
    Returns:
        モックスクリプトの配列
    """
    logger.info(f"Returning mock script for topic: {topic}")
    return DEFAULT_MOCK_SCRIPT_DICT

def get_mock_script_model(topic: Optional[str] = None) -> ManzaiScript:
    """
    指定されたトピックに基づいたモックスクリプトをPydanticモデルとして取得します。
    現在はトピックに関係なく同じスクリプトを返します。
    
    Args:
        topic: スクリプトのトピック（現在は無視される）
        
    Returns:
        ManzaiScript: Pydanticモデルとしてのモックスクリプト
    """
    logger.info(f"Returning mock script model for topic: {topic}")
    return ManzaiScript(script=DEFAULT_MOCK_SCRIPT, topic=topic) 