# Contributing to PakAgent

Thank you for your interest in contributing to PakAgent! We appreciate any help improving this 4-program workflow system for LLM-assisted code development.

## Quick Start

1. **Fork and Clone**: Fork the repository and clone your fork locally
2. **Install Dependencies**: Ensure you have Python 3.7+ and the pak tool installed
3. **Set up Environment**: Copy `.env.example` to `.env` and configure your API keys
4. **Run Tests**: Execute `pytest` to ensure everything works

## Development Workflow

### 1. Setting Up Your Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/pakagent.git
cd pakagent

# Install development dependencies
pip install pytest python-dotenv requests

# Install pak tool (required dependency)
# Follow instructions at: https://github.com/pak-tool/pak

# Set up environment variables
cp .env.example .env  # Edit with your API keys
```

### 2. Making Changes

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow the Architecture**
   - Each program should remain focused and self-contained
   - Use `/tmp/` for intermediate files
   - Follow pak ecosystem conventions
   - Maintain defensive programming practices

3. **Code Style Guidelines**
   - Use clear, descriptive function names
   - Add docstrings to all functions
   - Keep functions small and focused
   - Use proper error handling with try/except blocks
   - Follow PEP 8 style guidelines

### 3. Testing Your Changes

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_send.py

# Test the actual workflow
./send.py *.py *.md
./modify.py "add test comment"
./show_answer.py
./apply.py --force
```

### 4. Pre-commit Checks

Before committing, ensure:

- [ ] All tests pass: `pytest`
- [ ] Code follows style guidelines
- [ ] New functionality has corresponding tests
- [ ] Documentation is updated if needed
- [ ] The basic workflow still works end-to-end

If you have pre-commit hooks installed:
```bash
pre-commit run --all-files
```

### 5. Submitting Your Changes

1. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add clear description of changes"
   ```

2. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open a Pull Request**
   - Provide a clear title and description
   - Reference any related issues
   - Include test results if applicable

## Types of Contributions

### Bug Fixes
- Fix issues with pak tool integration
- Resolve API connection problems
- Address curses interface glitches
- Improve error handling

### New Features
- Enhance LLM integration (new models, prompts)
- Improve user interface (better curses display)
- Add configuration options
- Extend pakdiff format support

### Documentation
- Improve README and usage examples
- Add code comments and docstrings
- Create tutorials or guides
- Update API documentation

### Testing
- Add test cases for edge cases
- Improve test coverage
- Add integration tests
- Create performance benchmarks

## Code Architecture

Understanding the system architecture helps with contributions:

```
send.py     → Packages files using pak compression
modify.py   → LLM interaction and pakdiff generation  
show_answer.py → 3-window curses review interface
apply.py    → Safe pakdiff application to codebase
revert.py   → File restoration from archive
```

### Key Design Principles
- **Simplicity**: Each program has a single, clear purpose
- **Safety**: Interactive confirmations before destructive operations
- **Integration**: Seamless pak tool and LLM API integration
- **Resilience**: Graceful error handling and recovery options

## Testing Guidelines

### Test Structure
- Unit tests for each module in `tests/test_*.py`
- Integration tests for workflow scenarios
- Mock external dependencies (LLM API, pak tool)
- Test both success and failure cases

### Test Categories
- **Unit Tests**: Individual function testing
- **Integration Tests**: Multi-component workflows
- **API Tests**: LLM interaction testing (mocked)
- **UI Tests**: Curses interface testing (where possible)

### Writing Good Tests
```python
def test_function_name_scenario():
    """Test description explaining what is being tested"""
    # Arrange - set up test data
    # Act - execute the function
    # Assert - verify the results
```

## Reporting Issues

When reporting bugs or requesting features:

1. **Search Existing Issues**: Check if already reported
2. **Provide Context**: Include system info, pak version, Python version
3. **Reproduction Steps**: Clear steps to reproduce the issue
4. **Expected vs Actual**: What you expected vs what happened
5. **Logs/Output**: Include relevant error messages or logs

### Issue Template
```
**System Information:**
- OS: [e.g., Ubuntu 20.04, macOS 12.0]
- Python Version: [e.g., 3.9.7]
- Pak Tool Version: [e.g., 5.0.0]

**Description:**
Clear description of the issue or feature request

**Steps to Reproduce:**
1. Run command...
2. Enter input...
3. Observe error...

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Additional Context:**
Any other relevant information
```

## Code Review Process

All contributions go through code review:

1. **Automated Checks**: Tests and linting must pass
2. **Manual Review**: Code quality, architecture fit, documentation
3. **Testing**: Reviewer tests the changes locally
4. **Discussion**: Address feedback and iterate as needed
5. **Approval**: Maintainer approves and merges

## Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Create issues for bugs or feature requests
- **Code Review**: Ask for feedback during PR review
- **Documentation**: Check README.md and analysys.md

## Recognition

Contributors are recognized in:
- Git commit history
- Release notes for significant contributions
- README.md contributor section (for major contributions)

Thank you for contributing to PakAgent! Your efforts help make LLM-assisted development more efficient and accessible.
