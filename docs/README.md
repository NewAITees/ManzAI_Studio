# ManzAI Studio

ManzAI Studioは、AI支援の漫才脚本生成と、Live2Dを活用したバーチャルキャラクターによる実演を可能にするアプリケーションです。

## 主な機能

- **AIによる漫才脚本生成**: お題を入力するだけで、AIが漫才脚本を生成します
- **テキスト読み上げ**: 生成された脚本をAIボイスで読み上げます
- **Live2Dキャラクター表示**: 台詞に合わせてLive2Dキャラクターが口パクします
- **カスタムLive2Dモデル対応**: 独自のLive2Dモデルを追加できます
- **プロンプトカスタマイズ**: AIへの指示となるプロンプトをカスタマイズできます

## インストール方法

```bash
# リポジトリのクローン
git clone https://github.com/yourusername/manzai-studio.git
cd manzai-studio

# 依存関係のインストール
# バックエンド
cd src/backend
pip install -r requirements.txt

# フロントエンド
cd ../../frontend
npm install
```

## 使用方法

### 起動方法

```bash
# バックエンドの起動
cd src/backend
python run.py

# フロントエンドの起動 (別ターミナルで)
cd frontend
npm start
```

ブラウザで `http://localhost:3000` にアクセスしてアプリケーションを使用できます。

### Live2Dモデルの追加

Live2Dモデルを追加するには、`frontend/public/live2d/models/` ディレクトリに新しいモデルディレクトリを作成し、必要なファイルを配置します。詳細は [モデル設定ガイド](./model_setup.md) を参照してください。

### プロンプトのカスタマイズ

設定画面からプロンプトを編集・追加できます。これにより、AIが生成する漫才の特徴やスタイルをカスタマイズできます。

## 開発ドキュメント

- [開発工程書](./dev_plan/dev_plan7_completed.md) - 開発ステップの詳細情報
- [モデル設定ガイド](./model_setup.md) - Live2Dモデルの設定方法
- [プロンプト作成ガイド](./prompt_guide.md) - 効果的なプロンプトの作成方法

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 謝辞

- [Live2D Cubism SDK](https://www.live2d.com/)
- [OpenAI API](https://openai.com/api/)
- [その他使用ライブラリ] 