"""
Basic functionality tests for PakAgent
These tests verify core functionality without complex mocking
"""
import pytest
import sys
from pathlib import Path
import tempfile
import shutil

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestBasicFunctionality:
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_imports_work(self):
        """Test that all core modules can be imported"""
        import send
        import modify
        import apply
        import revert
        import show_answer
        import pakagent_config
        
        # Check main functions exist
        assert hasattr(send, 'main')
        assert hasattr(modify, 'main')
        assert hasattr(apply, 'main')
        assert hasattr(revert, 'main')
        assert hasattr(show_answer, 'main')
    
    def test_config_initialization(self):
        """Test config can be initialized"""
        import pakagent_config
        
        config = pakagent_config.PakAgentConfig()
        assert config is not None
        assert hasattr(config, 'session_dir')
        assert hasattr(config, 'archive_path')
        assert hasattr(config, 'answer_path')
        assert hasattr(config, 'fix_path')
    
    def test_send_file_patterns(self):
        """Test send file pattern processing"""
        import send
        
        # Test that send_files function exists and is callable
        assert hasattr(send, 'send_files')
        assert callable(send.send_files)
    
    def test_modify_text_classification(self):
        """Test modify text classification"""
        import modify
        
        # Test classify_request function
        assert hasattr(modify, 'classify_request')
        
        # Test with obvious text requests
        text_request = modify.classify_request("what do you think about this?")
        assert isinstance(text_request, bool)
        
        code_request = modify.classify_request("add logging to the function")
        assert isinstance(code_request, bool)
    
    def test_modify_llm_response_parsing(self):
        """Test LLM response parsing"""
        import modify
        
        # Test basic response parsing
        simple_response = "This is a simple text response"
        answer, pakdiff = modify.parse_llm_response(simple_response)
        assert answer.strip() == simple_response.strip()
        # pakdiff might contain the response if no PAKDIFF block found
        assert isinstance(pakdiff, str)
        
        # Test response with pakdiff
        response_with_pakdiff = """
        Analysis of changes.
        
        PAKDIFF_START
        @@ file.py @@
        +new line
        PAKDIFF_END
        """
        answer, pakdiff = modify.parse_llm_response(response_with_pakdiff)
        assert "Analysis" in answer
        assert "@@ file.py @@" in pakdiff
    
    def test_apply_file_checking(self):
        """Test apply file existence checking"""
        import apply
        
        # Test check_files_exist function
        assert hasattr(apply, 'check_files_exist')
        assert callable(apply.check_files_exist)
    
    def test_revert_archive_checking(self):
        """Test revert archive checking"""
        import revert
        
        # Test check_archive function
        assert hasattr(revert, 'check_archive')
        assert callable(revert.check_archive)
    
    def test_show_answer_file_reading(self):
        """Test show_answer file reading"""
        import show_answer
        
        # Test read_file function
        assert hasattr(show_answer, 'read_file')
        
        # Test with non-existent file
        result = show_answer.read_file("nonexistent.txt")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Error" in result[0] or "not found" in result[0]
    
    def test_show_answer_pakdiff_parsing(self):
        """Test show_answer pakdiff parsing"""
        import show_answer
        
        # Test parse_pakdiff function
        assert hasattr(show_answer, 'parse_pakdiff')
        
        pakdiff_lines = [
            "FILE: test.py",
            "FIND_METHOD: test_function",
            "REPLACE_WITH:",
            "def test_function():",
            "    pass"
        ]
        
        summary, content = show_answer.parse_pakdiff(pakdiff_lines)
        assert isinstance(summary, list)
        assert isinstance(content, dict)
    
    def test_pak_command_interface(self):
        """Test pak command interface"""
        import pakagent_config
        
        # Test run_pak_command function exists
        assert hasattr(pakagent_config, 'run_pak_command')
        assert callable(pakagent_config.run_pak_command)
        
        # Test check_required_files function
        assert hasattr(pakagent_config, 'check_required_files')
        assert callable(pakagent_config.check_required_files)
    
    def test_workflow_integration(self):
        """Test basic workflow integration"""
        import pakagent_config
        
        # Test that config paths are consistent
        config = pakagent_config.config
        
        # All paths should be Path objects under the same session directory
        assert isinstance(config.session_dir, str)
        assert isinstance(config.archive_path, Path)
        assert isinstance(config.answer_path, Path)
        assert isinstance(config.fix_path, Path)
        
        # Archive path should be under session_dir
        assert str(config.archive_path).startswith(str(config.session_dir))

if __name__ == "__main__":
    pytest.main([__file__, "-v"])