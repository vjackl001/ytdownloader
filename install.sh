#!/bin/bash

# Installation script for ytdownloader using uv

set -e

echo "🚀 Installing YouTube Downloader & Video Editor with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
    echo "✅ uv installed successfully"
fi

echo "✅ uv found: $(uv --version)"

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9 or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check for FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg not found!"
    echo "   Video editing features will not work without FFmpeg."
    echo "   Install instructions:"
    echo "   - macOS: brew install ffmpeg"
    echo "   - Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   - Windows: Download from https://ffmpeg.org/download.html"
    echo ""
    read -p "Continue installation anyway? (y/N): " continue_install
    if [[ ! $continue_install =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 1
    fi
else
    echo "✅ FFmpeg found: $(ffmpeg -version | head -n1)"
fi

# Create virtual environment (uv automatically manages this)
echo "📦 Creating virtual environment with uv..."
uv venv

# Activate virtual environment
source .venv/bin/activate
echo "✅ Virtual environment created and activated"

# Install dependencies with uv (much faster than pip)
echo "📦 Installing dependencies with uv..."
uv sync

# Install the package in development mode
echo "📦 Installing ytdownloader..."
uv pip install -e .

# Test installation
echo "🔍 Testing installation..."
if ytdownloader --version > /dev/null 2>&1; then
    echo "✅ Installation successful!"
    echo ""
    echo "🎉 ytdownloader is ready to use!"
    echo ""
    echo "Quick start:"
    echo "  ytdownloader download \"https://youtube.com/watch?v=dQw4w9WgXcQ\""
    echo "  ytdownloader edit video.mp4 --trim-start 10"
    echo "  ytdownloader --help"
    echo ""
    echo "Note: Virtual environment is activated. To use ytdownloader later:"
    echo "  source .venv/bin/activate"
    echo ""
    echo "To deactivate the virtual environment:"
    echo "  deactivate"
else
    echo "❌ Installation failed! Please check the error messages above."
    exit 1
fi