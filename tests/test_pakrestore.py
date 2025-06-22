import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import revert
from pakagent_config import config

class TestRevert:
    
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
    
    def test_check_archive_exists_success(self):
        """Test check_archive when archive exists"""
        config.archive_path.write_text("archive content")
        
        result = revert.check_archive()
        assert result is True
    
    def test_check_archive_exists_missing(self):
        """Test check_archive when archive is missing"""
        result = revert.check_archive()
        assert result is False
    
    @patch('revert.run_pak_command')
    def test_revert_files_success(self, mock_pak_command):
        """Test successful revert files"""
        mock_pak_command.return_value = (True, "Extracted successfully")
        
        result = revert.revert_files()
        
        assert result is True
        mock_pak_command.assert_called_once_with(["-x", str(config.archive_path)], timeout=60)
    
    @patch('revert.run_pak_command')
    def test_revert_files_failure(self, mock_pak_command):
        """Test failed revert files"""
        mock_pak_command.return_value = (False, "Extract failed")
        
        result = revert.revert_files()
        
        assert result is False
    
    def test_check_archive_basic(self):
        """Test basic archive checking functionality"""
        config.archive_path.write_text("archive content for preview")
        
        # This should not raise an exception
        result = revert.check_archive()
        assert result is True
    
    def test_check_archive_missing_archive(self):
        """Test checking missing archive"""
        # Should handle missing archive gracefully
        result = revert.check_archive()
        assert result is False
    
    def test_check_archive_large_archive(self):
        """Test checking large archive"""
        large_content = "line\n" * 1000  # Large content
        config.archive_path.write_text(large_content)
        
        # This should not raise an exception
        result = revert.check_archive()
        assert result is True
    
    @patch('revert.check_archive')
    @patch('revert.confirm_revert')
    @patch('revert.revert_files')
    def test_revert_changes_success(self, mock_revert, mock_confirm, mock_check):
        """Test successful revert changes"""
        mock_check.return_value = True
        mock_confirm.return_value = True
        mock_revert.return_value = True
        
        with patch('sys.argv', ['revert.py']):
            revert.main()
        
        mock_check.assert_called_once()
    
    @patch('revert.check_archive')
    @patch('sys.exit')
    def test_revert_changes_missing_archive(self, mock_exit, mock_check):
        """Test revert changes with missing archive"""
        mock_check.return_value = False
        
        with patch('sys.argv', ['revert.py']):
            revert.main()
        
        mock_check.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('revert.check_archive')
    @patch('revert.confirm_revert')
    @patch('sys.exit')
    def test_revert_changes_user_cancels(self, mock_exit, mock_confirm, mock_check):
        """Test revert changes when user cancels"""
        mock_check.return_value = True
        mock_confirm.return_value = False
        
        with patch('sys.argv', ['revert.py']):
            revert.main()
        
        mock_check.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('revert.check_archive')
    @patch('revert.revert_files')
    def test_revert_changes_force_mode(self, mock_revert, mock_check):
        """Test revert changes in force mode"""
        mock_check.return_value = True
        mock_revert.return_value = True
        
        with patch('sys.argv', ['revert.py', '--force']):
            revert.main()
        
        mock_check.assert_called_once()
        # Should skip user confirmation in force mode
        mock_revert.assert_called_once()
    
    @patch('revert.check_archive')
    @patch('revert.confirm_revert')
    @patch('revert.revert_files')
    @patch('sys.exit')
    def test_revert_changes_extract_failure(self, mock_exit, mock_revert, mock_confirm, mock_check):
        """Test revert changes when revert fails"""
        mock_check.return_value = True
        mock_confirm.return_value = True
        mock_revert.return_value = False
        
        with patch('sys.argv', ['revert.py']):
            revert.main()
        
        mock_revert.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('revert.check_archive')
    @patch('revert.revert_files')
    def test_main_with_force_flag(self, mock_revert, mock_check):
        """Test main function with --force flag"""
        mock_check.return_value = True
        mock_revert.return_value = True
        
        with patch('sys.argv', ['revert.py', '--force']):
            revert.main()
        
        mock_check.assert_called_once()
    
    @patch('revert.check_archive')
    @patch('revert.confirm_revert')
    @patch('revert.revert_files')
    def test_main_without_force_flag(self, mock_revert, mock_confirm, mock_check):
        """Test main function without --force flag"""
        mock_check.return_value = True
        mock_confirm.return_value = True
        mock_revert.return_value = True
        
        with patch('sys.argv', ['revert.py']):
            revert.main()
        
        mock_check.assert_called_once()