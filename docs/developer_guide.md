# 開発者ガイド

## Content-Type要件

### 概要

ManzAI Studio APIでは、各エンドポイントで適切なContent-Typeヘッダーの使用が必須です。
これにより、リクエストデータの形式を正確に解釈し、適切な処理を行うことができます。

### サポートされるContent-Type

1. **application/json**
   - JSON形式のデータを送信する場合に使用
   - 主にAPIリクエストボディにJSONデータを含む場合

2. **multipart/form-data**
   - ファイルアップロードを含むリクエストで使用
   - フォームデータと共にファイルを送信する場合

### エンドポイントごとの要件

#### JSONリクエスト

以下のエンドポイントでは`application/json`を使用します：

```python
# 台本生成API
POST /api/generate-script
Content-Type: application/json

{
    "topic": "猫",
    "model": "gemma3:4b"
}

# 音声合成API
POST /api/synthesize
Content-Type: application/json

{
    "script": [
        {
            "speaker": "ツッコミ",
            "text": "こんにちは",
            "speaker_id": 1
        }
    ]
}

# プロンプト作成API
POST /api/prompts
Content-Type: application/json

{
    "name": "新しいプロンプト",
    "description": "説明",
    "template": "テンプレート"
}
```

#### マルチパートフォームデータ

以下のエンドポイントでは`multipart/form-data`を使用します：

```python
# モデル登録API
POST /api/models/register
Content-Type: multipart/form-data

- name: モデル名
- description: モデルの説明
- model_file: モデルファイル
- thumbnail: サムネイル画像（オプショナル）
```

### 実装例

#### クライアント側

```python
# JSONリクエストの例
import requests

def generate_script(topic: str):
    response = requests.post(
        "http://localhost:5000/api/generate-script",
        json={"topic": topic},
        headers={"Content-Type": "application/json"}
    )
    return response.json()

# ファイルアップロードの例
def register_model(name: str, description: str, model_file: str):
    files = {
        'model_file': open(model_file, 'rb')
    }
    data = {
        'name': name,
        'description': description
    }
    response = requests.post(
        "http://localhost:5000/api/models/register",
        files=files,
        data=data
    )
    return response.json()
```

#### サーバー側

```python
from flask import request, jsonify

@app.before_request
def validate_content_type():
    """リクエストのContent-Typeを検証"""
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type', '')
        
        # ファイルアップロードエンドポイントの場合
        if request.path.startswith('/api/models/'):
            if not content_type.startswith('multipart/form-data'):
                raise ContentTypeError("Multipart form data required for file upload")
        # その他のAPIエンドポイントの場合
        elif not request.is_json:
            raise ContentTypeError("JSON data required")
```

### エラーハンドリング

不適切なContent-Typeが使用された場合、以下のエラーレスポンスが返されます：

```json
{
    "error": "Unsupported Media Type",
    "code": "API_ERROR_415",
    "details": {
        "expected": "application/json",
        "received": "text/plain"
    }
}
```

### テスト

Content-Type要件のテスト例：

```python
def test_generate_endpoint_with_wrong_content_type(client):
    """誤ったContent-Typeでリクエストした場合にAPIが適切に処理することを確認"""
    response = client.post('/api/generate',
                          data='{"topic":"テスト"}',
                          content_type='text/plain')
    assert response.status_code == 415
    data = json.loads(response.data)
    assert "error" in data
```

### 注意事項

1. **Content-Typeの正確な指定**
   - 大文字小文字を区別しない
   - パラメータ（charset等）は省略可能

2. **ファイルアップロード時の注意**
   - `multipart/form-data`使用時はboundaryパラメータが自動的に設定される
   - ファイルサイズ制限に注意

3. **セキュリティ考慮**
   - Content-Typeヘッダーの偽装に注意
   - 適切なバリデーションの実施

4. **デバッグ**
   - 開発ツールでリクエストヘッダーを確認
   - エラーレスポンスの詳細を確認 