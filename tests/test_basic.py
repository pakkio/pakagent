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
        import prepare
        import pakmod
        import pakapply
        import pakrestore
        import pakdiff
        import pakagent_config
        
        # Check main functions exist
        assert hasattr(prepare, 'main')
        assert hasattr(pakmod, 'main')
        assert hasattr(pakapply, 'main')
        assert hasattr(pakrestore, 'main')
        assert hasattr(pakdiff, 'main')
    
    def test_config_initialization(self):
        """Test config can be initialized"""
        import pakagent_config
        
        config = pakagent_config.PakAgentConfig()
        assert config is not None
        assert hasattr(config, 'session_dir')
        assert hasattr(config, 'archive_path')
        assert hasattr(config, 'answer_path')
        assert hasattr(config, 'fix_path')
    
    def test_prepare_file_patterns(self):
        """Test prepare file pattern processing"""
        import prepare
        
        # Test that send_files function exists and is callable
        assert hasattr(prepare, 'send_files')
        assert callable(prepare.send_files)
    
    def test_pakmod_text_classification(self):
        """Test pakmod text classification"""
        import pakmod
        
        # Test classify_request function
        assert hasattr(pakmod, 'classify_request')
        
        # Test with obvious text requests
        text_request = pakmod.classify_request("what do you think about this?")
        assert isinstance(text_request, bool)
        
        code_request = pakmod.classify_request("add logging to the function")
        assert isinstance(code_request, bool)
    
    def test_pakmod_llm_response_parsing(self):
        """Test LLM response parsing"""
        import pakmod
        
        # Test basic response parsing
        simple_response = "This is a simple text response"
        answer, pakdiff = pakmod.parse_llm_response(simple_response)
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
        answer, pakdiff = pakmod.parse_llm_response(response_with_pakdiff)
        assert "Analysis" in answer
        assert "@@ file.py @@" in pakdiff
    
    def test_pakapply_file_checking(self):
        """Test pakapply file existence checking"""
        import pakapply
        
        # Test check_files_exist function
        assert hasattr(pakapply, 'check_files_exist')
        assert callable(pakapply.check_files_exist)
    
    def test_pakrestore_archive_checking(self):
        """Test pakrestore archive checking"""
        import pakrestore
        
        # Test check_archive function
        assert hasattr(pakrestore, 'check_archive')
        assert callable(pakrestore.check_archive)
    
    def test_pakdiff_file_reading(self):
        """Test pakdiff file reading"""
        import pakdiff
        
        # Test read_file function
        assert hasattr(pakdiff, 'read_file')
        
        # Test with non-existent file
        result = pakdiff.read_file("nonexistent.txt")
        assert isinstance(result, list)
        assert len(result) > 0
        assert "Error" in result[0] or "not found" in result[0]
    
    def test_pakdiff_pakdiff_parsing(self):
        """Test pakdiff pakdiff parsing"""
        import pakdiff
        
        # Test parse_pakdiff function
        assert hasattr(pakdiff, 'parse_pakdiff')
        
        pakdiff_lines = [
            "FILE: test.py",
            "FIND_METHOD: test_function",
            "REPLACE_WITH:",
            "def test_function():",
            "    pass"
        ]
        
        summary, content = pakdiff.parse_pakdiff(pakdiff_lines)
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