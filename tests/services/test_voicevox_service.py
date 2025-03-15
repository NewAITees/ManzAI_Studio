import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
import requests
from src.services.voicevox_service import VoiceVoxService, VoiceVoxServiceError

@pytest.fixture
def voicevox_service():
    """テスト用のVoiceVoxServiceインスタンスを作成"""
    return VoiceVoxService()

def test_generate_voice_returns_audio_data(voicevox_service):
    """VoiceVoxサービスが有効な音声データを返すことを確認"""
    mock_audio_data = b'test audio data'
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.content = mock_audio_data
        mock_post.return_value.status_code = 200
        
        audio_data = voicevox_service.generate_voice("こんにちは", speaker_id=1)
        
        assert audio_data is not None
        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0
        assert audio_data == mock_audio_data

def test_get_timing_data_returns_valid_structure(voicevox_service):
    """VoiceVoxサービスが有効なタイミングデータを返すことを確認"""
    mock_response = {
        'accent_phrases': [
            {
                'moras': [
                    {'text': 'こ', 'start_time': 0.0, 'end_time': 0.1},
                    {'text': 'ん', 'start_time': 0.1, 'end_time': 0.2},
                    {'text': 'に', 'start_time': 0.2, 'end_time': 0.3},
                    {'text': 'ち', 'start_time': 0.3, 'end_time': 0.4},
                    {'text': 'は', 'start_time': 0.4, 'end_time': 0.5}
                ]
            }
        ]
    }
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200
        
        timing = voicevox_service.get_timing_data("こんにちは", speaker_id=1)
        
        assert isinstance(timing, dict)
        assert 'accent_phrases' in timing
        assert len(timing['accent_phrases']) > 0
        
        for accent in timing['accent_phrases']:
            assert 'moras' in accent
            for mora in accent['moras']:
                assert 'text' in mora
                assert 'start_time' in mora
                assert 'end_time' in mora
                assert isinstance(mora['start_time'], float)
                assert isinstance(mora['end_time'], float)

def test_generate_voice_handles_connection_error(voicevox_service):
    """VoiceVoxサービスが接続エラーを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = ConnectionError()
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.generate_voice("テスト", speaker_id=1)
        
        assert "connection error" in str(exc_info.value).lower()

def test_generate_voice_handles_invalid_response(voicevox_service):
    """VoiceVoxサービスが不正なレスポンスを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {'error': 'Internal Server Error'}
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.generate_voice("テスト", speaker_id=1)
        
        assert "invalid response" in str(exc_info.value).lower()

def test_generate_voice_handles_empty_text(voicevox_service):
    """VoiceVoxサービスが空のテキストを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        voicevox_service.generate_voice("", speaker_id=1)
    
    assert "text cannot be empty" in str(exc_info.value).lower()

def test_generate_voice_handles_invalid_speaker_id(voicevox_service):
    """VoiceVoxサービスが不正なスピーカーIDを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        voicevox_service.generate_voice("テスト", speaker_id=-1)
    
    assert "invalid speaker id" in str(exc_info.value).lower()

def test_generate_voice_with_valid_params(voicevox_service):
    """VoiceVoxServiceが有効なパラメータで音声を生成することを確認"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'audio content'
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = mock_response
        
        # メソッドを呼び出し
        result = voicevox_service.generate_voice("こんにちは", 1)
        
        # テスト
        assert isinstance(result, bytes)
        assert result == b'audio content'
        
        # リクエスト内容を確認
        calls = mock_post.call_args_list
        assert len(calls) == 2  # クエリと合成の2回呼ばれる
        assert "/audio_query" in str(calls[0])
        assert "/synthesis" in str(calls[1])

def test_generate_voice_empty_text(voicevox_service):
    """VoiceVoxServiceが空のテキストを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        voicevox_service.generate_voice("", 1)
    
    assert "text cannot be empty" in str(exc_info.value)

def test_get_timing_data_with_valid_params(voicevox_service):
    """VoiceVoxServiceが有効なパラメータでタイミングデータを取得することを確認"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"moras": [{"text": "こ", "start": 0.0, "end": 0.1}]}
    ]
    
    with patch('requests.post') as mock_post:
        mock_post.return_value = mock_response
        
        # メソッドを呼び出し
        result = voicevox_service.get_timing_data("こんにちは", 1)
        
        # テスト
        assert isinstance(result, list)
        assert len(result) == 1
        assert "moras" in result[0]
        
        # リクエスト内容を確認
        mock_post.assert_called_once()
        assert "/accent_phrases" in str(mock_post.call_args)

def test_synthesize_voice_with_valid_params(voicevox_service):
    """VoiceVoxServiceがテキストから音声を合成し、ファイルに保存することを確認"""
    mock_query_response = MagicMock()
    mock_query_response.status_code = 200
    mock_query_response.json.return_value = {"accent_phrases": []}
    
    mock_synthesis_response = MagicMock()
    mock_synthesis_response.status_code = 200
    mock_synthesis_response.content = b'audio content'
    
    with patch('requests.post') as mock_post, \
         patch('builtins.open', new_callable=mock_open) as mock_file, \
         patch('time.time', return_value=12345):
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        # メソッドを呼び出し
        file_path, timing_data = voicevox_service.synthesize_voice("こんにちは", 1)
        
        # テスト
        assert "12345_1.wav" in file_path
        assert timing_data == {"accent_phrases": []}
        
        # ファイル書き込みを確認
        mock_file.assert_called_once()
        mock_file().write.assert_called_once_with(b'audio content')

def test_get_speakers(voicevox_service):
    """VoiceVoxServiceが話者一覧を取得することを確認"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {
            "name": "ずんだもん",
            "styles": [
                {"id": 1, "name": "ノーマル"},
                {"id": 2, "name": "あまあま"}
            ]
        },
        {
            "name": "四国めたん",
            "styles": [
                {"id": 3, "name": "ノーマル"}
            ]
        }
    ]
    
    with patch('requests.get') as mock_get:
        mock_get.return_value = mock_response
        
        # メソッドを呼び出し
        result = voicevox_service.get_speakers()
        
        # テスト
        assert isinstance(result, list)
        assert len(result) == 3  # 3つのスタイルがある
        
        # 簡略化されたリストを確認
        assert result[0]["id"] == 1
        assert "ずんだもん" in result[0]["name"]
        assert "ノーマル" in result[0]["name"]
        
        assert result[2]["id"] == 3
        assert "四国めたん" in result[2]["name"]
        
        # リクエスト内容を確認
        mock_get.assert_called_once()
        assert "/speakers" in str(mock_get.call_args)

def test_init_with_custom_params():
    """カスタムパラメータでVoiceVoxServiceが初期化されることを確認"""
    service = VoiceVoxService("http://custom-url")
    assert service.base_url == "http://custom-url"

def test_get_speakers_success(voicevox_service):
    """話者リスト取得が成功した場合のテスト"""
    mock_speakers = [
        {"name": "四国めたん", "styles": [{"id": 2, "name": "ノーマル"}]},
        {"name": "ずんだもん", "styles": [{"id": 3, "name": "ノーマル"}]}
    ]
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_speakers
        mock_get.return_value = mock_response
        
        result = voicevox_service.get_speakers()
        
        mock_get.assert_called_once_with(f"{voicevox_service.base_url}/speakers")
        assert result == mock_speakers

def test_get_speakers_connection_error(voicevox_service):
    """話者リスト取得時に接続エラーが発生した場合のテスト"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.get_speakers()
        
        assert "connection error" in str(exc_info.value).lower()
        assert "failed to connect to voicevox service" in str(exc_info.value).lower()

def test_get_speakers_invalid_response(voicevox_service):
    """話者リスト取得時にAPIが不正なレスポンスを返した場合のテスト"""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.get_speakers()
        
        assert "invalid response" in str(exc_info.value).lower()

def test_synthesize_success(voicevox_service):
    """音声合成が成功した場合のテスト"""
    test_text = "こんにちは"
    test_speaker_id = 1
    mock_audio_content = b'audio_data'
    
    with patch('requests.post') as mock_post:
        # audio_query のモック
        mock_query_response = MagicMock()
        mock_query_response.status_code = 200
        mock_query_response.json.return_value = {"mock": "query_data"}
        
        # synthesis のモック
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.status_code = 200
        mock_synthesis_response.content = mock_audio_content
        
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        result = voicevox_service.synthesize(test_text, test_speaker_id)
        
        assert mock_post.call_count == 2
        assert result == mock_audio_content

def test_synthesize_query_connection_error(voicevox_service):
    """audio_query実行時に接続エラーが発生した場合のテスト"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.synthesize("テスト", 1)
        
        assert "connection error" in str(exc_info.value).lower()
        assert "failed to connect to voicevox service" in str(exc_info.value).lower()

def test_synthesize_query_invalid_response(voicevox_service):
    """audio_query実行時にAPIが不正なレスポンスを返した場合のテスト"""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.synthesize("テスト", 1)
        
        assert "invalid response" in str(exc_info.value).lower()

def test_synthesize_synthesis_connection_error(voicevox_service):
    """synthesis実行時に接続エラーが発生した場合のテスト"""
    with patch('requests.post') as mock_post:
        # audio_query のモック
        mock_query_response = MagicMock()
        mock_query_response.status_code = 200
        mock_query_response.json.return_value = {"mock": "query_data"}
        
        # synthesis で接続エラー
        mock_post.side_effect = [mock_query_response, requests.exceptions.ConnectionError()]
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.synthesize("テスト", 1)
        
        assert "connection error" in str(exc_info.value).lower()
        assert "failed to connect to voicevox service" in str(exc_info.value).lower()

def test_synthesize_synthesis_invalid_response(voicevox_service):
    """synthesis実行時にAPIが不正なレスポンスを返した場合のテスト"""
    with patch('requests.post') as mock_post:
        # audio_query のモック
        mock_query_response = MagicMock()
        mock_query_response.status_code = 200
        mock_query_response.json.return_value = {"mock": "query_data"}
        
        # synthesis で不正なレスポンス
        mock_synthesis_response = MagicMock()
        mock_synthesis_response.status_code = 500
        
        mock_post.side_effect = [mock_query_response, mock_synthesis_response]
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.synthesize("テスト", 1)
        
        assert "invalid response" in str(exc_info.value).lower() 