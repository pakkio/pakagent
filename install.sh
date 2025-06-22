#!/bin/bash

# install.sh - Build and install pakagent programs to ~/bin
# Creates six binaries: prepare, pakmod, pakdiff, pakapply, pakrestore, pakview

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
echo "Building prepare..."
pyinstaller prepare.spec --distpath dist --workpath build

echo "Building pakmod..."
pyinstaller pakmod.spec --distpath dist --workpath build

echo "Building pakdiff..."
pyinstaller pakdiff.spec --distpath dist --workpath build

echo "Building pakapply..."
pyinstaller pakapply.spec --distpath dist --workpath build

echo "Building pakrestore..."
pyinstaller pakrestore.spec --distpath dist --workpath build

echo "Building pakview..."
pyinstaller pakview.spec --distpath dist --workpath build

# Copy to ~/bin
echo "📦 Installing binaries to ~/bin..."
cp dist/prepare ~/bin/
cp dist/pakmod ~/bin/
cp dist/pakdiff ~/bin/
cp dist/pakapply ~/bin/
cp dist/pakrestore ~/bin/
cp dist/pakview ~/bin/

# Make executable
chmod +x ~/bin/prepare
chmod +x ~/bin/pakmod  
chmod +x ~/bin/pakdiff
chmod +x ~/bin/pakapply
chmod +x ~/bin/pakrestore
chmod +x ~/bin/pakview

echo "✅ Installation complete!"
echo ""
echo "Programs installed to ~/bin:"
echo "  prepare    - Package files for LLM with git integration"
echo "  pakmod     - Get LLM changes in pakdiff format"
echo "  pakdiff    - Review changes in 3-window interface"
echo "  pakapply   - Apply pakdiff changes with git branch support"
echo "  pakrestore - Restore original files from session archive"
echo "  pakview    - Navigate pak archives in 3-window interface"
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
echo "  pakapply --git-branch    # Apply changes in new branch"
echo "  pakapply --force         # Skip confirmations"
echo ""
echo "🧹 Cleaning up build artifacts..."
rm -rf build/ dist/

echo "🎉 Ready to use! Try: prepare *.py"
echo "💡 For git projects: commit your work first for safest workflow"