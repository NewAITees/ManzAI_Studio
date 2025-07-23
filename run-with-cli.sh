#!/bin/bash
set -e

PROJECT_NAME=$(basename $(pwd))
CONTAINER_NAME="${PROJECT_NAME}-dev"

echo "🚀 Starting ManzAI Studio development environment..."

# Check if modern-python-base image exists
if ! docker images | grep -q "modern-python-base"; then
    echo "❌ Error: modern-python-base image not found!"
    echo "Please build the base image first:"
    echo "  cd /path/to/modern-vibecoding-devcontainer/base"
    echo "  ./build.sh"
    exit 1
fi

# Check if container is already running
if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
    echo "📦 Container $CONTAINER_NAME is already running"
    echo "🔗 Connecting to existing container..."
    docker exec -it "$CONTAINER_NAME" bash
    exit 0
fi

# Check if container exists but is stopped
if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
    echo "🔄 Starting existing container $CONTAINER_NAME..."
    docker start "$CONTAINER_NAME"
    docker exec -it "$CONTAINER_NAME" bash
    exit 0
fi

# Create new container with persistent volumes
echo "🆕 Creating new container $CONTAINER_NAME..."
docker run -it --rm \
    --name "$CONTAINER_NAME" \
    -v $(pwd):/workspace \
    -v ~/.cache/uv:/home/dev/.cache/uv \
    -v "${PROJECT_NAME}-config:/home/dev/.config" \
    -v "${PROJECT_NAME}-npm:/home/dev/.npm-global" \
    -p 8000:8000 \
    -p 3000:3000 \
    -p 5000:5000 \
    -p 11434:11434 \
    -p 50021:50021 \
    -e PYTHONUNBUFFERED=1 \
    -e PYTHONDONTWRITEBYTECODE=1 \
    -e UV_CACHE_DIR=/home/dev/.cache/uv \
    -e NPM_CONFIG_PREFIX=/home/dev/.npm-global \
    -e PATH="/home/dev/.npm-global/bin:$PATH" \
    -e FLASK_ENV=development \
    -e FLASK_DEBUG=1 \
    --user dev \
    --workdir /workspace \
    modern-python-base:latest bash -c "
        echo '🔧 Setting up ManzAI Studio development environment...'
        
        # Install CLI tools if setup script exists and tools aren't installed
        if [ -f setup-cli.sh ] && [ ! -f ~/.npm-global/bin/claude ]; then
            echo '🛠️  Running initial setup...'
            ./setup-cli.sh
        fi
        
        # Set up Python environment
        if [ -f pyproject.toml ]; then
            echo '🐍 Installing Python dependencies...'
            uv sync --dev --quiet
        fi
        
        # Set up frontend dependencies
        if [ -d frontend ] && [ -f frontend/package.json ]; then
            echo '🟢 Installing frontend dependencies...'
            cd frontend && npm install --silent && cd ..
        fi
        
        # Display welcome message
        echo ''
        echo '🎭 Welcome to ManzAI Studio Development Environment!'
        echo '   Modern Python Development with AI CLI Tools'
        echo ''
        echo '📍 Available services:'
        echo '   • Backend API:       http://localhost:5000'
        echo '   • Frontend Dev:      http://localhost:3000'
        echo '   • Development:       http://localhost:8000'
        echo '   • Ollama:           http://localhost:11434'
        echo '   • VoiceVox:         http://localhost:50021'
        echo ''
        echo '🛠️  Available commands:'
        echo '   • uv run start      - Start Flask server'
        echo '   • uv run test       - Run Python tests'
        echo '   • uv run lint       - Run code linting'
        echo '   • uv run format     - Format code'
        echo '   • make dev          - Start full development stack'
        echo '   • make test         - Run all tests'
        echo ''
        if command -v claude &> /dev/null; then
            echo '🤖 AI Tools available:'
            echo '   • claude            - Claude Code CLI'
        fi
        if command -v gemini &> /dev/null; then
            echo '   • gemini            - Gemini CLI'
        fi
        echo ''
        echo '📚 Documentation: ./docs/'
        echo '🔧 Configuration: ./.devcontainer/ and ./compose.yml'
        echo ''
        
        # Start interactive shell
        exec bash
    "