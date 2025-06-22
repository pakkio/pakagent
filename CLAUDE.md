# Claude Context for PakAgent

## Project Overview
PakAgent is a secure, enterprise-grade 5-program workflow system that simplifies LLM-assisted code development by eliminating the copy-paste workflow. It uses the pak tool for semantic compression and pakdiff format for precise method-level code changes.

**Security-First Design**: Built with comprehensive input sanitization, API key protection, and code validation to ensure safe operation in any environment.

## Architecture
The system consists of 6 secure, enterprise-ready programs that work together:

1. **send.py** - Securely packages files using pak tool compression with input sanitization
2. **modify.py** - Gets LLM-generated changes with API key protection and validation
3. **pakdiff.py** - 3-window curses interface for safely reviewing changes
4. **apply.py** - Securely applies pakdiff changes with content validation and verification
5. **revert.py** - Safely restores original files from session archive with confirmations
6. **pakview.py** - 3-window curses interface for navigating pak archives

## Workflow
```bash
./send.py *.py *.md              # Package files → /tmp/archive.txt
./pakview.py                     # View packaged archive (optional)
./modify.py "add logging"        # LLM changes → /tmp/answer + /tmp/fix
./pakdiff.py                     # Review changes in 3-window interface
./apply.py                       # Apply changes to codebase
./revert.py                      # Restore original files if needed
```

## Key Technologies
- **Pak Tool**: Semantic compression and pakdiff application
- **Pakdiff v4.3.0**: Method-level diff format with global sections
- **OpenRouter API**: LLM integration (Claude/GPT models) with secure key handling
- **Curses**: Terminal UI for change review
- **Python**: Secure, enterprise-grade scripts with logging framework
- **PyInstaller**: Standalone binary generation for easy deployment
- **Logging Framework**: Structured logging with configurable levels and security masking

## File Structure
- `send.py` - Secure file packaging with input sanitization and git integration
- `modify.py` - LLM interaction with API key protection and response validation
- `pakdiff.py` - Interactive change review interface with safety checks
- `apply.py` - Secure pakdiff application with content validation
- `revert.py` - Safe file restoration with confirmation workflows
- `pakagent_config.py` - Centralized security functions and logging framework
- `install.sh` - PyInstaller-based binary generation and installation
- `*.spec` - PyInstaller specification files for each program
- `analysys.md` - Complete system specification
- `README.md` - User documentation with security features
- `CLAUDE.md` - Implementation context and development notes

## Configuration
Uses `.env` file for:
- `OPENROUTER_API_KEY` - API access (automatically masked in logs)
- `OPENROUTER_MODEL` - LLM model selection
- `OPENROUTER_MAX_TOKENS` - Response limits
- `OPENROUTER_TEMPERATURE` - Generation randomness
- `PAKAGENT_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)
- `PAKAGENT_TMP_DIR` - Override default temp directory path

## Dependencies
- pak tool (v5.0.0+) for compression/application
- python-dotenv for environment variables
- requests for API calls with retry logic
- curses for terminal interface (built-in)
- logging module for structured logging (built-in)
- re module for input sanitization (built-in)
- PyInstaller for binary generation (dev dependency)

## Development Notes
- Each program is self-contained and focused
- Uses session-based temp files with configurable location
- Follows pak ecosystem conventions with security enhancements
- Defensive programming with comprehensive error handling
- Interactive confirmations for safety with forced override options
- Centralized security functions in pakagent_config.py
- Comprehensive logging framework with sensitive data masking
- All user inputs sanitized to prevent command injection and path traversal
- API keys automatically masked in all log outputs and error messages
- Pakdiff content validated for safety before application

## Testing Commands
```bash
# Basic workflow test
./send.py
./modify.py "add comments to methods"
./pakdiff.py
./apply.py --force

# File-specific test
./send.py calculator.py
./modify.py "add input validation"

# Review without applying
./modify.py "refactor for clarity" && ./pakdiff.py

# Revert if something goes wrong
./revert.py --force
```

## Security Architecture

### Input Sanitization (pakagent_config.py:227-266)
- `sanitize_file_pattern()` - Validates file patterns, removes dangerous characters
- `sanitize_file_path()` - Prevents path traversal, blocks system directory access
- Regular expressions to enforce safe patterns: `^[a-zA-Z0-9_.*/-]+$`

### API Key Protection (pakagent_config.py:268-287)
- `mask_sensitive_data()` - Automatically masks API keys in all outputs
- Multiple detection patterns for various key formats
- Applied to all error messages, logs, and command outputs

### Code Validation (pakagent_config.py:289-341)
- `validate_pakdiff_content()` - Validates pakdiff format and safety
- Detects dangerous code patterns (eval, exec, subprocess, system calls)
- Ensures proper pakdiff structure before application

### Logging Framework (pakagent_config.py:197-223)
- `setup_logging()` - Configures structured logging with masking
- File and console output with timestamps and levels
- Automatic sensitive data masking in all log entries

## Integration Points
- Pak tool for all compression/diff operations with sanitized inputs
- OpenRouter for LLM API access with secure key handling
- Git for version control with branch workflow integration
- Terminal environment for curses interface with safety checks
- Session management for reliable temp file handling

## Error Handling
- Missing dependencies (pak tool, API keys) with helpful messages
- Invalid pakdiff format with detailed validation errors
- File not found errors with suggested remediation
- API failures with retry suggestions and masked error details
- Interactive confirmations before destructive operations
- Security violations (injection attempts, path traversal) with blocking
- Comprehensive logging for debugging and audit trails