"""
Test configuration and fixtures for PakAgent tests
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def mock_env_clean():
    """Provide a clean environment for tests"""
    with patch.dict(os.environ, {}, clear=True):
        yield

@pytest.fixture
def mock_env_with_api_key():
    """Provide environment with API key for tests"""
    with patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_api_key'}):
        yield

@pytest.fixture
def sample_archive_content():
    """Provide sample archive content for tests"""
    return """# Sample Archive Content
This is a sample archive file for testing purposes.
It contains multiple lines of text to simulate
a real archive file created by the pak tool.

def sample_function():
    pass

class SampleClass:
    def method(self):
        return "test"
"""

@pytest.fixture
def sample_pakdiff_content():
    """Provide sample pakdiff content for tests"""
    return """@@ file.py @@
-old_function():
+new_function():
     pass

@@ another_file.py @@
+def new_function():
+    return "added"

## Global changes ##
s/old_pattern/new_pattern/g
"""

@pytest.fixture
def sample_answer_content():
    """Provide sample answer content for tests"""
    return """Analysis of the requested changes:

The user wants to add logging functionality to the codebase.
This will involve:
1. Adding import statements for logging
2. Creating logger instances
3. Adding log statements at key points

The changes will improve debugging and monitoring capabilities.
"""

@pytest.fixture
def git_repo(temp_dir):
    """Provide a temporary git repository for tests"""
    import subprocess
    
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    
    try:
        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True, check=True)
        
        # Create initial commit
        Path("README.md").write_text("# Test Repository")
        subprocess.run(["git", "add", "README.md"], capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], capture_output=True, check=True)
        
        yield temp_dir
        
    finally:
        os.chdir(original_cwd)

@pytest.fixture
def mock_pak_success():
    """Mock successful pak command execution"""
    def mock_run_pak_command(args, timeout=None):
        return True, "Success"
    
    with patch('pakagent_config.run_pak_command', side_effect=mock_run_pak_command):
        yield

@pytest.fixture
def mock_pak_failure():
    """Mock failed pak command execution"""
    def mock_run_pak_command(args, timeout=None):
        return False, "Error: pak command failed"
    
    with patch('pakagent_config.run_pak_command', side_effect=mock_run_pak_command):
        yield

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response"""
    return {
        'choices': [{
            'message': {
                'content': '''Analysis of the changes requested.

PAKDIFF_START
@@ test.py @@
+# Added logging
+import logging
+logger = logging.getLogger(__name__)
PAKDIFF_END
'''
            }
        }]
    }

@pytest.fixture(autouse=True)
def reset_config():
    """Reset config state between tests"""
    # This ensures each test starts with a clean config state
    yield
    
    # Any cleanup needed after tests
    pass