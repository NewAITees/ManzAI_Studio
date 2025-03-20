"""
Tests for the validators module.
"""

import os
import unittest
import tempfile
from unittest.mock import Mock, patch

from src.backend.app.utils.validators import (
    validate_model_data,
    validate_prompt_data,
    validate_script_params,
    validate_model_file,
    sanitize_filename
)


class TestValidators(unittest.TestCase):
    """Tests for the validators utility functions."""

    def test_validate_model_data_valid(self):
        """Test validation of valid model data."""
        data = {
            'name': 'Test Model',
            'type': 'tsukkomi',
            'model': 'model.model3.json',
            'textures': ['texture1.png', 'texture2.png'],
        }
        
        is_valid, error = validate_model_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_model_data_missing_fields(self):
        """Test validation of model data with missing required fields."""
        # Missing name
        data = {
            'type': 'tsukkomi',
        }
        
        is_valid, error = validate_model_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Missing required field: name")
        
        # Missing type
        data = {
            'name': 'Test Model',
        }
        
        is_valid, error = validate_model_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Missing required field: type")

    def test_validate_model_data_invalid_type(self):
        """Test validation of model data with invalid type."""
        data = {
            'name': 'Test Model',
            'type': 'invalid_type',
        }
        
        is_valid, error = validate_model_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Invalid model type: invalid_type. Must be one of ['tsukkomi', 'boke', 'unknown']")

    def test_validate_model_data_invalid_name(self):
        """Test validation of model data with invalid name."""
        data = {
            'name': '',
            'type': 'tsukkomi',
        }
        
        is_valid, error = validate_model_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Model name must be a non-empty string")
        
        data = {
            'name': 123,  # Not a string
            'type': 'tsukkomi',
        }
        
        is_valid, error = validate_model_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Model name must be a non-empty string")

    def test_validate_prompt_data_valid(self):
        """Test validation of valid prompt data."""
        data = {
            'name': 'test_prompt',
            'content': 'This is a test prompt content.',
            'description': 'Test description',
            'tags': ['test', 'manzai']
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_prompt_data_missing_fields(self):
        """Test validation of prompt data with missing required fields."""
        # Missing name
        data = {
            'content': 'This is a test prompt content.',
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Missing required field: name")
        
        # Missing content
        data = {
            'name': 'test_prompt',
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Missing required field: content")

    def test_validate_prompt_data_invalid_name(self):
        """Test validation of prompt data with invalid name format."""
        data = {
            'name': 'invalid name with spaces',
            'content': 'This is a test prompt content.',
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Prompt name must contain only letters, numbers, underscores, and hyphens")
        
        # Empty name
        data = {
            'name': '',
            'content': 'This is a test prompt content.',
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Prompt name must be a non-empty string")

    def test_validate_prompt_data_invalid_content(self):
        """Test validation of prompt data with invalid content."""
        data = {
            'name': 'test_prompt',
            'content': '',  # Empty content
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Prompt content must be a non-empty string")
        
        data = {
            'name': 'test_prompt',
            'content': 123,  # Not a string
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Prompt content must be a non-empty string")

    def test_validate_prompt_data_invalid_optional_fields(self):
        """Test validation of prompt data with invalid optional fields."""
        # Invalid description
        data = {
            'name': 'test_prompt',
            'content': 'This is a test prompt content.',
            'description': 123  # Not a string
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Prompt description must be a string")
        
        # Invalid tags (not a list)
        data = {
            'name': 'test_prompt',
            'content': 'This is a test prompt content.',
            'tags': 'not_a_list'
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Tags must be a list")
        
        # Invalid tags (containing non-string)
        data = {
            'name': 'test_prompt',
            'content': 'This is a test prompt content.',
            'tags': ['valid', 123]
        }
        
        is_valid, error = validate_prompt_data(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Each tag must be a string")

    def test_validate_script_params_valid(self):
        """Test validation of valid script generation parameters."""
        data = {
            'topic': 'スポーツ',
            'prompt_name': 'default',
            'max_length': 1000,
            'temperature': 0.7
        }
        
        is_valid, error = validate_script_params(data)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_script_params_missing_topic(self):
        """Test validation of script params with missing topic."""
        data = {
            'prompt_name': 'default',
            'max_length': 1000
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Missing required field: topic")

    def test_validate_script_params_invalid_topic(self):
        """Test validation of script params with invalid topic."""
        # Empty topic
        data = {
            'topic': '',
            'prompt_name': 'default'
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Topic must be a non-empty string")
        
        # Non-string topic
        data = {
            'topic': 123,
            'prompt_name': 'default'
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Topic must be a non-empty string")

    def test_validate_script_params_invalid_optional_fields(self):
        """Test validation of script params with invalid optional fields."""
        # Invalid prompt_name
        data = {
            'topic': 'スポーツ',
            'prompt_name': 123  # Not a string
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "prompt_name must be a string")
        
        # Invalid max_length (too small)
        data = {
            'topic': 'スポーツ',
            'max_length': 50  # Less than 100
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "max_length must be an integer between 100 and 2000")
        
        # Invalid max_length (too large)
        data = {
            'topic': 'スポーツ',
            'max_length': 3000  # More than 2000
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "max_length must be an integer between 100 and 2000")
        
        # Invalid temperature (too small)
        data = {
            'topic': 'スポーツ',
            'temperature': -0.5  # Less than 0
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "temperature must be a number between 0 and 2")
        
        # Invalid temperature (too large)
        data = {
            'topic': 'スポーツ',
            'temperature': 2.5  # More than 2
        }
        
        is_valid, error = validate_script_params(data)
        self.assertFalse(is_valid)
        self.assertEqual(error, "temperature must be a number between 0 and 2")

    def test_validate_model_file_valid(self):
        """Test validation of valid model file."""
        mock_file = Mock()
        mock_file.filename = 'model.model3.json'
        mock_file.content_length = 1024 * 1024  # 1MB
        
        is_valid, error = validate_model_file(mock_file)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")
        
        # Test with zip file
        mock_file.filename = 'model.zip'
        
        is_valid, error = validate_model_file(mock_file)
        self.assertTrue(is_valid)
        self.assertEqual(error, "")

    def test_validate_model_file_no_file(self):
        """Test validation when no file is provided."""
        is_valid, error = validate_model_file(None)
        self.assertFalse(is_valid)
        self.assertEqual(error, "No file provided")

    def test_validate_model_file_invalid_extension(self):
        """Test validation of model file with invalid extension."""
        mock_file = Mock()
        mock_file.filename = 'model.txt'  # Invalid extension
        
        is_valid, error = validate_model_file(mock_file)
        self.assertFalse(is_valid)
        self.assertEqual(error, "Invalid file extension: .txt. Must be one of ['.model3.json', '.zip']")

    def test_validate_model_file_too_large(self):
        """Test validation of model file that is too large."""
        mock_file = Mock()
        mock_file.filename = 'model.model3.json'
        mock_file.content_length = 60 * 1024 * 1024  # 60MB (over the 50MB limit)
        
        is_valid, error = validate_model_file(mock_file)
        self.assertFalse(is_valid)
        self.assertEqual(error, "File too large. Maximum size is 50MB")

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Basic sanitization
        self.assertEqual(sanitize_filename('test.txt'), 'test.txt')
        
        # Remove path components
        self.assertEqual(sanitize_filename('/path/to/test.txt'), 'test.txt')
        self.assertEqual(sanitize_filename('..\\..\\test.txt'), 'test.txt')
        
        # Replace invalid characters
        self.assertEqual(sanitize_filename('test file.txt'), 'test_file.txt')
        self.assertEqual(sanitize_filename('test@#$%^&.txt'), 'test_____.txt')
        
        # Handle empty filename or starting with period
        self.assertEqual(sanitize_filename(''), 'file_')
        self.assertEqual(sanitize_filename('.gitignore'), 'file_.gitignore')


if __name__ == '__main__':
    unittest.main() 