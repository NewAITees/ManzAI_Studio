# Python Development Rules for ManzAI Studio

## General Guidelines

### Code Style
- Use **ruff** for formatting and linting (configured in pyproject.toml)
- Line length: 100 characters
- Target Python version: 3.12+
- Use **Black** compatible formatting
- Follow **Google style docstrings**

### Type Hints
- **Mandatory** type hints for all functions and methods
- Use **strict MyPy** configuration
- Prefer `from typing import` over `typing.` prefix
- Use **Pydantic models** for data validation and serialization

### Import Organization (ruff/isort)
1. **Standard library imports**
2. **Third-party library imports**
3. **Local application imports**
4. Separate each group with blank line

```python
# Standard library
import os
from pathlib import Path

# Third-party
from flask import Flask
from pydantic import BaseModel

# Local
from src.backend.app.models.script import ScriptModel
```

## ManzAI Studio Specific Rules

### Backend Development (Flask)
- Use **Pydantic models** for request/response validation
- Implement proper **error handling** with custom exceptions
- Use **dependency injection** pattern for services
- Follow **Blueprint pattern** for route organization

### Service Layer Pattern
```python
# Services should be injected via app context
def some_route():
    ollama_service = current_app.ollama_service
    result = ollama_service.generate_script(topic)
    return jsonify(result)
```

### Data Models
- All models inherit from **Pydantic BaseModel**
- Use **enums** for role definitions (Role.TSUKKOMI, Role.BOKE)
- Implement **proper validation** with field constraints

### Error Handling
- Use **structured exceptions** (APIError, OllamaServiceError, etc.)
- Implement **@api_error_handler** decorator for consistent responses
- Log errors with **appropriate levels** (INFO, WARNING, ERROR)

### Testing
- Use **pytest** with fixtures in `conftest.py`
- **Mock external services** (Ollama, VoiceVox) for reliable testing
- Aim for **high test coverage** (>80%)
- Test **both success and error scenarios**

## File Structure Guidelines

### Backend Structure
```
src/backend/app/
├── models/          # Pydantic data models
├── routes/          # Flask blueprints
├── services/        # Business logic
├── templates/       # AI prompt templates
├── utils/           # Helper functions
└── config.py        # Configuration management
```

### Naming Conventions
- **snake_case** for variables, functions, modules
- **PascalCase** for classes
- **UPPER_CASE** for constants
- **Descriptive names** for functions and variables

## Dependencies

### Required Production Dependencies
- **Flask** - Web framework
- **Pydantic** - Data validation
- **python-dotenv** - Environment management
- **requests** - HTTP client
- **flask-cors** - CORS handling

### Required Development Dependencies
- **ruff** - Modern linting and formatting
- **pytest** + **pytest-cov** - Testing framework
- **mypy** - Static type checking
- **pre-commit** - Git hooks for code quality
- **safety** + **bandit** - Security scanning

## AI Integration Guidelines

### Ollama Service
- Always handle **connection errors** gracefully
- Implement **timeout configurations**
- Use **structured prompts** from template system
- Validate **JSON responses** with Pydantic models

### VoiceVox Integration
- Handle **audio file generation** with proper cleanup
- Implement **speaker management** for character voices
- Synchronize **audio timing** with Live2D animations

## Security Best Practices

- **Never log sensitive data** (API keys, user inputs)
- Use **environment variables** for configuration
- Implement **input validation** on all endpoints
- Handle **file uploads** securely with size limits
- Use **proper CORS** configuration

## Performance Guidelines

- Use **async patterns** where appropriate
- Implement **caching** for expensive operations
- **Stream large responses** when possible
- Monitor **memory usage** for LLM operations
- Optimize **database queries** (if applicable)

## Common Patterns to Avoid

- **Bare except** statements (use specific exceptions)
- **Hard-coded values** (use configuration)
- **Direct file system access** without validation
- **Synchronous operations** for long-running tasks
- **Missing type hints** on public interfaces
