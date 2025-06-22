# PakAgent

A secure, enterprise-grade 5-program workflow system for LLM-assisted code development using pak tool and pakdiff format.

## Overview

PakAgent simplifies the process of getting LLM help with your code by automating the tedious copy-paste workflow. It uses the pak tool for semantic compression and pakdiff format for precise code changes.

**🔒 Security-First Design** - Built with comprehensive input sanitization, API key protection, and code validation to ensure safe operation in any environment.

**🚀 Professional Workflow** - Logging framework, git integration, and session management for reliable development processes.

## The 6-Program Workflow

### a) `send.py` - Package Files
```bash
./send.py                    # Default: *.py *.md files
./send.py *.js *.ts          # Specific file types
./send.py src/ docs/         # Directories
```
Produces `/tmp/archive.txt` with compressed files for LLM review.

### b) `modify.py` - Get LLM Changes  
```bash
./modify.py "add logging to all methods"
./modify.py "implement error handling"
./modify.py "refactor for better readability"
```
Uses `/tmp/archive.txt` and generates:
- `/tmp/answer` - LLM's analysis and explanation
- `/tmp/fix` - Pakdiff format changes

### c) `pakdiff.py` - Review Changes
```bash
./pakdiff.py
```
Opens 3-window terminal interface to review:
- Window 1: LLM analysis (↑↓ to scroll)
- Window 2: Pakdiff summary (PgUp/PgDn to navigate)  
- Window 3: Method details (synchronized with window 2, +/- to scroll)

Controls: `a/z` (top/bottom), `s/x` (navigate), `d/c` (jump), `q` (quit)

### d) `apply.py` - Apply Changes
```bash
./apply.py                   # Interactive confirmation
./apply.py --force          # Skip confirmation
```
Applies pakdiff changes to your codebase with verification.

### e) `revert.py` - Restore Original Files
```bash
./revert.py                  # Interactive confirmation
./revert.py --force         # Skip confirmation
```
Restores files to their original state from session archive if apply fails or you want to undo changes.

### f) `pakview.py` - Navigate Pak Archives
```bash
./pakview.py                 # View current session archive
./pakview.py archive.pak     # View specific pak file
```
3-window interface to explore pak archives: metadata, file list, and content view with navigation controls.

## 🔒 Security Features

PakAgent includes enterprise-grade security features:

### Input Sanitization
- **Command Injection Prevention** - All file patterns and paths are sanitized
- **Path Traversal Protection** - Prevents access to system directories
- **Dangerous Character Filtering** - Removes shell metacharacters (`;`, `&`, `|`, etc.)

### API Key Protection  
- **Automatic Masking** - API keys never appear in logs or error messages
- **Multiple Pattern Detection** - Catches various key formats and contexts
- **Secure Error Handling** - Sensitive data stripped from all outputs

### Code Validation
- **Pakdiff Safety Checks** - Validates code changes before application  
- **Dangerous Pattern Detection** - Warns about risky code patterns
- **Format Verification** - Ensures pakdiff integrity before applying

## 📊 Logging & Monitoring

### Comprehensive Logging Framework
- **Structured Logging** - Timestamps, levels, and component identification
- **File + Console Output** - Logs saved to `~/.pakagent/logs/pakagent.log`
- **Configurable Levels** - Set `PAKAGENT_LOG_LEVEL` environment variable
- **Security-Safe** - All sensitive data automatically masked

### Log Levels
```bash
export PAKAGENT_LOG_LEVEL=DEBUG    # Verbose debugging
export PAKAGENT_LOG_LEVEL=INFO     # Default level
export PAKAGENT_LOG_LEVEL=WARNING  # Warnings and errors only
export PAKAGENT_LOG_LEVEL=ERROR    # Errors only
```

## Complete Example Workflow

```bash
# 1. Package your Python and markdown files
./send.py *.py *.md

# 2. View the packaged archive (optional)
./pakview.py

# 3. Request changes from LLM
./modify.py "add comprehensive logging and error handling"

# 4. Review the proposed changes
./pakdiff.py

# 5. Apply the changes to your codebase
./apply.py

# 6. If something goes wrong, revert to original state
./revert.py
```

## Installation

### Quick Install (Recommended)
```bash
# Install PakAgent as standalone binaries
./install.sh

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/bin:$PATH"

# Verify installation
send --help
```

### Prerequisites

1. **Pak Tool**: Install pak v5.0.0 or later
   ```bash
   # Clone and install pak
   git clone https://github.com/your-org/pak.git
   cd pak && ./install.sh
   ```

2. **Python Environment**: Poetry or pip
   ```bash
   # Using Poetry (recommended)
   poetry install
   
   # Using pip
   pip install requests python-dotenv
   ```

3. **API Key**: Set up OpenRouter API key
   ```bash
   # Create .env file
   echo "OPENROUTER_API_KEY=your_key_here" > .env
   ```

## Configuration

Create `.env` file with:
```env
# Required: OpenRouter API Configuration
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku:beta
OPENROUTER_MAX_TOKENS=4000
OPENROUTER_TEMPERATURE=0.1

# Optional: Logging Configuration
PAKAGENT_LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
PAKAGENT_TMP_DIR=/custom/temp/path        # Override temp directory
```

## Features

### Core Functionality
- **Semantic Compression**: Uses pak tool for intelligent file packaging
- **Pakdiff v4.3.0**: Precise method-level changes with global section support
- **Interactive Review**: 3-window terminal interface for change inspection
- **Safe Application**: Verification and confirmation before applying changes
- **Multi-language Support**: Python, JavaScript, Java, C++, and more
- **Iterative Workflow**: Run modify multiple times to refine changes

### Enterprise Features
- **🔒 Security-First**: Input sanitization, API key protection, code validation
- **📊 Professional Logging**: Structured logs with configurable levels
- **🔧 Git Integration**: Branch workflows, status checks, commit suggestions
- **🏗️ Session Management**: Persistent session files, cleanup handling
- **⚡ Standalone Binaries**: PyInstaller-built executables for easy deployment
- **🛡️ Error Recovery**: Comprehensive error handling and rollback capabilities

## Advanced Usage

### Multiple Iterations
```bash
./send.py
./modify.py "add basic logging"
./pakdiff.py
./apply.py

# Refine further
./send.py  # Re-package updated code
./modify.py "improve the logging with structured format"
./pakdiff.py
./apply.py
```

### Specific File Focus
```bash
./send.py src/core.py src/utils.py
./modify.py "optimize the core algorithms"
```

### Review Without Applying
```bash
./modify.py "add unit tests"
./pakdiff.py  # Review changes
# Don't run apply.py if you don't like the changes
```

## Troubleshooting

### Common Issues
- **"pak command not found"**: Install pak tool and ensure it's in PATH
- **"API key not found"**: Set OPENROUTER_API_KEY in .env file
- **"Archive not found"**: Run send.py first to create session archive
- **Pakdiff errors**: Check format with `pak -vd <pakdiff_file>`

### Security-Related
- **"Invalid file pattern"**: Pattern contains dangerous characters - use only alphanumeric, dots, stars, and forward slashes
- **"Path traversal not allowed"**: Remove `..` sequences from file paths
- **"Access to system directory not allowed"**: Avoid paths starting with `/etc/`, `/usr/`, etc.

### Logging & Debugging
```bash
# Enable debug logging
export PAKAGENT_LOG_LEVEL=DEBUG
send *.py

# Check log files
tail -f ~/.pakagent/logs/pakagent.log

# Validate pakdiff content
apply --force  # Skip validation if needed
```

## Architecture

PakAgent follows the pak ecosystem philosophy with enterprise-grade enhancements:

### Core Components
- **send.py**: Secure file packaging with input sanitization and git integration
- **modify.py**: LLM integration with API key protection and response validation
- **pakdiff.py**: Curses-based pakdiff visualization with safety checks
- **apply.py**: Secure pakdiff application with content validation and rollback
- **revert.py**: Safe file restoration with confirmation workflows

### Security Architecture
- **pakagent_config.py**: Centralized security functions and logging framework
- **Input Sanitization**: All user inputs validated before processing
- **API Key Protection**: Automatic masking in all outputs and logs
- **Code Validation**: Pakdiff content checked for safety before application

### Key Design Principles
- **Security by Default**: All operations secured against common vulnerabilities
- **Fail-Safe Operations**: Comprehensive error handling and recovery mechanisms
- **Observability**: Detailed logging for debugging and audit trails
- **Git-Aware**: Deep integration with git workflows and branch management

This design eliminates the copy-paste workflow while ensuring enterprise-grade security and reliability for LLM-assisted development.