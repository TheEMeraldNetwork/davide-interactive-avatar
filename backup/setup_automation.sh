#!/bin/bash

echo "🚀 Setting up Voice Automation System for HeyGen"
echo "================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    echo "Please install Python 3 from https://python.org"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Make Python script executable
chmod +x voice_automation.py

echo ""
echo "🎯 Setup complete! Usage instructions:"
echo "======================================"
echo ""
echo "1. Open index-voice.html in your browser"
echo "2. Turn OFF HeyGen's microphone"
echo "3. Click 'Voice Input' and speak"
echo "4. The system will:"
echo "   - Copy text to clipboard automatically"
echo "   - Show guidance popup"
echo "   - You click in HeyGen chat and press Cmd+V"
echo ""
echo "For full automation (optional):"
echo "python3 voice_automation.py 'your text here'"
echo ""
echo "🎉 Ready to use!" 