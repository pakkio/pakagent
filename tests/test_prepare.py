import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import prepare
from pakagent_config import config

class TestPrepare:
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp()
        self.original_archive_path = config.archive_path
        config.archive_path = Path(self.test_dir) / "test_archive.txt"
    
    def teardown_method(self):
        """Cleanup after each test method"""
        config.archive_path = self.original_archive_path
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    @patch('prepare.run_pak_command')
    @patch('pakagent_config.config.suggest_git_workflow')
    def test_send_files_default_patterns(self, mock_git_workflow, mock_pak_command):
        """Test send_files with default patterns"""
        mock_pak_command.return_value = (True, "Success")
        
        # Create mock archive file
        config.archive_path.write_text("mock archive content")
        
        prepare.send_files([])
        
        mock_pak_command.assert_called_once()
        args = mock_pak_command.call_args[0][0]
        assert "." in args
        assert "-t" in args
        assert "py,md" in args
        assert "-c" in args
        assert "medium" in args
        assert "-o" in args
        assert str(config.archive_path) in args
    
    @patch('prepare.run_pak_command')
    @patch('pakagent_config.config.suggest_git_workflow')
    def test_send_files_custom_patterns(self, mock_git_workflow, mock_pak_command):
        """Test send_files with custom patterns"""
        mock_pak_command.return_value = (True, "Success")
        config.archive_path.write_text("mock archive content")
        
        prepare.send_files(["*.js", "*.json"])
        
        mock_pak_command.assert_called_once()
        args = mock_pak_command.call_args[0][0]
        assert "-t" in args
        assert "js,json" in args
    
    @patch('prepare.run_pak_command')
    @patch('pakagent_config.config.suggest_git_workflow')
    def test_send_files_specific_paths(self, mock_git_workflow, mock_pak_command):
        """Test send_files with specific file paths"""
        mock_pak_command.return_value = (True, "Success")
        config.archive_path.write_text("mock archive content")
        
        prepare.send_files(["file1.py", "dir/file2.py"])
        
        mock_pak_command.assert_called_once()
        args = mock_pak_command.call_args[0][0]
        assert "file1.py" in args
        assert "dir/file2.py" in args
    
    @patch('prepare.run_pak_command')
    @patch('pakagent_config.config.suggest_git_workflow')
    def test_send_files_pak_failure(self, mock_git_workflow, mock_pak_command):
        """Test send_files when pak command fails"""
        mock_pak_command.return_value = (False, "Error message")
        
        prepare.send_files(["*.py"])
        
        mock_pak_command.assert_called_once()
    
    @patch('prepare.run_pak_command')
    @patch('pakagent_config.config.suggest_git_workflow')
    @patch('builtins.input', return_value='y')
    def test_send_files_with_preview(self, mock_input, mock_git_workflow, mock_pak_command):
        """Test send_files with archive preview"""
        mock_pak_command.return_value = (True, "Success")
        config.archive_path.write_text("line1\nline2\nline3\n" * 10)
        
        prepare.send_files(["*.py"])
        
        mock_pak_command.assert_called_once()
    
    @patch('prepare.send_files')
    def test_main_with_args(self, mock_send_files):
        """Test main function with command line arguments"""
        with patch('sys.argv', ['prepare.py', '*.py', '*.md']):
            prepare.main()
        mock_send_files.assert_called_once_with(['*.py', '*.md'])
    
    @patch('prepare.send_files')
    def test_main_without_args(self, mock_send_files):
        """Test main function without command line arguments"""
        with patch('sys.argv', ['prepare.py']):
            prepare.main()
        mock_send_files.assert_called_once_with([])