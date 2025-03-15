"""
モックデータを提供するユーティリティモジュール
"""
import logging

# ロガーの設定
logger = logging.getLogger(__name__)

# デフォルトのモックスクリプト
DEFAULT_MOCK_SCRIPT = [
    {
        "role": "tsukkomi",
        "text": "今日のテーマは何だっけ？"
    },
    {
        "role": "boke",
        "text": "今日のテーマは「旅行」だよ！最近どこか行った？"
    },
    {
        "role": "tsukkomi",
        "text": "いや、行ってないよ。コロナ禍から..."
    },
    {
        "role": "boke",
        "text": "僕はこの前、海外旅行に行ってきたよ！"
    },
    {
        "role": "tsukkomi",
        "text": "へー、どこに行ったの？"
    },
    {
        "role": "boke",
        "text": "グーグルアースで世界一周！"
    },
    {
        "role": "tsukkomi",
        "text": "それ旅行じゃないから！"
    },
    {
        "role": "boke",
        "text": "でもね、飛行機代も宿泊費もかからないよ！"
    },
    {
        "role": "tsukkomi",
        "text": "だからそれは旅行じゃなくて、ただの検索だって！"
    },
    {
        "role": "boke",
        "text": "じゃあ、君はどんな旅行がしたいの？"
    },
    {
        "role": "tsukkomi",
        "text": "そうだな、やっぱり温泉とかいいよな。"
    },
    {
        "role": "boke",
        "text": "僕も温泉好き！特に源泉かけ流しの..."
    },
    {
        "role": "tsukkomi",
        "text": "お前、本当に温泉入ったことあるの？"
    },
    {
        "role": "boke",
        "text": "もちろん！家のお風呂に入浴剤入れたよ！"
    },
    {
        "role": "tsukkomi",
        "text": "だからそれは温泉じゃないって！"
    },
    {
        "role": "boke",
        "text": "でもパッケージに「温泉気分」って書いてあったよ？"
    },
    {
        "role": "tsukkomi",
        "text": "気分だけだろ！実際の温泉とは全然違うわ！"
    }
]

def get_mock_script(topic: str = None) -> list:
    """
    指定されたトピックに基づいたモックスクリプトを取得します。
    現在はトピックに関係なく同じスクリプトを返します。
    
    Args:
        topic: スクリプトのトピック（現在は無視される）
        
    Returns:
        モックスクリプトの配列
    """
    logger.info(f"Returning mock script for topic: {topic}")
    return DEFAULT_MOCK_SCRIPT 