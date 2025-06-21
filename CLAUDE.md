# Claude Context for PakAgent

## Project Overview
PakAgent is a 4-program workflow system that simplifies LLM-assisted code development by eliminating the copy-paste workflow. It uses the pak tool for semantic compression and pakdiff format for precise method-level code changes.

## Architecture
The system consists of 4 simple programs that work together:

1. **send.py** - Packages files using pak tool compression
2. **modify.py** - Gets LLM-generated changes in pakdiff format
3. **show_answer.py** - 3-window curses interface for reviewing changes
4. **apply.py** - Safely applies pakdiff changes to codebase

## Workflow
```bash
./send.py *.py *.md              # Package files → /tmp/archive.txt
./modify.py "add logging"        # LLM changes → /tmp/answer + /tmp/fix
./show_answer.py                 # Review changes in 3-window interface
./apply.py                       # Apply changes to codebase
```

## Key Technologies
- **Pak Tool**: Semantic compression and pakdiff application
- **Pakdiff v4.3.0**: Method-level diff format with global sections
- **OpenRouter API**: LLM integration (Claude/GPT models)
- **Curses**: Terminal UI for change review
- **Python**: Simple, focused scripts

## File Structure
- `send.py` - File packaging with pak compression
- `modify.py` - LLM interaction and pakdiff generation
- `show_answer.py` - Interactive change review interface
- `apply.py` - Safe pakdiff application
- `analysys.md` - Complete system specification
- `README.md` - User documentation

## Configuration
Uses `.env` file for:
- `OPENROUTER_API_KEY` - API access
- `OPENROUTER_MODEL` - LLM model selection
- `OPENROUTER_MAX_TOKENS` - Response limits
- `OPENROUTER_TEMPERATURE` - Generation randomness

## Dependencies
- pak tool (v5.0.0+) for compression/application
- python-dotenv for environment variables
- requests for API calls
- curses for terminal interface (built-in)

## Development Notes
- Each program is self-contained and focused
- Uses /tmp/ for intermediate files
- Follows pak ecosystem conventions
- Defensive programming with error handling
- Interactive confirmations for safety

## Testing Commands
```bash
# Basic workflow test
./send.py
./modify.py "add comments to methods"
./show_answer.py
./apply.py --force

# File-specific test
./send.py calculator.py
./modify.py "add input validation"

# Review without applying
./modify.py "refactor for clarity" && ./show_answer.py
```

## Integration Points
- Pak tool for all compression/diff operations
- OpenRouter for LLM API access
- Git for version control (apply.py suggests git workflow)
- Terminal environment for curses interface

## Error Handling
- Missing dependencies (pak tool, API keys)
- Invalid pakdiff format
- File not found errors
- API failures with retry suggestions
- Interactive confirmations before destructive operations