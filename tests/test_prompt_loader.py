"""Test the PromptLoader functionality."""

import json
import os
import uuid
from pathlib import Path
from unittest.mock import patch

import pytest

from src.backend.app.utils.prompt_loader import (
    PromptLoader,
    PromptTemplateNotFoundError,
)


@pytest.fixture
def temp_dirs(tmpdir):
    """Create temporary directories for prompts and templates."""
    prompts_dir = Path(tmpdir) / "prompts"
    templates_dir = Path(tmpdir) / "templates"
    prompts_dir.mkdir(exist_ok=True)
    templates_dir.mkdir(exist_ok=True)
    return str(prompts_dir), str(templates_dir)


@pytest.fixture
def prompt_loader(temp_dirs):
    """Create a PromptLoader instance with temporary directories."""
    prompts_dir, templates_dir = temp_dirs
    return PromptLoader(prompts_dir=prompts_dir, templates_dir=templates_dir)


def test_init_creates_directories():
    """Test that constructor creates directories if they don't exist."""
    with patch("os.makedirs") as mock_makedirs:
        PromptLoader(prompts_dir="nonexistent_dir1", templates_dir="nonexistent_dir2")
        assert mock_makedirs.call_count == 2
        mock_makedirs.assert_any_call("nonexistent_dir1", exist_ok=True)
        mock_makedirs.assert_any_call("nonexistent_dir2", exist_ok=True)


def test_get_all_prompts_empty(prompt_loader, temp_dirs):
    """Test getting all prompts from an empty directory."""
    _prompts_dir, _ = temp_dirs
    result = prompt_loader.get_all_prompts()
    assert isinstance(result, list)
    assert len(result) == 0


def test_get_all_prompts(prompt_loader, temp_dirs):
    """Test getting all prompts."""
    prompts_dir, _ = temp_dirs

    # Create test prompt files
    prompts = [
        {"id": "prompt1", "name": "Prompt 1", "template": "Template 1"},
        {"id": "prompt2", "name": "Prompt 2", "template": "Template 2"},
    ]

    for prompt in prompts:
        file_path = os.path.join(prompts_dir, f"{prompt['id']}.json")
        with open(file_path, "w") as f:
            json.dump(prompt, f)

    # Test getting prompts
    result = prompt_loader.get_all_prompts()

    # Check results
    assert len(result) == 2
    assert all(isinstance(item, dict) for item in result)

    # Check prompt content
    prompt_ids = [p["id"] for p in result]
    assert "prompt1" in prompt_ids
    assert "prompt2" in prompt_ids


def test_get_prompt_by_id_found(prompt_loader, temp_dirs):
    """Test getting a prompt by ID when it exists."""
    prompts_dir, _ = temp_dirs

    # Create test prompt file
    prompt = {"id": "test_prompt", "name": "Test Prompt", "template": "Test Template"}
    file_path = os.path.join(prompts_dir, "test_prompt.json")
    with open(file_path, "w") as f:
        json.dump(prompt, f)

    # Test getting the prompt
    result = prompt_loader.get_prompt_by_id("test_prompt")

    # Check result
    assert result is not None
    assert result["id"] == "test_prompt"
    assert result["name"] == "Test Prompt"
    assert result["template"] == "Test Template"


def test_get_prompt_by_id_not_found(prompt_loader):
    """Test getting a prompt by ID when it doesn't exist."""
    result = prompt_loader.get_prompt_by_id("nonexistent")
    assert result is None


def test_create_prompt(prompt_loader, temp_dirs):
    """Test creating a new prompt."""
    prompts_dir, _ = temp_dirs

    # Mock UUID generation for deterministic testing
    test_uuid = "123e4567-e89b-12d3-a456-426614174000"

    with patch("src.backend.app.utils.prompt_loader.uuid4", return_value=uuid.UUID(test_uuid)):
        # Test data
        prompt_data = {
            "name": "New Prompt",
            "description": "Test description",
            "template": "Test template with {{variable}}",
        }

        # Create the prompt
        result = prompt_loader.create_prompt(prompt_data)

        # Check result
        assert result is not None
        assert result["id"] == test_uuid
        assert result["name"] == "New Prompt"
        assert result["template"] == "Test template with {{variable}}"

        # Check that the file was created
        file_path = os.path.join(prompts_dir, f"{test_uuid}.json")
        assert os.path.exists(file_path)

        # Verify file contents
        with open(file_path, "r") as f:
            saved_data = json.load(f)
            assert saved_data["id"] == test_uuid
            assert saved_data["name"] == "New Prompt"
            assert saved_data["template"] == "Test template with {{variable}}"


def test_load_template_json(prompt_loader, temp_dirs):
    """Test loading a template from a JSON file."""
    prompts_dir, _ = temp_dirs

    # Create test prompt JSON file
    prompt_data = {
        "id": "test_template",
        "name": "Test Template",
        "template": "This is a test template with {placeholder}",
    }
    file_path = os.path.join(prompts_dir, "test_template.json")
    with open(file_path, "w") as f:
        json.dump(prompt_data, f)

    # Test loading the template with a placeholder
    result = prompt_loader.load_template("test_template", placeholder="test value")

    # Check result
    assert result == "This is a test template with test value"


def test_load_template_txt(prompt_loader, temp_dirs):
    """Test loading a template from a TXT file."""
    _, templates_dir = temp_dirs

    # Create test template TXT file
    template_content = "This is a test template from txt file with {placeholder}"
    file_path = os.path.join(templates_dir, "test_template.txt")
    with open(file_path, "w") as f:
        f.write(template_content)

    # Test loading the template with a placeholder
    result = prompt_loader.load_template("test_template", placeholder="test value")

    # Check result
    assert result == "This is a test template from txt file with test value"


def test_load_template_txt_preferred_over_json(prompt_loader, temp_dirs):
    """Test that when both JSON and TXT files exist, JSON is preferred."""
    prompts_dir, templates_dir = temp_dirs

    # Create test prompt JSON file
    prompt_data = {
        "id": "test_template",
        "name": "Test Template",
        "template": "This is a JSON template with {placeholder}",
    }
    json_path = os.path.join(prompts_dir, "test_template.json")
    with open(json_path, "w") as f:
        json.dump(prompt_data, f)

    # Create test template TXT file
    template_content = "This is a TXT template with {placeholder}"
    txt_path = os.path.join(templates_dir, "test_template.txt")
    with open(txt_path, "w") as f:
        f.write(template_content)

    # Test loading the template
    result = prompt_loader.load_template("test_template", placeholder="test value")

    # Check that JSON template was used
    assert result == "This is a JSON template with test value"


def test_load_template_not_found(prompt_loader):
    """Test loading a non-existent template."""
    with pytest.raises(PromptTemplateNotFoundError):
        prompt_loader.load_template("nonexistent_template")


def test_load_template_missing_variable(prompt_loader, temp_dirs):
    """Test loading a template with a missing required variable."""
    _, templates_dir = temp_dirs

    # Create test template with required variable
    template_content = "Template with {required_var}"
    file_path = os.path.join(templates_dir, "test_template.txt")
    with open(file_path, "w") as f:
        f.write(template_content)

    # Test loading without the required variable
    with pytest.raises(ValueError, match="テンプレート変数が不足しています"):
        prompt_loader.load_template("test_template")


def test_load_template_invalid_format(prompt_loader, temp_dirs):
    """Test loading a template with invalid format string."""
    _, templates_dir = temp_dirs

    # Create test template with invalid format
    template_content = "Template with {unclosed"
    file_path = os.path.join(templates_dir, "test_template.txt")
    with open(file_path, "w") as f:
        f.write(template_content)

    # Test loading with invalid format
    with pytest.raises(ValueError, match="テンプレート変数の形式が不正です"):
        prompt_loader.load_template("test_template")


def test_load_template_generic_error(prompt_loader, temp_dirs):
    """Test generic error handling in load_template."""
    _, templates_dir = temp_dirs

    # Create test template file
    file_path = os.path.join(templates_dir, "test_template.txt")
    with open(file_path, "w") as f:
        f.write("Test template")

    # Mock the file reading to raise an exception
    with patch("builtins.open", side_effect=Exception("Unexpected error")):
        with pytest.raises(Exception, match="プロンプトのロード中にエラーが発生しました"):
            prompt_loader.load_template("test_template")
