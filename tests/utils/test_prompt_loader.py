import pytest
from unittest.mock import patch, mock_open
import os
from src.utils.prompt_loader import load_prompt, PromptTemplateNotFoundError

def test_load_prompt_replaces_variables():
    """load_promptが変数を正しく置き換えることを確認"""
    mock_template = "トピック: {topic}について考えてください。また、{option}も検討してください。"
    
    with patch('builtins.open', mock_open(read_data=mock_template)):
        result = load_prompt("test_template", topic="猫", option="犬")
        
        assert result == "トピック: 猫について考えてください。また、犬も検討してください。"

def test_load_prompt_file_not_found():
    """存在しないテンプレートファイルを指定したときにPromptTemplateNotFoundErrorが発生することを確認"""
    with patch('builtins.open', side_effect=FileNotFoundError()):
        with pytest.raises(PromptTemplateNotFoundError):
            load_prompt("non_existent_template")

def test_load_prompt_builds_correct_path():
    """正しいパスでテンプレートファイルを開くことを確認"""
    mock_template = "テスト用テンプレート"
    expected_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "src", "templates")
    
    with patch('builtins.open', mock_open(read_data=mock_template)) as mock_file:
        load_prompt("test_template")
        
        # 呼び出し時のパスを確認
        path_arg = mock_file.call_args[0][0]
        assert path_arg.endswith("test_template.txt")
        assert "templates" in path_arg 