import pytest
import os
from src.backend.app.utils.prompt_loader import PromptLoader, PromptTemplateNotFoundError

@pytest.fixture
def prompt_loader(tmp_path):
    """Create a PromptLoader instance with temporary directories"""
    templates_dir = tmp_path / "templates"
    prompts_dir = tmp_path / "templates" / "prompts"
    templates_dir.mkdir()
    prompts_dir.mkdir()
    return PromptLoader(prompts_dir=str(prompts_dir), templates_dir=str(templates_dir))

@pytest.fixture
def sample_template(tmp_path):
    """Create a sample template file"""
    template_path = tmp_path / "templates" / "test_template.txt"
    template_content = "これは{topic}についてのテストです。{option}も含みます。"
    template_path.write_text(template_content, encoding='utf-8')
    return template_path

@pytest.fixture
def sample_json_prompt(tmp_path):
    """Create a sample JSON prompt file"""
    import json
    prompt_path = tmp_path / "templates" / "prompts" / "test_prompt.json"
    prompt_data = {
        "id": "test_prompt",
        "name": "テストプロンプト",
        "description": "テスト用のプロンプト",
        "template": "これは{topic}についてのJSONテストです。{option}も含みます。"
    }
    prompt_path.write_text(json.dumps(prompt_data, ensure_ascii=False), encoding='utf-8')
    return prompt_path

def test_load_template_replaces_variables(prompt_loader, sample_template):
    """load_templateが変数を正しく置き換えることを確認"""
    result = prompt_loader.load_template("test_template", topic="猫", option="犬")
    assert "猫" in result
    assert "犬" in result

def test_load_template_from_json(prompt_loader, sample_json_prompt):
    """JSONプロンプトから正しくテンプレートを読み込むことを確認"""
    result = prompt_loader.load_template("test_prompt", topic="猫", option="犬")
    assert "猫" in result
    assert "犬" in result
    assert "JSONテスト" in result

def test_load_template_file_not_found(prompt_loader):
    """存在しないテンプレートファイルのエラーハンドリングを確認"""
    with pytest.raises(PromptTemplateNotFoundError):
        prompt_loader.load_template("non_existent_template")

def test_get_all_prompts(prompt_loader, sample_json_prompt):
    """全プロンプトの取得を確認"""
    prompts = prompt_loader.get_all_prompts()
    assert len(prompts) == 1
    assert prompts[0]["id"] == "test_prompt"
    assert prompts[0]["name"] == "テストプロンプト"

def test_get_prompt_by_id(prompt_loader, sample_json_prompt):
    """IDによるプロンプト取得を確認"""
    prompt = prompt_loader.get_prompt_by_id("test_prompt")
    assert prompt is not None
    assert prompt["name"] == "テストプロンプト"

def test_create_prompt(prompt_loader):
    """新しいプロンプトの作成を確認"""
    new_prompt = {
        "name": "新規プロンプト",
        "description": "新しく作成したプロンプト",
        "template": "これは{topic}についての新しいテストです。"
    }
    result = prompt_loader.create_prompt(new_prompt)
    assert "id" in result
    assert result["name"] == "新規プロンプト"

    # 作成したプロンプトが取得できることを確認
    saved_prompt = prompt_loader.get_prompt_by_id(result["id"])
    assert saved_prompt is not None
    assert saved_prompt["name"] == "新規プロンプト" 