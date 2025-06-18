# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ManzAI Studio is a web application that generates and performs manzai (Japanese comedy) scripts using local LLMs and voice synthesis. It features Live2D character animations synchronized with audio, running entirely locally without internet dependency.

## Development Commands

### Docker Development (Recommended)
```bash
# Start development environment with hot reload
make dev

# Start production environment  
make prod

# Run backend tests
make test

# View logs
make logs

# Clean up containers and volumes
make clean

# Complete rebuild with cache clearing
make rebuild
```

### Backend Development (Poetry)
```bash
# Start Flask development server
poetry run start

# Run tests with coverage
poetry run test
poetry run coverage

# Code quality tools
poetry run lint        # Flake8 linting
poetry run format     # Black code formatting  
poetry run type-check # MyPy type checking
```

### Frontend Development
```bash
cd frontend/

# Start development server with hot reload
npm run start

# Build for production
npm run build

# Run tests
npm test
npm run test:watch     # Watch mode
npm run test:coverage  # With coverage
```

## Architecture Overview

**Backend Structure:**
- `src/backend/app/` - Flask application root
- `src/backend/app/models/` - Pydantic data models (AudioModel, ScriptModel, ServiceModel)
- `src/backend/app/routes/` - API endpoints (main blueprint)
- `src/backend/app/services/` - Business logic (OllamaService, VoiceVoxService, AudioManager)
- `src/backend/app/templates/` - AI prompt templates for script generation
- `src/backend/app/utils/` - Helper functions and utilities
- `src/backend/app/config.py` - Application configuration management

**Frontend Structure:**
- `frontend/src/components/` - React components (InputForm, DisplayWindow, AudioPlayer, Settings)
- `frontend/src/services/` - API communication services
- `frontend/src/stores/` - State management (character store)  
- `frontend/src/utils/` - Utilities (lip sync, Live2D integration, window management)

**External Services Integration:**
- **Ollama**: Local LLM server (default model: gemma3:4b) for script generation
- **VoiceVox**: Japanese TTS engine for voice synthesis
- **Live2D**: Character animation system with audio synchronization

## Key Configuration Files

- `pyproject.toml` - Poetry dependencies, code quality tools (Black, MyPy, Flake8), test configuration
- `frontend/package.json` - React app dependencies and scripts
- `docker-compose.yml` / `docker-compose.dev.yml` - Container orchestration
- `src/backend/app/config.py` - Runtime configuration management
- `mypy.ini` - Strict type checking configuration

## Testing Strategy

**Backend Testing:**
- Framework: pytest with fixtures in `tests/conftest.py`
- Test categories: unit, integration, service, API tests
- Run via: `tests/run_tests.py` or `poetry run test`
- Coverage reporting enabled by default

**Frontend Testing:**
- Framework: Jest with React Testing Library
- Configuration: `frontend/jest.config.js`
- jsdom environment for DOM testing

## Development Guidelines

**Code Style:**
- Backend: Black formatting (100 char line length), isort import sorting
- MyPy strict type checking enforced
- Flake8 linting for code quality

**API Development:**
- RESTful API design with Flask blueprints
- Pydantic models for request/response validation
- Error handling with structured responses
- CORS enabled for frontend communication

**Frontend Development:**
- React 18.2 with functional components
- Webpack 5 custom configuration with dev server proxy
- Axios for API communication
- Component-based architecture with clear separation of concerns

## Local Development Setup

The application runs entirely locally with no internet dependency after initial setup:

1. **Containerized Development**: Full Docker setup with hot reloading for both backend and frontend
2. **Service Dependencies**: Ollama and VoiceVox automatically configured via Docker
3. **Volume Mounting**: Source code mounted for live development
4. **Proxy Configuration**: Webpack dev server proxies API calls to Flask backend

## Important Notes

- All processing happens locally - no external API calls during runtime
- Live2D models and animations are synchronized with generated audio
- Template-based prompt system allows customization of AI generation
- Comprehensive error handling across all layers
- File storage for generated audio in `/audio/` directory