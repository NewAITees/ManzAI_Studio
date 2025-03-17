# ManzAI Studio API リファレンス

## 概要

ManzAI StudioのREST APIは、漫才台本の生成、音声合成、モデル管理などの機能を提供します。

## 共通仕様

### ベースURL
```
http://localhost:5000/api
```

### リクエストヘッダー
すべてのAPIリクエストには適切な`Content-Type`ヘッダーが必要です：

- JSON形式のリクエスト: `Content-Type: application/json`
- ファイルアップロード: `Content-Type: multipart/form-data`

### エラーレスポンス
エラー発生時は以下の形式でレスポンスが返されます：

```json
{
    "error": "エラーメッセージ",
    "code": "エラーコード",
    "details": {}  // オプショナル
}
```

## エンドポイント一覧

### 1. 台本生成 API

#### POST /generate-script

漫才台本を生成します。

**リクエスト**
- Content-Type: `application/json`

```json
{
    "topic": "猫",
    "model": "gemma3:4b"  // オプショナル
}
```

**レスポンス**
- 成功時: 200 OK
```json
{
    "topic": "猫",
    "model": "gemma3:4b",
    "script": [
        {
            "role": "boke",
            "text": "こんにちは！"
        },
        {
            "role": "tsukkomi",
            "text": "どうも！"
        }
    ]
}
```

### 2. 音声合成 API

#### POST /synthesize

台本から音声を生成します。

**リクエスト**
- Content-Type: `application/json`

```json
{
    "script": [
        {
            "speaker": "ツッコミ",
            "text": "こんにちは",
            "speaker_id": 1
        }
    ]
}
```

**レスポンス**
- 成功時: 200 OK
```json
{
    "audio_file": "generated_123.wav"
}
```

### 3. モデル管理 API

#### POST /models/register

新しいモデルを登録します。

**リクエスト**
- Content-Type: `multipart/form-data`
- フォームフィールド:
  - `name`: モデル名
  - `description`: モデルの説明
  - `model_file`: モデルファイル
  - `thumbnail`: サムネイル画像（オプショナル）

**レスポンス**
- 成功時: 201 Created
```json
{
    "model_id": "model_123",
    "message": "Model registered successfully"
}
```

#### GET /models

利用可能なモデル一覧を取得します。

**レスポンス**
- 成功時: 200 OK
```json
{
    "models": [
        {
            "name": "gemma3:4b",
            "modified_at": 1647532800,
            "size": 4000000000
        }
    ]
}
```

### 4. 話者管理 API

#### GET /speakers

利用可能な話者一覧を取得します。

**レスポンス**
- 成功時: 200 OK
```json
{
    "speakers": [
        {
            "name": "四国めたん",
            "styles": [
                {
                    "id": 2,
                    "name": "ノーマル"
                }
            ]
        }
    ]
}
```

### 5. プロンプト管理 API

#### GET /prompts

利用可能なプロンプト一覧を取得します。

**レスポンス**
- 成功時: 200 OK
```json
{
    "prompts": [
        {
            "id": "prompt1",
            "name": "ベーシックマンザイ",
            "description": "基本的なマンザイ生成プロンプト"
        }
    ]
}
```

#### POST /prompts

新しいプロンプトを作成します。

**リクエスト**
- Content-Type: `application/json`

```json
{
    "name": "新しいプロンプト",
    "description": "説明",
    "template": "プロンプトテンプレート"
}
```

**レスポンス**
- 成功時: 201 Created
```json
{
    "id": "new_prompt_id",
    "name": "新しいプロンプト",
    "message": "Prompt created successfully"
}
``` 