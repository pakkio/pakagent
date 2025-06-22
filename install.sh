#!/bin/bash

# install.sh - Build and install pakagent programs to ~/bin
# Creates six binaries: send, modify, pakdiff, apply, revert, pakview

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

echo "Building pakdiff..."
pyinstaller pakdiff.spec --distpath dist --workpath build

echo "Building apply..."
pyinstaller apply.spec --distpath dist --workpath build

echo "Building revert..."
pyinstaller revert.spec --distpath dist --workpath build

echo "Building pakview..."
pyinstaller pakview.spec --distpath dist --workpath build

# Copy to ~/bin
echo "📦 Installing binaries to ~/bin..."
cp dist/send ~/bin/
cp dist/modify ~/bin/
cp dist/pakdiff ~/bin/
cp dist/apply ~/bin/
cp dist/revert ~/bin/
cp dist/pakview ~/bin/

# Make executable
chmod +x ~/bin/send
chmod +x ~/bin/modify  
chmod +x ~/bin/pakdiff
chmod +x ~/bin/apply
chmod +x ~/bin/revert
chmod +x ~/bin/pakview

echo "✅ Installation complete!"
echo ""
echo "Programs installed to ~/bin:"
echo "  send     - Package files for LLM with git integration"
echo "  modify   - Get LLM changes in pakdiff format"
echo "  pakdiff  - Review changes in 3-window interface"
echo "  apply    - Apply pakdiff changes with git branch support"
echo "  revert   - Restore original files from session archive"
echo "  pakview  - Navigate pak archives in 3-window interface"
echo ""
echo "🔧 New Features:"
echo "  • Session-based temp files (no more /tmp brittleness)"
echo "  • Git integration with branch workflow"
echo "  • Better error handling and cleanup"
echo "  • Automatic git status checks"
echo ""
echo "Make sure ~/bin is in your PATH:"
echo "  export PATH=\"\$HOME/bin:\$PATH\""
echo ""
echo "🔀 Git Integration Usage:"
echo "  apply --git-branch    # Apply changes in new branch"
echo "  apply --force         # Skip confirmations"
echo ""
echo "🧹 Cleaning up build artifacts..."
rm -rf build/ dist/

echo "🎉 Ready to use! Try: send *.py"
echo "💡 For git projects: commit your work first for safest workflow"