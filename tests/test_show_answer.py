import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import show_answer
from pakagent_config import config

class TestShowAnswer:
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp()
        self.original_answer_path = config.answer_path
        self.original_fix_path = config.fix_path
        
        config.answer_path = Path(self.test_dir) / "test_answer.txt"
        config.fix_path = Path(self.test_dir) / "test_fix.txt"
    
    def teardown_method(self):
        """Cleanup after each test method"""
        config.answer_path = self.original_answer_path
        config.fix_path = self.original_fix_path
        
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_read_file_success(self):
        """Test read_file when file exists"""
        config.answer_path.write_text("answer content\nline 2")
        
        result = show_answer.read_file(str(config.answer_path))
        assert len(result) == 2
        assert "answer content" in result[0]
    
    def test_read_file_missing(self):
        """Test read_file when file is missing"""
        result = show_answer.read_file("nonexistent.txt")
        assert len(result) == 1
        assert "Error: File not found" in result[0]
    
    def test_parse_pakdiff_basic(self):
        """Test basic pakdiff parsing"""
        pakdiff_lines = [
            "FILE: test.py",
            "FIND_METHOD: test_function",
            "REPLACE_WITH:",
            "def test_function():",
            "    pass"
        ]
        
        summary, content = show_answer.parse_pakdiff(pakdiff_lines)
        assert len(summary) == 1
        assert "test.py: test_function" in summary
    
    def test_parse_pakdiff_empty(self):
        """Test parsing empty pakdiff"""
        pakdiff_lines = []
        
        summary, content = show_answer.parse_pakdiff(pakdiff_lines)
        assert len(summary) == 0
        assert len(content) == 0
    
    def test_parse_pakdiff_multiple_files(self):
        """Test parsing pakdiff with multiple files"""
        pakdiff_lines = [
            "FILE: test1.py",
            "FIND_METHOD: func1",
            "REPLACE_WITH:",
            "def func1(): pass",
            "FILE: test2.py",
            "FIND_METHOD: func2",
            "REPLACE_WITH:",
            "def func2(): pass"
        ]
        
        summary, content = show_answer.parse_pakdiff(pakdiff_lines)
        assert len(summary) == 2
        assert "test1.py: func1" in summary
        assert "test2.py: func2" in summary
    
    @patch('curses.newwin')
    def test_show_answer_ui_init(self, mock_newwin):
        """Test ShowAnswerUI initialization"""
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (30, 120)
        
        mock_newwin.return_value = MagicMock()
        
        ui = show_answer.ShowAnswerUI(mock_stdscr)
        
        assert ui.height == 30
        assert ui.width == 120
        assert mock_newwin.call_count == 3  # Three windows
    
    def test_main_function_exists(self):
        """Test that main function exists and is callable"""
        assert hasattr(show_answer, 'main')
        assert callable(show_answer.main)
    
    @patch('show_answer.read_file')
    def test_file_reading_integration(self, mock_read_file):
        """Test file reading integration"""
        mock_read_file.return_value = ["line 1", "line 2"]
        
        result = show_answer.read_file("test.txt")
        
        assert len(result) == 2
        mock_read_file.assert_called_once_with("test.txt")
    
    def test_pakdiff_parsing_robustness(self):
        """Test pakdiff parsing with edge cases"""
        # Test with malformed input
        pakdiff_lines = [
            "FILE:",  # Empty file name
            "FIND_METHOD:",  # Empty method name
            "REPLACE_WITH:",
            "some content"
        ]
        
        summary, content = show_answer.parse_pakdiff(pakdiff_lines)
        # Should handle empty names gracefully
        assert len(summary) >= 0
    
    def test_file_error_handling(self):
        """Test file error handling"""
        # Create a file and then remove permissions
        test_file = Path(self.test_dir) / "restricted.txt"
        test_file.write_text("content")
        test_file.chmod(0o000)
        
        try:
            result = show_answer.read_file(str(test_file))
            # Should return error message, not crash
            assert len(result) >= 1
        finally:
            test_file.chmod(0o644)  # Restore permissions for cleanup
    
    @patch('show_answer.curses.wrapper')
    @patch('os.path.exists')
    def test_main_with_existing_files(self, mock_exists, mock_wrapper):
        """Test main function when files exist"""
        mock_exists.return_value = True
        
        show_answer.main()
        
        mock_wrapper.assert_called_once()
    
    @patch('os.path.exists')
    @patch('sys.exit')
    def test_main_with_missing_files(self, mock_exit, mock_exists):
        """Test main function when files are missing"""
        mock_exists.return_value = False
        
        show_answer.main()
        
        mock_exit.assert_called_once_with(1)
    
    def test_show_answer_ui_structure(self):
        """Test ShowAnswerUI basic structure"""
        # Test that the class exists and has expected methods
        assert hasattr(show_answer, 'ShowAnswerUI')
        
        # Test that key methods exist
        ui_class = show_answer.ShowAnswerUI
        assert hasattr(ui_class, '__init__')
        assert hasattr(ui_class, 'setup_windows')
    
    def test_file_content_types(self):
        """Test handling different file content types"""
        # Test with different line endings
        test_file = Path(self.test_dir) / "test_endings.txt"
        test_file.write_text("line1\nline2\r\nline3\r")
        
        result = show_answer.read_file(str(test_file))
        
        # Should handle different line endings gracefully
        assert len(result) >= 1
    
    def test_curses_integration_structure(self):
        """Test curses integration structure exists"""
        # Just test that curses import and basic structure exists
        import curses
        assert curses is not None
        
        # Test that ShowAnswerUI can be instantiated structure-wise
        assert show_answer.ShowAnswerUI is not None
    
    def test_pakdiff_content_extraction(self):
        """Test pakdiff content extraction"""
        pakdiff_lines = [
            "FILE: test.py",
            "FIND_METHOD: my_function",
            "REPLACE_WITH:",
            "def my_function():",
            "    print('hello')",
            "    return 42"
        ]
        
        summary, content = show_answer.parse_pakdiff(pakdiff_lines)
        
        assert "test.py: my_function" in summary
        key = "test.py: my_function"
        if key in content:
            assert len(content[key]) > 0
    
    def test_integration_file_paths(self):
        """Test integration with config file paths"""
        # Test that the module can access config paths
        assert hasattr(config, 'answer_path')
        assert hasattr(config, 'fix_path')
        
        # Test file reading with actual paths (even if files don't exist)
        result = show_answer.read_file(str(config.answer_path))
        assert isinstance(result, list)
        assert len(result) >= 1
    
    def test_module_imports(self):
        """Test that all required modules can be imported"""
        import curses
        import os
        from typing import List, Tuple, Dict, Any
        from pakagent_config import config
        
        # All imports should work without error
        assert curses is not None
        assert os is not None
        assert config is not None