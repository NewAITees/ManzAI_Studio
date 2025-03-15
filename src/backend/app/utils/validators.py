"""
Input validation utilities for ManzAI Studio API.

This module provides functions for validating input data for API endpoints.
It includes validation for models, prompts, script generation parameters, etc.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional, Union, Tuple

from werkzeug.datastructures import FileStorage


def validate_model_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate model registration data.
    
    Args:
        data: Dictionary containing model data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['name', 'type']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate model type
    valid_types = ['tsukkomi', 'boke', 'unknown']
    if data['type'] not in valid_types:
        return False, f"Invalid model type: {data['type']}. Must be one of {valid_types}"
    
    # Validate name (not empty)
    if not data['name'] or not isinstance(data['name'], str):
        return False, "Model name must be a non-empty string"
    
    return True, ""


def validate_prompt_data(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate prompt data for creation or update.
    
    Args:
        data: Dictionary containing prompt data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ['name', 'content']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate name (not empty)
    if not data['name'] or not isinstance(data['name'], str):
        return False, "Prompt name must be a non-empty string"
    
    # Validate name format (alphanumeric, underscores, hyphens only)
    if not re.match(r'^[a-zA-Z0-9_-]+$', data['name']):
        return False, "Prompt name must contain only letters, numbers, underscores, and hyphens"
    
    # Validate content (not empty)
    if not data['content'] or not isinstance(data['content'], str):
        return False, "Prompt content must be a non-empty string"
    
    # Check optional fields
    if 'description' in data and not isinstance(data['description'], str):
        return False, "Prompt description must be a string"
    
    if 'tags' in data:
        if not isinstance(data['tags'], list):
            return False, "Tags must be a list"
        for tag in data['tags']:
            if not isinstance(tag, str):
                return False, "Each tag must be a string"
    
    return True, ""


def validate_script_params(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate script generation parameters.
    
    Args:
        data: Dictionary containing script generation parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required fields
    if 'topic' not in data:
        return False, "Missing required field: topic"
    
    # Validate topic (not empty)
    if not data['topic'] or not isinstance(data['topic'], str):
        return False, "Topic must be a non-empty string"
    
    # Check optional fields with defaults
    if 'prompt_name' in data and not isinstance(data['prompt_name'], str):
        return False, "prompt_name must be a string"
    
    if 'max_length' in data:
        if not isinstance(data['max_length'], int) or data['max_length'] < 100 or data['max_length'] > 2000:
            return False, "max_length must be an integer between 100 and 2000"
    
    if 'temperature' in data:
        if not isinstance(data['temperature'], (int, float)) or data['temperature'] < 0 or data['temperature'] > 2:
            return False, "temperature must be a number between 0 and 2"
    
    return True, ""


def validate_model_file(file: FileStorage) -> Tuple[bool, str]:
    """
    Validate a Live2D model file upload.
    
    Args:
        file: The uploaded file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    # Check file extension
    allowed_extensions = ['.model3.json', '.zip']
    file_ext = os.path.splitext(file.filename)[-1].lower()
    
    if file_ext not in allowed_extensions:
        return False, f"Invalid file extension: {file_ext}. Must be one of {allowed_extensions}"
    
    # Check file size (max 50MB)
    if file.content_length > 50 * 1024 * 1024:  # 50MB in bytes
        return False, "File too large. Maximum size is 50MB"
    
    return True, ""


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal and other security issues.
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and ensure only allowed characters
    sanitized = re.sub(r'[^\w\.-]', '_', os.path.basename(filename))
    
    # Ensure it's not empty and doesn't start with a period
    if not sanitized or sanitized.startswith('.'):
        sanitized = 'file_' + sanitized
    
    return sanitized 