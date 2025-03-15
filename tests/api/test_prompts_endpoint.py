"""
プロンプト関連APIのテストモジュール
"""
import json
import pytest
from unittest.mock import patch, MagicMock

from tests.utils.test_helpers import app, client

@pytest.fixture
def mock_prompt_loader():
    """
    モックプロンプトローダーを提供するフィクスチャ
    """
    with patch('src.app.prompt_loader') as mock_loader:
        mock_instance = MagicMock()
        mock_loader.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def sample_prompts():
    """
    サンプルプロンプトデータを提供するフィクスチャ
    """
    return [
        {
            "id": "prompt1",
            "name": "ベーシックマンザイ",
            "description": "基本的なマンザイ生成プロンプト",
            "template": "あなたは漫才師です。{{topic}}についての漫才を書いてください。"
        },
        {
            "id": "prompt2",
            "name": "詳細設定マンザイ",
            "description": "詳細設定付きのマンザイ生成プロンプト",
            "template": "あなたは漫才師です。{{topic}}について、{{style}}スタイルの漫才を書いてください。"
        }
    ]

def test_get_prompts_success(client, mock_prompt_loader, sample_prompts):
    """
    プロンプト一覧取得APIの成功ケースをテスト
    
    Args:
        client: テスト用クライアント
        mock_prompt_loader: モックプロンプトローダー
        sample_prompts: サンプルプロンプトデータ
    """
    # モックの設定
    mock_prompt_loader.get_all_prompts.return_value = sample_prompts
    
    # テスト実行
    response = client.get('/api/prompts')
    
    # レスポンスの検証
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "prompts" in data
    assert data["prompts"] == sample_prompts
    
    # モックサービスの呼び出し検証
    mock_prompt_loader.get_all_prompts.assert_called_once()

def test_get_prompts_service_error(client, mock_prompt_loader):
    """
    サービスエラー発生時のプロンプト一覧取得APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_prompt_loader: モックプロンプトローダー
    """
    # モックにエラーを設定
    mock_prompt_loader.get_all_prompts.side_effect = Exception("読み込みエラー")
    
    # テスト実行
    response = client.get('/api/prompts')
    
    # レスポンスの検証
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data

def test_get_prompt_by_id_success(client, mock_prompt_loader, sample_prompts):
    """
    特定のプロンプト取得APIの成功ケースをテスト
    
    Args:
        client: テスト用クライアント
        mock_prompt_loader: モックプロンプトローダー
        sample_prompts: サンプルプロンプトデータ
    """
    # モックの設定
    prompt_id = "prompt1"
    mock_prompt_loader.get_prompt_by_id.return_value = sample_prompts[0]
    
    # テスト実行
    response = client.get(f'/api/prompts/{prompt_id}')
    
    # レスポンスの検証
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "prompt" in data
    assert data["prompt"] == sample_prompts[0]
    
    # モックサービスの呼び出し検証
    mock_prompt_loader.get_prompt_by_id.assert_called_once_with(prompt_id)

def test_get_prompt_by_id_not_found(client, mock_prompt_loader):
    """
    存在しないプロンプトIDでの取得APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_prompt_loader: モックプロンプトローダー
    """
    # モックの設定
    prompt_id = "nonexistent_id"
    mock_prompt_loader.get_prompt_by_id.return_value = None
    
    # テスト実行
    response = client.get(f'/api/prompts/{prompt_id}')
    
    # レスポンスの検証
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data
    
    # モックサービスの呼び出し検証
    mock_prompt_loader.get_prompt_by_id.assert_called_once_with(prompt_id)

def test_create_prompt_success(client, mock_prompt_loader, sample_prompts):
    """
    プロンプト作成APIの成功ケースをテスト
    
    Args:
        client: テスト用クライアント
        mock_prompt_loader: モックプロンプトローダー
        sample_prompts: サンプルプロンプトデータ
    """
    # 新しいプロンプトデータ
    new_prompt = {
        "name": "新しいプロンプト",
        "description": "テスト用の新しいプロンプト",
        "template": "あなたは漫才師です。{{topic}}について面白い漫才を書いてください。"
    }
    
    # 作成後のレスポンス
    created_prompt = {
        "id": "new_prompt_id",
        "name": new_prompt["name"],
        "description": new_prompt["description"],
        "template": new_prompt["template"]
    }
    
    # モックの設定
    mock_prompt_loader.create_prompt.return_value = created_prompt
    
    # テスト実行
    response = client.post('/api/prompts',
                          data=json.dumps(new_prompt),
                          content_type='application/json')
    
    # レスポンスの検証
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "prompt" in data
    assert data["prompt"] == created_prompt
    
    # モックサービスの呼び出し検証
    mock_prompt_loader.create_prompt.assert_called_once()

def test_create_prompt_invalid_data(client, mock_prompt_loader):
    """
    無効なデータでのプロンプト作成APIをテスト
    
    Args:
        client: テスト用クライアント
        mock_prompt_loader: モックプロンプトローダー
    """
    # 不完全なプロンプトデータ
    invalid_prompt = {
        "name": "不完全なプロンプト"
        # template が欠けている
    }
    
    # テスト実行
    response = client.post('/api/prompts',
                          data=json.dumps(invalid_prompt),
                          content_type='application/json')
    
    # レスポンスの検証
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    
    # モックサービスが呼び出されていないことを検証
    mock_prompt_loader.create_prompt.assert_not_called() 