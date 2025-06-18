"""Test the AudioManager functionality."""

import os
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from src.backend.app.models.audio import AudioFile
from src.backend.app.utils.audio_manager import AudioManager


@pytest.fixture
def temp_audio_dir(tmpdir):
    """Create a temporary directory for audio files."""
    audio_dir = Path(tmpdir) / "audio"
    audio_dir.mkdir(exist_ok=True)
    return str(audio_dir)


@pytest.fixture
def audio_manager(temp_audio_dir):
    """Create an AudioManager instance with a temporary directory."""
    return AudioManager(audio_dir=temp_audio_dir)


def test_init_creates_directory():
    """Test that the constructor creates the audio directory if it doesn't exist."""
    with patch("os.makedirs") as mock_makedirs:
        AudioManager(audio_dir="nonexistent_dir")
        mock_makedirs.assert_called_once_with("nonexistent_dir", exist_ok=True)


def test_save_audio(audio_manager, temp_audio_dir):
    """Test saving audio data to a file."""
    test_data = b"test audio data"
    test_filename = "test.wav"

    # Mock the open function to avoid actually writing a file
    with patch("builtins.open", mock_open()) as mock_file:
        result = audio_manager.save_audio(test_data, test_filename)

        # Check that the file was opened for writing
        mock_file.assert_called_once()
        # Get the call arguments and check the path
        args, _kwargs = mock_file.call_args
        file_path = args[0]
        assert os.path.dirname(file_path) == temp_audio_dir
        assert file_path.endswith(".wav")
        assert os.path.basename(file_path).startswith(datetime.now().strftime("%Y%m%d_"))

        # Check that the data was written
        mock_file().write.assert_called_once_with(test_data)

        # Check the return value
        assert isinstance(result, str)
        assert result.endswith(".wav")


def test_save_audio_invalid_data(audio_manager):
    """Test save_audio with invalid data."""
    with pytest.raises(ValueError, match="音声データがありません"):
        audio_manager.save_audio(None, "test.wav")


def test_save_audio_empty_filename(audio_manager):
    """Test save_audio with empty filename."""
    with pytest.raises(ValueError, match="ファイル名が無効です"):
        audio_manager.save_audio(b"test data", "")


def test_get_audio_success(audio_manager, temp_audio_dir):
    """Test getting audio data from a file."""
    # Create a test file
    test_data = b"test audio data"
    test_filename = "test.wav"
    test_path = os.path.join(temp_audio_dir, test_filename)

    with open(test_path, "wb") as f:
        f.write(test_data)

    # Test reading the file
    result = audio_manager.get_audio(test_filename)
    assert result == test_data


def test_get_audio_adds_wav_extension(audio_manager, temp_audio_dir):
    """Test that get_audio adds .wav extension if not present."""
    # Create a test file
    test_data = b"test audio data"
    test_filename = "test.wav"
    test_path = os.path.join(temp_audio_dir, test_filename)

    with open(test_path, "wb") as f:
        f.write(test_data)

    # Test reading the file without .wav extension
    result = audio_manager.get_audio("test")
    assert result == test_data


def test_get_audio_not_found(audio_manager):
    """Test get_audio with non-existent file."""
    with pytest.raises(FileNotFoundError):
        audio_manager.get_audio("nonexistent.wav")


def test_list_audio_files(audio_manager, temp_audio_dir):
    """Test listing available audio files."""
    # Create test files
    test_files = ["test1.wav", "test2.wav", "test3.wav"]

    # Use different creation times
    for i, filename in enumerate(test_files):
        file_path = os.path.join(temp_audio_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"test")
        # Set modification time with 1-second intervals
        os.utime(file_path, (time.time(), time.time() - i))

    # Test listing files
    result = audio_manager.list_audio_files()

    # Check results
    assert len(result) == 3
    assert all(isinstance(item, AudioFile) for item in result)

    # Files should be sorted by creation time (newest first)
    assert os.path.basename(result[0].path) == "test1.wav"
    assert os.path.basename(result[1].path) == "test2.wav"
    assert os.path.basename(result[2].path) == "test3.wav"


def test_list_audio_files_empty_dir(audio_manager):
    """Test listing audio files in an empty directory."""
    result = audio_manager.list_audio_files()
    assert isinstance(result, list)
    assert len(result) == 0


def test_cleanup_old_files(audio_manager, temp_audio_dir):
    """Test cleaning up old audio files."""
    # Create test files
    test_files = [f"test{i}.wav" for i in range(15)]

    for i, filename in enumerate(test_files):
        file_path = os.path.join(temp_audio_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"test")
        # Set modification time with 1-second intervals
        os.utime(file_path, (time.time(), time.time() - i))

    # Patch os.remove to avoid actually deleting files
    with patch("os.remove") as mock_remove:
        # Keep 10 files, delete 5
        deleted = audio_manager.cleanup_old_files(max_files=10)

        # Check that the correct number of files were "deleted"
        assert deleted == 5
        assert mock_remove.call_count == 5

        # Check that the oldest files were deleted
        deleted_paths = [call_args[0][0] for call_args in mock_remove.call_args_list]
        for i in range(10, 15):
            assert any(f"test{i}.wav" in path for path in deleted_paths)


def test_cleanup_old_files_fewer_than_max(audio_manager, temp_audio_dir):
    """Test cleanup when there are fewer files than the max."""
    # Create test files
    test_files = [f"test{i}.wav" for i in range(5)]

    for filename in test_files:
        file_path = os.path.join(temp_audio_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"test")

    # Patch os.remove to avoid actually deleting files
    with patch("os.remove") as mock_remove:
        # Set max_files higher than the number of files
        deleted = audio_manager.cleanup_old_files(max_files=10)

        # Should not delete any files
        assert deleted == 0
        mock_remove.assert_not_called()


def test_cleanup_old_files_error_handling(audio_manager, temp_audio_dir):
    """Test error handling during cleanup."""
    # Create test files
    test_files = [f"test{i}.wav" for i in range(15)]

    for i, filename in enumerate(test_files):
        file_path = os.path.join(temp_audio_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"test")
        # Set modification time with 1-second intervals
        os.utime(file_path, (time.time(), time.time() - i))

    # Patch os.remove to raise an exception
    with (
        patch("os.remove", side_effect=OSError("Test error")),
        patch("builtins.print") as mock_print,
    ):
        # Try to delete files
        deleted = audio_manager.cleanup_old_files(max_files=10)

        # Should attempt to delete 5 files but all fail
        assert deleted == 0
        assert mock_print.call_count == 5


def test_get_audio_file_path(audio_manager, temp_audio_dir):
    """Test getting the full path for an audio file."""
    assert audio_manager.get_audio_file_path("test.wav") == os.path.join(temp_audio_dir, "test.wav")


def test_get_audio_url(audio_manager):
    """Test getting the API URL for an audio file."""
    assert audio_manager.get_audio_url("test.wav") == "/audio/test.wav"


def test_generate_filename(audio_manager):
    """Test filename generation."""
    filename = audio_manager.generate_filename()
    assert filename.endswith(".wav")
    assert datetime.now().strftime("%Y%m%d") in filename
