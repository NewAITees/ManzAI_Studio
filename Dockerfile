FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# Copy poetry configuration
COPY pyproject.toml poetry.lock ./

# Configure poetry
RUN poetry config virtualenvs.create false

# Install dependencies without development packages
RUN poetry install --no-dev --no-root

# Copy application code
COPY . .

# Create static directories
RUN mkdir -p static/audio

# Set environment variables
ENV FLASK_APP=src.app:create_app
ENV FLASK_ENV=production
ENV VOICEVOX_URL=http://voicevox:50021
ENV OLLAMA_URL=http://ollama:11434
ENV OLLAMA_MODEL=llama2

# Expose port
EXPOSE 5000

# Run the application using gunicorn
CMD ["poetry", "run", "gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"] 