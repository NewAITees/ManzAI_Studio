"""
ManzAI Studioのエントリーポイント
後方互換性のために残しています
"""

from src.backend.app import create_app

# アプリケーションインスタンスを作成
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
