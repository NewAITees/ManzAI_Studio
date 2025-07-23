#!/bin/bash
set -e

echo "🚀 Installing CLI tools for ManzAI Studio..."

# Create necessary directories
mkdir -p ~/.npm-global
mkdir -p ~/.cache/uv

# npm configuration for user-local installation
echo "📦 Setting up npm configuration..."
npm config set prefix '~/.npm-global'
export PATH="~/.npm-global/bin:$PATH"

# Install Claude Code CLI
if ! command -v claude &> /dev/null; then
    echo "🤖 Installing Claude Code CLI..."
    npm install -g @anthropic-ai/claude-code@latest
else
    echo "✅ Claude Code CLI already installed"
fi

# Install Gemini CLI
if ! command -v gemini &> /dev/null; then
    echo "💎 Installing Gemini CLI..."
    npm install -g @google/gemini-cli@latest
else
    echo "✅ Gemini CLI already installed"
fi

# Install additional Python development tools with uv
echo "🐍 Installing additional Python development tools..."
if [ -f pyproject.toml ]; then
    # Add development dependencies if they don't exist
    uv add --dev pytest-cov pytest-mock vulture safety bandit --quiet || true
    uv add --dev ruff black mypy --quiet || true
    echo "✅ Python development tools updated"
else
    echo "⚠️  pyproject.toml not found, skipping Python tool installation"
fi

# Install Node.js development tools
echo "🟢 Installing Node.js development tools..."
npm install -g nodemon @types/node typescript ts-node || echo "⚠️  Some Node.js tools may have failed to install"

# Set up shell configuration
echo "🔧 Setting up shell configuration..."
SHELL_RC_FILE=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC_FILE="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC_FILE="$HOME/.bashrc"
fi

if [ -n "$SHELL_RC_FILE" ]; then
    # Add npm global path to shell configuration if not already present
    if ! grep -q 'npm-global/bin' "$SHELL_RC_FILE" 2>/dev/null; then
        echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> "$SHELL_RC_FILE"
        echo "✅ Added npm global path to $SHELL_RC_FILE"
    fi
fi

echo ""
echo "✅ CLI tools installation complete!"
echo ""
echo "🛠️  Available tools:"
echo "  - python $(python --version 2>&1)"
echo "  - uv $(uv --version 2>&1)"
echo "  - node $(node --version 2>&1)"
echo "  - npm $(npm --version 2>&1)"
if command -v claude &> /dev/null; then
    echo "  - claude (Claude Code CLI)"
fi
if command -v gemini &> /dev/null; then
    echo "  - gemini (Gemini CLI)"
fi
echo ""
echo "📋 Next steps:"
echo "  1. Restart your shell or run: source ~/.bashrc (or ~/.zshrc)"
echo "  2. Run 'uv sync --dev' to install Python dependencies"
echo "  3. Run 'cd frontend && npm install' to install frontend dependencies"
echo ""
echo "🎯 ManzAI Studio development environment is ready!"