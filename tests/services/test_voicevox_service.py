"""VoiceVoxサービスのテスト"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
import os
import json
import requests
from typing import Generator, Dict, Any, cast

from src.backend.app.services.voicevox_service import VoiceVoxService, VoiceVoxServiceError
from src.backend.app.models.audio import AudioSynthesisResult, SpeechTimingData

@pytest.fixture
def voicevox_service() -> VoiceVoxService:
    """テスト用のVoiceVoxServiceインスタンスを作成"""
    return VoiceVoxService()

def test_generate_voice_returns_audio_data(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxサービスが有効な音声データを返すことを確認"""
    mock_audio_data = b'test audio data'
    mock_query_response = {
        'accent_phrases': [
            {
                'moras': [
                    {'text': 'こ', 'consonant': 'k', 'consonant_length': 0.1, 'vowel': 'o', 'vowel_length': 0.2, 'pitch': 5.4}
                ],
                'accent': 1,
                'pause_mora': None,
                'is_interrogative': False
            }
        ],
        'speedScale': 1.0,
        'pitchScale': 1.0,
        'intonationScale': 1.0,
        'volumeScale': 1.0,
        'prePhonemeLength': 0.1,
        'postPhonemeLength': 0.1,
        'outputSamplingRate': 44100,
        'outputStereo': False,
        'kana': 'コンニチハ'
    }
    
    with patch('requests.post') as mock_post:
        # audio_queryのレスポンスを設定
        mock_query = MagicMock()
        mock_query.status_code = 200
        mock_query.json.return_value = mock_query_response
        
        # synthesisのレスポンスを設定
        mock_synthesis = MagicMock()
        mock_synthesis.status_code = 200
        mock_synthesis.content = mock_audio_data
        
        mock_post.side_effect = [mock_query, mock_synthesis]
        
        audio_data = voicevox_service.generate_voice("こんにちは", speaker_id=1)
        
        assert audio_data is not None
        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0
        assert audio_data == mock_audio_data

def test_get_timing_data_returns_valid_structure(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxサービスが有効なタイミングデータを返すことを確認"""
    mock_response = {
        'accent_phrases': [
            {
                'moras': [
                    {'text': 'こ', 'consonant': 'k', 'consonant_length': 0.1, 'vowel': 'o', 'vowel_length': 0.2, 'pitch': 5.4},
                    {'text': 'ん', 'consonant': '', 'consonant_length': 0.0, 'vowel': 'N', 'vowel_length': 0.2, 'pitch': 5.2},
                    {'text': 'に', 'consonant': 'n', 'consonant_length': 0.1, 'vowel': 'i', 'vowel_length': 0.2, 'pitch': 5.0},
                    {'text': 'ち', 'consonant': 'ch', 'consonant_length': 0.1, 'vowel': 'i', 'vowel_length': 0.2, 'pitch': 4.8},
                    {'text': 'は', 'consonant': 'h', 'consonant_length': 0.1, 'vowel': 'a', 'vowel_length': 0.2, 'pitch': 4.6}
                ],
                'accent': 1,
                'pause_mora': None,
                'is_interrogative': False
            }
        ],
        'speedScale': 1.0,
        'pitchScale': 1.0,
        'intonationScale': 1.0,
        'volumeScale': 1.0,
        'prePhonemeLength': 0.1,
        'postPhonemeLength': 0.1,
        'outputSamplingRate': 44100,
        'outputStereo': False,
        'kana': 'コンニチハ'
    }
    
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = mock_response
        mock_post.return_value.status_code = 200
        
        timing = voicevox_service.get_timing_data("こんにちは", speaker_id=1)
        
        assert isinstance(timing, dict)
        assert 'accent_phrases' in timing
        assert len(timing['accent_phrases']) == 1
        assert 'moras' in timing['accent_phrases'][0]
        assert len(timing['accent_phrases'][0]['moras']) == 5
        
        # タイミング情報を確認
        for mora in timing['accent_phrases'][0]['moras']:
            assert 'text' in mora
            assert 'consonant' in mora
            assert 'vowel' in mora
            assert 'consonant_length' in mora
            assert 'vowel_length' in mora
            assert isinstance(mora['consonant_length'], float)
            assert isinstance(mora['vowel_length'], float)

def test_generate_voice_handles_connection_error(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxサービスが接続エラーを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.generate_voice("テスト", speaker_id=1)
        
        assert "connection error with voicevox api" in str(exc_info.value).lower()

def test_generate_voice_handles_invalid_response(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxサービスが不正なレスポンスを適切に処理することを確認"""
    with patch('requests.post') as mock_post:
        mock_post.return_value.status_code = 500
        mock_post.return_value.json.return_value = {'error': 'Internal Server Error'}
        
        with pytest.raises(VoiceVoxServiceError) as exc_info:
            voicevox_service.generate_voice("テスト", speaker_id=1)
        
        assert "voicevox api returned error status: 500" in str(exc_info.value).lower()

def test_generate_voice_handles_empty_text(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxサービスが空のテキストを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        voicevox_service.generate_voice("", speaker_id=1)
    
    assert "text cannot be empty" in str(exc_info.value).lower()

def test_generate_voice_handles_invalid_speaker_id(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxサービスが不正なスピーカーIDを適切に処理することを確認"""
    with pytest.raises(ValueError) as exc_info:
        voicevox_service.generate_voice("テスト", speaker_id=-1)
    
    assert "invalid speaker id" in str(exc_info.value).lower()

def test_generate_voice_with_valid_params(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxServiceが有効なパラメータで音声を生成することを確認"""
    mock_audio_data = b'test audio data'
    mock_query_response = {'query': 'data'}
    
    with patch('requests.post') as mock_post:
        mock_query = MagicMock()
        mock_query.status_code = 200
        mock_query.json.return_value = mock_query_response
        
        mock_synthesis = MagicMock()
        mock_synthesis.status_code = 200
        mock_synthesis.content = mock_audio_data
        
        mock_post.side_effect = [mock_query, mock_synthesis]
        
        result = voicevox_service.generate_voice("テスト", speaker_id=1)
        
        assert result == mock_audio_data
        assert mock_post.call_count == 2

def test_get_timing_data_with_valid_params(voicevox_service: VoiceVoxService) -> None:
    """VoiceVoxServiceが有効なパラメータでタイミングデータを取得することを確認"""
    mock_response = {
        'accent_phrases': [
            {
                'moras': [
                    {'text': 'こ', 'consonant': 'k', 'consonant_length': 0.1, 'vowel': 'o', 'vowel_length': 0.2, 'pitch': 5.4},
                    {'text': 'ん', 'consonant': '', 'consonant_length': 0.0, 'vowel': 'N', 'vowel_length': 0.2, 'pitch': 5.2},
                    {'text': 'に', 'consonant': 'n', 'consonant_length': 0.1, 'vowel': 'i', 'vowel_length': 0.2, 'pitch': 5.0},
                    {'text': 'ち', 'consonant': 'ch', 'consonant_length': 0.1, 'vowel': 'i', 'vowel_length': 0.2, 'pitch': 4.8},
                    {'text': 'は', 'consonant': 'h', 'consonant_length': 0.1, 'vowel': 'a', 'vowel_length': 0.2, 'pitch': 4.6}
                ],
                'accent': 1,
                'pause_mora': None,
                'is_interrogative': False
            }
        ],
        'speedScale': 1.0,
        'pitchScale': 1.0,
        'intonationScale': 1.0,
        'volumeScale': 1.0,
        'prePhonemeLength': 0.1,
        'postPhonemeLength': 0.1,
        'outputSamplingRate': 44100,
        'outputStereo': False,
        'kana': 'コンニチハ'
    }
    
    with patch('requests.post') as mock_post:
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = mock_response
        mock_post.return_value = mock_response_obj
        
        result = voicevox_service.get_timing_data("こんにちは", speaker_id=1)
        
        assert isinstance(result, dict)
        assert 'accent_phrases' in result
        assert len(result['accent_phrases']) == 1
        assert 'moras' in result['accent_phrases'][0]
        assert len(result['accent_phrases'][0]['moras']) == 5
        
        for mora in result['accent_phrases'][0]['moras']:
            assert 'text' in mora
            assert 'consonant' in mora
            assert 'consonant_length' in mora
            assert 'vowel' in mora
            assert 'vowel_length' in mora
            assert 'pitch' in mora
            assert isinstance(mora['consonant_length'], float)
            assert isinstance(mora['vowel_length'], float)
            assert isinstance(mora['pitch'], float)
        
        mock_post.assert_called_once()
        assert "/audio_query" in str(mock_post.call_args)

def test_synthesize_voice_with_valid_params(voicevox_service):
    """VoiceVoxServiceがテキストから音声を合成し、ファイルに保存することを確認"""
    mock_query_response = {
        'accent_phrases': [
            {
                'moras': [
                    {'text': 'こ', 'consonant': 'k', 'consonant_length': 0.1, 'vowel': 'o', 'vowel_length': 0.2, 'pitch': 5.4},
                    {'text': 'ん', 'consonant': '', 'consonant_length': 0.0, 'vowel': 'N', 'vowel_length': 0.2, 'pitch': 5.2},
                    {'text': 'に', 'consonant': 'n', 'consonant_length': 0.1, 'vowel': 'i', 'vowel_length': 0.2, 'pitch': 5.0},
                    {'text': 'ち', 'consonant': 'ch', 'consonant_length': 0.1, 'vowel': 'i', 'vowel_length': 0.2, 'pitch': 4.8},
                    {'text': 'は', 'consonant': 'h', 'consonant_length': 0.1, 'vowel': 'a', 'vowel_length': 0.2, 'pitch': 4.6}
                ],
                'accent': 1,
                'pause_mora': None,
                'is_interrogative': False
            }
        ],
        'speedScale': 1.0,
        'pitchScale': 1.0,
        'intonationScale': 1.0,
        'volumeScale': 1.0,
        'prePhonemeLength': 0.1,
        'postPhonemeLength': 0.1,
        'outputSamplingRate': 44100,
        'outputStereo': False,
        'kana': 'コンニチハ'
    }
    
    mock_audio_data = b'test audio data'
    
    with patch('requests.post') as mock_post, \
         patch('builtins.open', new_callable=mock_open) as mock_file, \
         patch('time.time', return_value=12345), \
         patch('os.makedirs') as mock_makedirs:
        
        # audio_queryのレスポンスを設定（get_timing_dataとgenerate_voice用）
        mock_query1 = MagicMock()
        mock_query1.status_code = 200
        mock_query1.json.return_value = mock_query_response

        mock_query2 = MagicMock()
        mock_query2.status_code = 200
        mock_query2.json.return_value = mock_query_response
        
        # synthesisのレスポンスを設定（generate_voice用）
        mock_synthesis = MagicMock()
        mock_synthesis.status_code = 200
        mock_synthesis.content = mock_audio_data
        
        # side_effectを正しく設定（get_timing_data用のquery、generate_voice用のqueryとsynthesis）
        mock_post.side_effect = [mock_query1, mock_query2, mock_synthesis]
        
        # メソッドを呼び出し
        result = voicevox_service.synthesize_voice("こんにちは", speaker_id=1)
        
        # 結果を検証
        assert isinstance(result, AudioSynthesisResult)
        assert result.file_path.endswith('12345_1.wav')
        assert len(result.timing_data) == 5  # 5つのモーラ
        assert result.text == "こんにちは"
        assert result.speaker_id == 1
        assert result.duration > 0
        
        # タイミングデータを検証
        for timing in result.timing_data:
            assert isinstance(timing, SpeechTimingData)
            assert timing.start_time >= 0
            assert timing.end_time > timing.start_time
            assert timing.phoneme
            assert timing.text
        
        # ディレクトリ作成を確認
        mock_makedirs.assert_called_once_with(os.path.dirname(result.file_path), exist_ok=True)
        
        # ファイル書き込みを確認
        mock_file().write.assert_called_once_with(mock_audio_data)
        
        # APIコールを確認
        assert mock_post.call_count == 3  # get_timing_data用のquery、generate_voice用のqueryとsynthesis
        assert "/audio_query" in str(mock_post.call_args_list[0])  # get_timing_data
        assert "/audio_query" in str(mock_post.call_args_list[1])  # generate_voice
        assert "/synthesis" in str(mock_post.call_args_list[2])    # generate_voice

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
        assert len(result) == 2  # 2人の話者がいる
        
        # 話者情報を確認
        assert result[0]["name"] == "ずんだもん"
        assert len(result[0]["styles"]) == 2  # ずんだもんは2つのスタイルを持つ
        assert result[0]["styles"][0]["id"] == 1
        assert result[0]["styles"][0]["name"] == "ノーマル"
        assert result[0]["styles"][1]["id"] == 2
        assert result[0]["styles"][1]["name"] == "あまあま"
        
        assert result[1]["name"] == "四国めたん"
        assert len(result[1]["styles"]) == 1  # 四国めたんは1つのスタイルを持つ
        assert result[1]["styles"][0]["id"] == 3
        assert result[1]["styles"][0]["name"] == "ノーマル"
        
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
        
        assert "connection error with voicevox api" in str(exc_info.value).lower()

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
        
        assert "connection error with voicevox api" in str(exc_info.value).lower()

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
        
        assert "connection error with voicevox api" in str(exc_info.value).lower()

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
        
        assert "voicevox api returned error status: 500" in str(exc_info.value).lower() 