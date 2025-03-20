"""Test data models."""
import pytest
from pydantic import ValidationError
from src.backend.app.models.script import (
    Role,
    ScriptLine,
    ManzaiScript,
    GenerateScriptRequest,
    AudioMetadata,
    GenerateScriptResponse
)

def test_role_enum():
    """Test Role enum values."""
    assert Role.TSUKKOMI.value == "tsukkomi"
    assert Role.BOKE.value == "boke"

def test_script_line_valid():
    """Test valid ScriptLine creation."""
    line = ScriptLine(role=Role.TSUKKOMI, text="こんにちは")
    assert line.role == Role.TSUKKOMI
    assert line.text == "こんにちは"

def test_script_line_empty_text():
    """Test ScriptLine with empty text."""
    with pytest.raises(ValidationError) as exc_info:
        ScriptLine(role=Role.TSUKKOMI, text="")
    assert "セリフの内容は空にできません" in str(exc_info.value)

def test_manzai_script_valid():
    """Test valid ManzaiScript creation."""
    script = ManzaiScript(
        script=[
            ScriptLine(role=Role.TSUKKOMI, text="こんにちは"),
            ScriptLine(role=Role.BOKE, text="どうも")
        ],
        topic="挨拶"
    )
    assert len(script.script) == 2
    assert script.topic == "挨拶"

def test_manzai_script_empty():
    """Test ManzaiScript with empty script."""
    with pytest.raises(ValidationError) as exc_info:
        ManzaiScript(script=[], topic="テスト")
    assert "スクリプトは少なくとも1行必要です" in str(exc_info.value)

def test_generate_script_request_valid():
    """Test valid GenerateScriptRequest creation."""
    request = GenerateScriptRequest(topic="テスト", model="llama3")
    assert request.topic == "テスト"
    assert request.model == "llama3"
    assert not request.use_mock

def test_generate_script_request_empty_topic():
    """Test GenerateScriptRequest with empty topic."""
    with pytest.raises(ValidationError) as exc_info:
        GenerateScriptRequest(topic="", model="llama3")
    assert "トピックは空にできません" in str(exc_info.value)

def test_audio_metadata_valid():
    """Test valid AudioMetadata creation."""
    metadata = AudioMetadata(
        filename="test.wav",
        duration=1.5,
        line_index=0
    )
    assert metadata.filename == "test.wav"
    assert metadata.duration == 1.5
    assert metadata.line_index == 0

def test_generate_script_response_valid():
    """Test valid GenerateScriptResponse creation."""
    response = GenerateScriptResponse(
        topic="テスト",
        model="llama3",
        script=[
            ScriptLine(role=Role.TSUKKOMI, text="こんにちは"),
            ScriptLine(role=Role.BOKE, text="どうも")
        ],
        audio_data=[
            AudioMetadata(filename="test.wav", duration=1.5, line_index=0)
        ]
    )
    assert response.topic == "テスト"
    assert len(response.script) == 2
    assert len(response.audio_data) == 1
    assert response.error is None 