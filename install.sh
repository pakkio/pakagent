#!/bin/bash

# install.sh - Build and install pakagent programs to ~/bin
# Creates four binaries: send, modify, pakdiff, apply

set -e  # Exit on error

echo "🔨 Building pakagent programs with PyInstaller..."

# Check if PyInstaller is available
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Create ~/bin directory if it doesn't exist
mkdir -p ~/bin

# Build each program
echo "Building send..."
pyinstaller send.spec --distpath dist --workpath build

echo "Building modify..."
pyinstaller modify.spec --distpath dist --workpath build

echo "Building pakdiff (show_answer)..."
pyinstaller show_answer.spec --distpath dist --workpath build

echo "Building apply..."
pyinstaller apply.spec --distpath dist --workpath build

# Copy to ~/bin
echo "📦 Installing binaries to ~/bin..."
cp dist/send ~/bin/
cp dist/modify ~/bin/
cp dist/pakdiff ~/bin/
cp dist/apply ~/bin/

# Make executable
chmod +x ~/bin/send
chmod +x ~/bin/modify  
chmod +x ~/bin/pakdiff
chmod +x ~/bin/apply

echo "✅ Installation complete!"
echo ""
echo "Programs installed to ~/bin:"
echo "  send     - Package files for LLM"
echo "  modify   - Get LLM changes in pakdiff format"
echo "  pakdiff  - Review changes in 3-window interface"
echo "  apply    - Apply pakdiff changes to codebase"
echo ""
echo "Make sure ~/bin is in your PATH:"
echo "  export PATH=\"\$HOME/bin:\$PATH\""
echo ""
echo "🧹 Cleaning up build artifacts..."
rm -rf build/ dist/

echo "🎉 Ready to use! Try: send *.py"