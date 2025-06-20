# Bash Tool Best Practices

## Directory Navigation and Path Handling

### ❌ Avoid (不推奨)
```bash
cd /some/directory && npm install
cd frontend
pwd
ls
```

### ✅ Recommended (推奨)
```bash
# Use absolute paths with --prefix for npm commands
npm install --prefix /home/persona/analysis/ManzAI_Studio/frontend

# Use absolute paths for file operations
cat /home/persona/analysis/ManzAI_Studio/frontend/package.json

# Use LS tool instead of ls command
# LS tool with absolute path: /home/persona/analysis/ManzAI_Studio/frontend

# Use Read tool instead of cat command
# Read tool with absolute path: /home/persona/analysis/ManzAI_Studio/frontend/src/App.js
```

## Key Guidelines

1. **Always use absolute paths** - avoid `cd` commands
2. **Use dedicated tools**:
   - Use `LS` tool instead of `ls` command
   - Use `Read` tool instead of `cat`, `head`, `tail` commands
   - Use `Grep` tool instead of `grep` command
   - Use `Glob` tool instead of `find` command

3. **npm/yarn commands with --prefix**:
   ```bash
   npm install --prefix /absolute/path/to/project
   npm run build --prefix /absolute/path/to/project
   npm test --prefix /absolute/path/to/project
   ```

4. **Python commands with absolute paths**:
   ```bash
   python /absolute/path/to/script.py
   pytest /absolute/path/to/tests/
   ```

5. **Multiple commands with absolute paths**:
   ```bash
   # Good - using absolute paths
   pytest /absolute/path/tests/ && flake8 /absolute/path/src/

   # Avoid - using cd
   cd /some/path && pytest tests/
   ```

## Common Patterns

### Frontend Development
```bash
# Install dependencies
npm install --prefix /home/persona/analysis/ManzAI_Studio/frontend

# Start development server
npm run start --prefix /home/persona/analysis/ManzAI_Studio/frontend

# Run tests
npm test --prefix /home/persona/analysis/ManzAI_Studio/frontend

# Build production
npm run build --prefix /home/persona/analysis/ManzAI_Studio/frontend
```

### Python Development
```bash
# Run tests from project root
uv run pytest /home/persona/analysis/ManzAI_Studio/tests/

# Run specific test file
uv run pytest /home/persona/analysis/ManzAI_Studio/tests/test_api.py

# Run linting
uv run ruff check /home/persona/analysis/ManzAI_Studio/src/

# Run formatting
uv run ruff format /home/persona/analysis/ManzAI_Studio/src/
```

### Docker Commands
```bash
# Docker commands from project root (use absolute paths when needed)
docker-compose -f /home/persona/analysis/ManzAI_Studio/docker-compose.yml up -d

# Or use make commands which handle paths internally
make dev
make test
make build
```

## Remember
- **The Bash tool maintains working directory throughout the session**
- **Use absolute paths to avoid confusion**
- **Leverage specialized tools (LS, Read, Grep, Glob) for better performance**
- **Use `--prefix` for npm/yarn commands instead of changing directories**
