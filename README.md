# PakAgent

A simple 4-program workflow system for LLM-assisted code development using pak tool and pakdiff format.

## Overview

PakAgent simplifies the process of getting LLM help with your code by automating the tedious copy-paste workflow. It uses the pak tool for semantic compression and pakdiff format for precise code changes.

## The 4-Program Workflow

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

### c) `show_answer.py` - Review Changes
```bash
./show_answer.py
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
Restores files to their original state from `/tmp/archive.txt` if apply fails or you want to undo changes.

## Complete Example Workflow

```bash
# 1. Package your Python and markdown files
./send.py *.py *.md

# 2. Request changes from LLM
./modify.py "add comprehensive logging and error handling"

# 3. Review the proposed changes
./show_answer.py

# 4. Apply the changes to your codebase
./apply.py

# 5. If something goes wrong, revert to original state
./revert.py
```

## Prerequisites

1. **Pak Tool**: Install pak v5.0.0 or later
   ```bash
   # Clone and install pak
   git clone https://github.com/your-org/pak.git
   cd pak && ./install.sh
   ```

2. **API Key**: Set up OpenRouter API key
   ```bash
   # Create .env file
   echo "OPENROUTER_API_KEY=your_key_here" > .env
   ```

3. **Python Dependencies**:
   ```bash
   pip install requests python-dotenv
   ```

## Configuration

Create `.env` file with:
```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3-haiku:beta
OPENROUTER_MAX_TOKENS=4000
OPENROUTER_TEMPERATURE=0.1
```

## Features

- **Semantic Compression**: Uses pak tool for intelligent file packaging
- **Pakdiff v4.3.0**: Precise method-level changes with global section support
- **Interactive Review**: 3-window terminal interface for change inspection
- **Safe Application**: Verification and confirmation before applying changes
- **Multi-language Support**: Python, JavaScript, Java, C++, and more
- **Iterative Workflow**: Run modify multiple times to refine changes

## Advanced Usage

### Multiple Iterations
```bash
./send.py
./modify.py "add basic logging"
./show_answer.py
./apply.py

# Refine further
./send.py  # Re-package updated code
./modify.py "improve the logging with structured format"
./show_answer.py
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
./show_answer.py  # Review changes
# Don't run apply.py if you don't like the changes
```

## Troubleshooting

- **"pak command not found"**: Install pak tool and ensure it's in PATH
- **"API key not found"**: Set OPENROUTER_API_KEY in .env file
- **"Archive not found"**: Run send.py first to create /tmp/archive.txt
- **Pakdiff errors**: Check format with `pak -vd /tmp/fix`

## Architecture

PakAgent follows the pak ecosystem philosophy:
- **send.py**: Wrapper around `pak` compression
- **modify.py**: LLM integration with pakdiff format generation
- **show_answer.py**: Curses-based pakdiff visualization
- **apply.py**: Wrapper around `pak -ad` (apply diff)

This design eliminates the copy-paste workflow and provides a smooth LLM-assisted development experience.