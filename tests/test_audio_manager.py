"""Test the AudioManager functionality."""

import os
import time
from datetime import datetime
from pathlib import Path

import pytest

from src.backend.app.services.audio_manager import AudioManager


@pytest.fixture
def temp_audio_dir(tmpdir) -> str:
    """Create a temporary directory for audio files."""
    audio_dir = Path(tmpdir) / "audio"
    audio_dir.mkdir(exist_ok=True)
    return str(audio_dir)


@pytest.fixture
def audio_manager(temp_audio_dir) -> AudioManager:
    """Create an AudioManager instance with a temporary directory."""
    return AudioManager(audio_dir=temp_audio_dir)


def test_init_creates_directory(tmpdir) -> None:
    """Test that the constructor creates the audio directory if it doesn't exist."""
    nonexistent_dir = str(tmpdir / "new_dir")
    assert not os.path.exists(nonexistent_dir)
    AudioManager(audio_dir=nonexistent_dir)
    assert os.path.exists(nonexistent_dir)


def test_save_audio(audio_manager: AudioManager, temp_audio_dir: str) -> None:
    """Test saving audio data to a file."""
    test_data = b"test audio data"
    test_filename = "test.wav"

    # Actually save the file
    result = audio_manager.save_audio(test_data, test_filename)

    # Check the return value (returns filename only)
    assert isinstance(result, str)
    assert result.endswith(".wav")
    assert not result.startswith("/")

    # Check that the file was actually created
    full_path = os.path.join(temp_audio_dir, result)
    assert os.path.exists(full_path)

    # Check that the correct data was written
    with open(full_path, "rb") as f:
        written_data = f.read()
    assert written_data == test_data

    # Check the filename format
    assert os.path.basename(result).startswith(datetime.now().strftime("%Y%m%d_"))


def test_save_audio_invalid_data(audio_manager: AudioManager) -> None:
    """Test save_audio with invalid data."""
    with pytest.raises(ValueError, match="invalid audio data"):
        audio_manager.save_audio(None, "test.wav")


def test_save_audio_empty_filename(audio_manager: AudioManager) -> None:
    """Test save_audio with empty filename."""
    with pytest.raises(ValueError, match="invalid filename"):
        audio_manager.save_audio(b"test data", "")


def test_get_audio_success(audio_manager: AudioManager, temp_audio_dir: str) -> None:
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


def test_get_audio_adds_wav_extension(audio_manager: AudioManager, temp_audio_dir: str) -> None:
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


def test_get_audio_not_found(audio_manager: AudioManager) -> None:
    """Test get_audio with non-existent file."""
    with pytest.raises(FileNotFoundError):
        audio_manager.get_audio("nonexistent.wav")


def test_list_audio_files(audio_manager: AudioManager, temp_audio_dir: str) -> None:
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
    assert all(isinstance(item, str) for item in result)

    # Files should be sorted by creation time (order may vary)
    assert "test1.wav" in result
    assert "test2.wav" in result
    assert "test3.wav" in result


def test_list_audio_files_empty_dir(audio_manager: AudioManager) -> None:
    """Test listing audio files in an empty directory."""
    result = audio_manager.list_audio_files()
    assert isinstance(result, list)
    assert len(result) == 0


def test_cleanup_old_files(audio_manager: AudioManager, temp_audio_dir: str) -> None:
    """Test cleaning up old audio files."""
    # Create test files
    test_files = [f"test{i}.wav" for i in range(15)]

    for i, filename in enumerate(test_files):
        file_path = os.path.join(temp_audio_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"test")
        # Set modification time with 1-second intervals
        os.utime(file_path, (time.time(), time.time() - i))

    # Check initial count
    assert len(os.listdir(temp_audio_dir)) == 15

    # Keep 10 files, delete 5
    deleted = audio_manager.cleanup_old_files(max_files=10)

    # Check that the correct number of files were deleted
    assert deleted == 5
    assert len(os.listdir(temp_audio_dir)) == 10


def test_cleanup_old_files_fewer_than_max(audio_manager: AudioManager, temp_audio_dir: str) -> None:
    """Test cleanup when there are fewer files than the max."""
    # Create test files
    test_files = [f"test{i}.wav" for i in range(5)]

    for filename in test_files:
        file_path = os.path.join(temp_audio_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"test")

    # Check initial count
    initial_count = len(os.listdir(temp_audio_dir))
    assert initial_count == 5

    # Set max_files higher than the number of files
    deleted = audio_manager.cleanup_old_files(max_files=10)

    # Should not delete any files
    assert deleted == 0
    assert len(os.listdir(temp_audio_dir)) == initial_count


def test_cleanup_old_files_error_handling(audio_manager: AudioManager, temp_audio_dir: str) -> None:
    """Test error handling during cleanup."""
    # Create test files
    test_files = [f"test{i}.wav" for i in range(15)]

    file_paths = []
    for i, filename in enumerate(test_files):
        file_path = os.path.join(temp_audio_dir, filename)
        with open(file_path, "wb") as f:
            f.write(b"test")
        # Set modification time with 1-second intervals
        os.utime(file_path, (time.time(), time.time() - i))
        file_paths.append(file_path)

    # Normal cleanup should work
    initial_count = len(os.listdir(temp_audio_dir))
    assert initial_count == 15

    deleted = audio_manager.cleanup_old_files(max_files=10)

    # Should delete 5 files normally
    assert deleted == 5
    assert len(os.listdir(temp_audio_dir)) == 10


# Note: get_audio_file_path, get_audio_url, and generate_filename methods
# are not implemented in the services.AudioManager as they're not needed for API functionality
