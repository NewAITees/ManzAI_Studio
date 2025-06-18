# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ManzAI Studio** is a web application that generates and performs manzai (Japanese comedy) scripts using local LLMs and voice synthesis. It features Live2D character animations synchronized with audio, running entirely locally without internet dependency.

**Purpose**: Create an entertainment application that combines AI-powered script generation with Live2D animation and Japanese voice synthesis for immersive manzai comedy experiences.

**Team**: Multi-language development (Python backend, React frontend, Docker containerization)

## Technology Stack

**Backend**:
- **Python 3.10+** with Flask web framework
- **Pydantic 2.0+** for data validation and serialization
- **Poetry** for dependency management (transitioning to uv)
- **pytest** with coverage for testing
- **MyPy** for strict type checking
- **Black + isort** for code formatting

**Frontend**:
- **React 18.2** with functional components
- **Webpack 5** custom configuration
- **Jest + React Testing Library** for testing
- **Live2D SDK** for character animation
- **Axios** for API communication

**External Services**:
- **Ollama** (local LLM server, default: gemma3:4b)
- **VoiceVox** (Japanese TTS engine)
- **Docker + Docker Compose** for containerization

## Domain Knowledge

### Business Rules
- Scripts generated based on user-provided topics with manzai format (boke/tsukkomi roles)
- Audio generation synchronized with Live2D character mouth movements
- All processing happens locally - no internet dependency after setup
- Multiple Live2D models supported (Haru, Bambas2, Neko_Army)
- Custom prompt templates allow script generation customization

### Data Models
```python
# Key data structures from src/backend/app/models/
class ScriptModel(BaseModel):
    boke_lines: List[str]
    tsukkomi_lines: List[str]
    topic: str

class AudioModel(BaseModel):
    file_path: str
    character: str
    text: str

class ServiceModel(BaseModel):
    status: str
    message: str
```

## Development Commands

### Docker Development (Recommended)
```bash
# Start development environment with hot reload
make dev

# Start production environment
make prod

# Run backend tests
make test

# View logs (backend specific)
make backend-logs

# Clean up containers and volumes
make clean

# Complete rebuild with cache clearing
make rebuild
```

### Backend Development
```bash
# Poetry commands (current)
poetry run start       # Start Flask server
poetry run test        # Run pytest with coverage
poetry run lint        # Flake8 linting
poetry run format      # Black formatting
poetry run type-check  # MyPy type checking

# UV commands (modern approach)
uv run start          # Start Flask server
uv run pytest        # Run tests
uv run ruff check     # Modern linting
uv run ruff format    # Modern formatting
uv run mypy src/      # Type checking
```

### Frontend Development
```bash
cd frontend/

# Development server with hot reload
npm run start

# Production build
npm run build

# Testing
npm test              # Run Jest tests
npm run test:watch    # Watch mode
npm run test:coverage # With coverage report
```

## Architecture Overview

**Backend Structure (`src/backend/app/`)**:
- `models/` - Pydantic data models (AudioModel, ScriptModel, ServiceModel)
- `routes/` - Flask API blueprints (api.py, models.py, prompts.py)
- `services/` - Business logic (OllamaService, VoiceVoxService, AudioManager)
- `templates/` - AI prompt templates for manzai script generation
- `utils/` - Helper functions (error handlers, validators, prompt loaders)
- `config.py` - Application configuration management

**Frontend Structure (`frontend/src/`)**:
- `components/` - React components (InputForm, DisplayWindow, AudioPlayer, Settings)
- `services/` - API communication and business logic
- `stores/` - State management (character store)
- `utils/` - Utilities (lip sync, Live2D integration, window management)

**Live2D Integration**:
- Models stored in `frontend/public/live2d/models/`
- Character animation synchronized with audio playback
- Lip sync calculations based on audio waveform analysis

## Key Configuration Files

- `pyproject.toml` - Poetry dependencies, Black/MyPy/pytest configuration
- `mypy.ini` - Strict type checking rules (disallow_untyped_defs=true)
- `frontend/package.json` - React dependencies and build scripts
- `frontend/webpack.config.js` - Custom Webpack configuration with dev proxy
- `docker-compose.yml` / `docker-compose.dev.yml` - Container orchestration
- `src/backend/app/config.py` - Runtime configuration for services

## Testing Strategy

**Backend Testing**:
- **Framework**: pytest with fixtures in `tests/conftest.py`
- **Categories**: Unit, integration, service, API tests via `tests/run_tests.py`
- **Coverage**: Enabled by default with `--cov=src`
- **Mocking**: External services (Ollama, VoiceVox) mocked for reliable testing

**Frontend Testing**:
- **Framework**: Jest with React Testing Library
- **Environment**: jsdom for DOM testing
- **Configuration**: `frontend/jest.config.js`
- **Setup**: `frontend/src/setupTests.js`

## Development Guidelines

**Python Code Style**:
- **Formatting**: Black (100 char line length), isort for imports
- **Type Checking**: Strict MyPy configuration enforced
- **Linting**: Flake8 (transitioning to ruff)
- **Docstrings**: Google style documentation required

**API Development**:
- RESTful design with Flask blueprints
- Pydantic models for request/response validation
- Structured error handling with custom exceptions
- CORS enabled for frontend communication

**Frontend Development**:
- Functional React components with hooks
- Component-based architecture with clear separation
- Webpack dev server proxies API calls to Flask backend
- State management via React Context (character store)

## Local Development Workflow

**Initial Setup**:
1. Clone repository and ensure Docker is running
2. Use `make dev` for containerized development (recommended)
3. Or manual setup: `poetry install` + `cd frontend && npm install`

**Development Cycle**:
1. Backend changes automatically reload in dev container
2. Frontend changes hot-reload via Webpack dev server
3. API calls proxied from frontend:3000 to backend:5000
4. Live2D models and audio files mounted as volumes

**Service Dependencies**:
- Ollama server automatically starts with backend container
- VoiceVox engine configured in docker-compose
- No internet required after initial model downloads

## Common Development Tasks

**Adding New API Endpoints**:
1. Add route to `src/backend/app/routes/api.py`
2. Create Pydantic models in `src/backend/app/models/`
3. Implement business logic in `src/backend/app/services/`
4. Add tests in `tests/test_api.py`

**Adding New React Components**:
1. Create component in `frontend/src/components/`
2. Add corresponding test file (*.test.js)
3. Update parent components to integrate
4. Test with `npm test`

**Adding New Live2D Models**:
1. Place model files in `frontend/public/live2d/models/[ModelName]/`
2. Update model metadata with `scripts/create_model_metadata.js`
3. Register in character store (`frontend/src/stores/characterStore.js`)

## Troubleshooting

**Common Issues**:
- Port conflicts: Check Docker containers with `docker ps`
- Model loading failures: Verify Live2D model file structure
- Audio sync issues: Check VoiceVox service status in logs
- Build failures: Clear node_modules and reinstall dependencies

**Debug Commands**:
- Backend logs: `make backend-logs`
- Test debugging: Use `tests/run_tests.py` with verbose flags
- Frontend debugging: Check browser console for React errors
