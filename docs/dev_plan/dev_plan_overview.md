# ManzAI Studio 開発計画書

## 1. プロジェクト概要

ManzAI Studioは、ローカルで動作する漫才生成・実演Webアプリケーションです。Ollamaの大規模言語モデル（LLM）を活用して漫才の台本を生成し、Live2Dキャラクターとボイスボックスを使用してアニメーションと音声で実演します。全ての機能はローカル環境で動作し、インターネット接続を必要としません。

## 2. 技術スタック

### バックエンド
- Python 3.10
- Flask 3.0.2
- Flask-CORS 4.0.0
- Ollama API (LLM推論用)
- VoiceVox (音声合成用)

### フロントエンド
- Node.js (18.0.0以上)
- React.js
- Live2D Cubism SDK for Web

### 開発環境
- Poetry (依存関係管理)
- pytest, pytest-cov (テスト)
- black, flake8, mypy (コード品質管理)
- Docker, docker-compose (コンテナ化)

## 3. 開発フェーズとタイムライン

### フェーズ1: 環境構築とベースアーキテクチャ (2週間)

#### タスク
1. **バックエンド基盤構築**
   - Flaskアプリケーションのベース構造の実装
   - 必要なAPIエンドポイントの定義
   - Dockerfileとdocker-compose.ymlの調整

2. **外部サービス統合基盤の実装**
   - Ollama APIクライアントの実装 
   - VoiceVox APIクライアントの実装

3. **テスト環境の整備**
   - 単体テストとモックの実装
   - CI/CD設定の検討

#### 成果物
- 動作するFlaskベースアプリケーション
- 外部サービス(Ollama, VoiceVox)との接続検証
- テスト環境の整備

### フェーズ2: コア機能の実装 (3週間)

#### タスク
1. **漫才スクリプト生成機能の実装**
   - Ollamaを使用した漫才スクリプト生成ロジックの実装
   - プロンプトエンジニアリングによる出力品質の向上
   - 生成されたスクリプトのフォーマット処理

2. **音声合成機能の実装**
   - VoiceVoxを使用した音声合成ロジックの実装
   - 話者の切り替え機能
   - モーラタイミングデータを活用した口の動きの同期準備

3. **Live2D統合の基礎実装**
   - Live2D Cubism SDK for Webの統合
   - キャラクターモデルの表示
   - 基本的なアニメーション制御

#### 成果物
- トピックから漫才スクリプトを生成する機能
- 生成されたスクリプトから音声を合成する機能
- 基本的なLive2Dキャラクター表示機能

### フェーズ3: フロントエンド開発とUI/UX (2週間)

#### タスク
1. **ユーザーインターフェース設計と実装**
   - トピック入力フォームの実装
   - 生成された漫才コンテンツの表示
   - 再生コントロールの実装

2. **Live2Dキャラクターの完全統合**
   - 音声と口の動きの同期
   - 表情やジェスチャーの追加
   - レスポンシブデザインへの対応

3. **インタラクティブ機能の追加**
   - 生成済みスクリプトの保存機能
   - 好みのキャラクター選択機能
   - 生成パラメータ調整機能

#### 成果物
- 完全な機能を持つユーザーインターフェース
- 音声と同期したLive2Dキャラクターアニメーション
- インタラクティブなユーザー体験

### フェーズ4: 統合とQA (1週間)

#### タスク
1. **システム統合**
   - バックエンドとフロントエンドの完全統合
   - エラーハンドリングの強化
   - パフォーマンス最適化

2. **テストと品質保証**
   - 単体テストとE2Eテストの実行
   - バグ修正
   - エッジケースの検証

3. **ドキュメント作成**
   - ユーザーマニュアルの作成
   - セットアップガイドの更新
   - APIドキュメントの完成

#### 成果物
- 完全統合されたシステム
- 包括的なテスト結果
- 詳細なドキュメント

## 4. ディレクトリ構造と実装詳細

```
manzai_studio/
├── backend/
│   ├── app/
│   │   ├── __init__.py        # アプリケーションファクトリ
│   │   ├── routes/            # APIルート
│   │   │   ├── __init__.py
│   │   │   ├── api.py         # APIエンドポイント
│   │   ├── services/          # ビジネスロジック
│   │   │   ├── __init__.py
│   │   │   ├── ollama.py      # Ollama APIクライアント
│   │   │   ├── voicevox.py    # VoiceVox APIクライアント
│   │   │   ├── script.py      # スクリプト生成処理
│   │   ├── models/            # データモデル
│   │   │   ├── __init__.py
│   │   │   ├── script.py      # スクリプトモデル
│   ├── tests/                 # テストコード
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   ├── test_services/
│   │   │   ├── test_ollama.py
│   │   │   ├── test_voicevox.py
│   ├── config.py              # 設定
├── frontend/
│   ├── src/
│   │   ├── components/        # Reactコンポーネント
│   │   │   ├── InputForm.jsx  # トピック入力フォーム
│   │   │   ├── Character.jsx  # Live2Dキャラクター表示
│   │   │   ├── ScriptDisplay.jsx # スクリプト表示
│   │   │   ├── Player.jsx     # 再生コントロール
│   │   ├── services/          # APIサービス
│   │   │   ├── api.js         # バックエンドAPI呼び出し
│   │   ├── App.jsx
│   │   ├── main.jsx
│   ├── public/
│   │   ├── models/            # Live2Dモデルファイル
│   ├── package.json
├── models/                    # モデルファイル保存用
│   ├── live2d/                # Live2Dモデル
│   ├── ollama/                # Ollamaモデル設定
├── pyproject.toml             # Poetry設定
├── docker-compose.yml         # Docker Compose設定
├── Dockerfile.dev             # 開発用Dockerfile
├── README.md                  # プロジェクト説明
```

## 5. APIエンドポイント設計

### バックエンドAPI

1. **健全性チェック**
   - エンドポイント: `GET /api/health`
   - 説明: システムの健全性チェック
   - レスポンス: `{"status": "healthy"}`

2. **漫才スクリプト生成**
   - エンドポイント: `POST /api/generate`
   - 説明: トピックから漫才スクリプトを生成
   - リクエスト: `{"topic": "string"}`
   - レスポンス: 
     ```json
     {
       "script": {
         "title": "string",
         "characters": ["A", "B"],
         "dialogue": [
           {"character": "A", "text": "string", "audio_file": "string"}
         ]
       }
     }
     ```

3. **音声合成**
   - エンドポイント: `POST /api/synthesize`
   - 説明: テキストから音声を合成
   - リクエスト: `{"text": "string", "speaker": integer}`
   - レスポンス: 音声ファイルのURL

4. **スクリプト保存**
   - エンドポイント: `POST /api/scripts`
   - 説明: 生成されたスクリプトを保存
   - リクエスト: スクリプトオブジェクト
   - レスポンス: 保存されたスクリプトのID

5. **保存されたスクリプト取得**
   - エンドポイント: `GET /api/scripts`
   - 説明: 保存されたスクリプト一覧を取得
   - レスポンス: スクリプトオブジェクトの配列

## 6. 実装の詳細

### 漫才スクリプト生成 (OllamaService)

```python
from typing import Dict, List, Any
import requests

class OllamaService:
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model
        
    def generate_script(self, topic: str) -> Dict[str, Any]:
        """Ollamaを使用して漫才スクリプトを生成する"""
        prompt = self._create_manzai_prompt(topic)
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
            
        result = response.json()
        
        # 生成されたテキストを解析してスクリプト形式に変換
        return self._parse_script(result["response"])
        
    def _create_manzai_prompt(self, topic: str) -> str:
        """漫才スクリプト生成用のプロンプトを作成"""
        return f"""
        あなたは日本の漫才スクリプトの名手です。
        「{topic}」をテーマにした面白い漫才の台本を作成してください。
        
        以下の条件に従ってください：
        - キャラクターAはツッコミ役、キャラクターBはボケ役とします
        - 会話形式で、各行は「A:」または「B:」で始まるようにしてください
        - 5分程度で演じられる長さにしてください
        - 日常的な言葉遣いで自然な会話にしてください
        - オチをつけてください
        
        台本のみを出力してください。
        """
        
    def _parse_script(self, text: str) -> Dict[str, Any]:
        """生成されたテキストを解析してスクリプト形式に変換"""
        lines = text.strip().split("\n")
        dialogue = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("A:"):
                character = "A"
                text = line[2:].strip()
            elif line.startswith("B:"):
                character = "B"
                text = line[2:].strip()
            else:
                # 形式に合わない行はスキップ
                continue
                
            dialogue.append({
                "character": character,
                "text": text,
                "audio_file": None  # 音声合成後に設定
            })
            
        return {
            "title": f"漫才「{topic}」",
            "characters": ["A", "B"],
            "dialogue": dialogue
        }
```

### 音声合成 (VoiceVoxService)

```python
from typing import Dict, Any, Optional
import requests
import os
import uuid
import json

class VoiceVoxService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.output_dir = os.path.join("static", "audio")
        os.makedirs(self.output_dir, exist_ok=True)
        
    def synthesize(self, text: str, speaker: int = 1) -> Dict[str, Any]:
        """テキストから音声を合成する"""
        # 音声合成用のクエリを作成
        audio_query_response = requests.post(
            f"{self.base_url}/audio_query",
            params={"text": text, "speaker": speaker}
        )
        
        if audio_query_response.status_code != 200:
            raise Exception(f"VoiceVox audio_query error: {audio_query_response.text}")
            
        audio_query = audio_query_response.json()
        
        # 音声合成を実行
        synthesis_response = requests.post(
            f"{self.base_url}/synthesis",
            headers={"Content-Type": "application/json"},
            params={"speaker": speaker},
            data=json.dumps(audio_query)
        )
        
        if synthesis_response.status_code != 200:
            raise Exception(f"VoiceVox synthesis error: {synthesis_response.text}")
            
        # 音声ファイルを保存
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "wb") as f:
            f.write(synthesis_response.content)
            
        # モーラタイミングデータを取得
        accent_phrases = audio_query.get("accent_phrases", [])
        timing_data = self._extract_timing_data(accent_phrases)
            
        return {
            "audio_file": f"/static/audio/{filename}",
            "timing_data": timing_data
        }
        
    def _extract_timing_data(self, accent_phrases: list) -> list:
        """アクセント句からモーラタイミングデータを抽出"""
        timing_data = []
        
        for phrase in accent_phrases:
            for mora in phrase.get("moras", []):
                timing_data.append({
                    "text": mora.get("text", ""),
                    "start": mora.get("start_time", 0),
                    "end": mora.get("end_time", 0)
                })
                
        return timing_data
        
    def process_script(self, script: Dict[str, Any], speaker_mapping: Dict[str, int] = None) -> Dict[str, Any]:
        """スクリプト内のすべての台詞に対して音声合成を行う"""
        if speaker_mapping is None:
            speaker_mapping = {"A": 1, "B": 3}  # デフォルトのスピーカーマッピング
            
        for i, line in enumerate(script["dialogue"]):
            result = self.synthesize(line["text"], speaker_mapping[line["character"]])
            script["dialogue"][i]["audio_file"] = result["audio_file"]
            script["dialogue"][i]["timing_data"] = result["timing_data"]
            
        return script
```

### Live2D統合 (フロントエンド)

```javascript
// Character.jsx
import React, { useEffect, useRef } from 'react';

const Character = ({ characterId, mouthOpenValue = 0 }) => {
  const live2dRef = useRef(null);
  const modelRef = useRef(null);

  useEffect(() => {
    // Live2Dモデルの初期化
    const initLive2D = async () => {
      try {
        // Live2D SDKの読み込み
        await import('@/lib/live2d.min.js');
        
        // モデルのロード
        const modelPath = `/models/live2d/${characterId}/model.json`;
        modelRef.current = new Live2DModel();
        await modelRef.current.load(modelPath);
        
        // キャンバスに描画
        const canvas = live2dRef.current;
        modelRef.current.startRender(canvas);
      } catch (error) {
        console.error('Failed to initialize Live2D model:', error);
      }
    };

    initLive2D();
    
    return () => {
      // クリーンアップ
      if (modelRef.current) {
        modelRef.current.stopRender();
      }
    };
  }, [characterId]);
  
  // 口の開閉制御
  useEffect(() => {
    if (modelRef.current) {
      modelRef.current.setParamFloat('ParamMouthOpenY', mouthOpenValue);
    }
  }, [mouthOpenValue]);

  return (
    <div className="character-container">
      <canvas 
        ref={live2dRef} 
        width={512} 
        height={512} 
        style={{ width: '100%', maxWidth: '512px' }}
      />
    </div>
  );
};

export default Character;
```

```javascript
// Player.jsx
import React, { useState, useEffect, useRef } from 'react';
import Character from './Character';

const Player = ({ script }) => {
  const [currentLineIndex, setCurrentLineIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [mouthOpenValue, setMouthOpenValue] = useState(0);
  const audioRef = useRef(null);
  
  const currentLine = script?.dialogue[currentLineIndex];
  
  // 音声再生と次の行への移動
  useEffect(() => {
    if (isPlaying && audioRef.current) {
      audioRef.current.play();
      
      // 音声終了時の処理
      audioRef.current.onended = () => {
        if (currentLineIndex < script.dialogue.length - 1) {
          // 次の行へ
          setCurrentLineIndex(prev => prev + 1);
        } else {
          // 再生終了
          setIsPlaying(false);
        }
      };
    }
  }, [isPlaying, currentLineIndex, script]);
  
  // 口の動きの制御
  useEffect(() => {
    if (!isPlaying || !currentLine?.timing_data) return;
    
    // タイマーを使用して口の動きを制御
    const intervalId = setInterval(() => {
      if (!audioRef.current) return;
      
      const currentTime = audioRef.current.currentTime * 1000; // ミリ秒に変換
      let isMouthOpen = false;
      
      // 現在の時間に対応するモーラを検索
      for (const mora of currentLine.timing_data) {
        if (currentTime >= mora.start && currentTime <= mora.end) {
          isMouthOpen = true;
          break;
        }
      }
      
      // 口の開閉値を設定
      setMouthOpenValue(isMouthOpen ? 1 : 0);
    }, 50); // 50msごとに更新
    
    return () => clearInterval(intervalId);
  }, [isPlaying, currentLine]);
  
  const togglePlay = () => {
    setIsPlaying(!isPlaying);
    if (!isPlaying) {
      // 再生開始時は最初の行から
      setCurrentLineIndex(0);
    } else {
      // 一時停止時は音声を停止
      audioRef.current?.pause();
    }
  };
  
  return (
    <div className="player-container">
      <div className="character-display">
        <Character 
          characterId={currentLine?.character === 'A' ? 'characterA' : 'characterB'}
          mouthOpenValue={mouthOpenValue}
        />
      </div>
      
      <div className="controls">
        <button onClick={togglePlay}>
          {isPlaying ? '一時停止' : '再生'}
        </button>
      </div>
      
      <div className="script-display">
        <p className="current-line">
          <span className="character-name">{currentLine?.character}:</span> {currentLine?.text}
        </p>
      </div>
      
      {currentLine?.audio_file && (
        <audio 
          ref={audioRef}
          src={currentLine.audio_file} 
          preload="auto"
        />
      )}
    </div>
  );
};

export default Player;
```

## 7. デプロイメントとセットアップ

### Docker環境を使用した開発とデプロイ

1. **開発環境の起動**
   ```bash
   docker-compose up -d
   ```

2. **必要なモデルのセットアップ**
   ```bash
   # コンテナ内でOllamaモデルをダウンロード
   docker-compose exec ollama ollama pull phi
   ```

3. **アプリケーションへのアクセス**
   - バックエンド: http://localhost:5000
   - フロントエンド開発サーバー: http://localhost:3000

### スタンドアロンセットアップ

1. **Python環境のセットアップ**
   ```bash
   pyenv install 3.10.13
   pyenv local 3.10.13
   poetry install
   ```

2. **フロントエンド環境のセットアップ**
   ```bash
   cd frontend
   npm install
   ```

3. **外部サービスのインストール**
   - Ollamaをインストール
   - VoiceVoxをインストール

4. **開発サーバーの起動**
   ```bash
   # バックエンド
   poetry run flask run
   
   # フロントエンド（別ターミナル）
   cd frontend && npm run dev
   ```

## 8. テスト戦略

### 単体テスト

- **バックエンドサービス**
  - OllamaServiceのテスト
  - VoiceVoxServiceのテスト
  - スクリプト処理ロジックのテスト

- **APIエンドポイント**
  - 各エンドポイントのリクエスト/レスポンスのテスト
  - エラーハンドリングのテスト

### 統合テスト

- **外部サービス連携**
  - Ollama APIとの実際の連携テスト
  - VoiceVox APIとの実際の連携テスト

- **E2Eテスト**
  - トピック入力から漫才再生までの一連のフローテスト

### パフォーマンステスト

- ローカル環境での応答時間テスト
- メモリ使用量の監視
- 同時処理の限界テスト

## 9. 課題と解決策

### 予想される課題

1. **Ollamaの出力品質**
   - **課題**: 生成されるスクリプトが常に高品質とは限らない
   - **解決策**: プロンプト最適化と複数回生成によるベスト選択

2. **音声合成の自然さ**
   - **課題**: 漫才特有のイントネーションを表現しづらい
   - **解決策**: VoiceVoxのパラメータ調整と適切な話者選択

3. **Live2Dと音声の同期**
   - **課題**: 精密な口の動きの同期が難しい
   - **解決策**: モーラタイミングデータの活用とテスト駆動開発

4. **パフォーマンス**
   - **課題**: ローカル環境でのLLM推論が遅い場合がある
   - **解決策**: 軽量モデル（Phi）の使用とキャッシュの活用

## 10. 今後の展望

1. **機能拡張**
   - 複数のキャラクターモデル対応
   - より多様な漫才スタイルの生成
   - ユーザー定義プロンプトの追加

2. **ユーザー体験の向上**
   - リアルタイムフィードバック
   - キャラクターのカスタマイズ
   - 生成結果の編集機能

3. **技術的改善**
   - リアルタイムリップシンク精度の向上
   - 生成モデルの最適化
   - オフライン機能の強化

## 11. まとめ

ManzAI Studioは、最新のAI技術を活用したローカルで動作する漫才生成・実演アプリケーションです。Flask、Ollama、VoiceVox、Live2Dを統合することで、ユーザーはトピックを入力するだけで漫才を生成し、アニメーションキャラクターと音声で実演を楽しむことができます。

このプロジェクトは4つのフェーズに分けて開発され、約2ヶ月で完成する予定です。各フェーズで具体的な成果物を設定し、着実に進めていきます。

技術的にはPython 3.10、Flask、React.jsを主要フレームワークとして使用し、Poetryによる依存関係管理と包括的なテスト戦略により、高品質なアプリケーションを目指します。
