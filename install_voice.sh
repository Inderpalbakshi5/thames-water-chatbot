#!/bin/bash

echo "================================================"
echo "Thames Water Voice Chatbot - Installation"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Check if pip is installed
echo ""
echo "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed. Please install pip first."
    exit 1
fi
echo "pip3 is installed"

# Install system dependencies for audio (Linux only)
echo ""
echo "Installing system dependencies..."
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Detected Linux - installing portaudio19-dev..."
    sudo apt-get update
    sudo apt-get install -y portaudio19-dev python3-pyaudio
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Detected macOS - installing portaudio via brew..."
    if command -v brew &> /dev/null; then
        brew install portaudio
    else
        echo "WARNING: Homebrew not found. Please install portaudio manually."
    fi
fi

# Install Python dependencies
echo ""
echo "Installing Python packages..."
pip3 install -r requirements.txt

echo ""
echo "================================================"
echo "Installation complete!"
echo "================================================"
echo ""
echo "To run the voice chatbot:"
echo "  streamlit run voice_chatbot.py"
echo ""
echo "To run the text-only chatbot:"
echo "  streamlit run water_company_chatbot.py"
echo ""
echo "================================================"
