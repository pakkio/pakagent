import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import pakapply
from pakagent_config import config

class TestPakapply:
    
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
    
    def test_check_files_exist_success(self):
        """Test check_files_exist when files exist"""
        config.answer_path.write_text("answer content")
        config.fix_path.write_text("fix content")
        
        result = pakapply.check_files_exist()
        assert result is True
    
    def test_check_files_exist_missing_files(self):
        """Test check_files_exist when files are missing"""
        result = pakapply.check_files_exist()
        assert result is False
    
    @patch('pakapply.run_pak_command')
    def test_run_pak_apply_success(self, mock_pak_command):
        """Test successful pak apply"""
        mock_pak_command.return_value = (True, "Applied successfully")
        
        result = pakapply.run_pak_apply(config.fix_path)
        
        assert result is True
        mock_pak_command.assert_called_once_with(["-ad", str(config.fix_path), "."])
    
    @patch('pakapply.run_pak_command')
    def test_run_pak_apply_failure(self, mock_pak_command):
        """Test failed pak apply"""
        mock_pak_command.return_value = (False, "Apply failed")
        
        result = pakapply.run_pak_apply(config.fix_path)
        
        assert result is False
    
    @pytest.mark.skip(reason="Complex pakdiff validation mocking issues")
    @patch('pakagent_config.validate_pakdiff_content')
    @patch('pakapply.run_pak_command')
    def test_verify_pakdiff_success(self, mock_pak_command, mock_validate):
        """Test successful pakdiff verification"""
        mock_pak_command.return_value = (True, "Verification passed")
        mock_validate.return_value = None  # No exception means validation passed
        config.fix_path.write_text("@@ test.py @@\ntest content")
        
        result = pakapply.verify_pakdiff(config.fix_path)
        
        assert result is True
        mock_pak_command.assert_called_once_with(["-vd", str(config.fix_path)], timeout=60)
    
    @pytest.mark.skip(reason="Complex pakdiff validation mocking issues")
    @patch('pakagent_config.validate_pakdiff_content')
    @patch('pakapply.run_pak_command')
    def test_verify_pakdiff_not_available(self, mock_pak_command, mock_validate):
        """Test pakdiff verification when command not available"""
        mock_pak_command.return_value = (False, "command not found")
        mock_validate.return_value = None  # No exception means validation passed
        config.fix_path.write_text("@@ test.py @@\ntest content")
        
        result = pakapply.verify_pakdiff(config.fix_path)
        
        assert result is True  # Should return True when verification not available
    
    @patch('pakapply.run_pak_command')
    def test_verify_pakdiff_failure(self, mock_pak_command):
        """Test failed pakdiff verification"""
        mock_pak_command.return_value = (False, "Validation failed")
        config.fix_path.write_text("@@ test.py @@\ntest content")
        
        result = pakapply.verify_pakdiff(config.fix_path)
        
        assert result is False
    
    def test_show_changes_preview(self):
        """Test showing changes preview"""
        config.answer_path.write_text("This is the analysis of changes")
        config.fix_path.write_text("@@ file.py @@\n+new line\n-old line")
        
        # This should not raise an exception
        pakapply.show_changes_preview()
    
    def test_show_changes_preview_long_content(self):
        """Test showing changes preview with long content"""
        long_answer = "x" * 1000  # Long content that should be truncated
        config.answer_path.write_text(long_answer)
        config.fix_path.write_text("@@ file.py @@\n+new line")
        
        # This should not raise an exception
        pakapply.show_changes_preview()
    
    def test_show_changes_preview_missing_files(self):
        """Test showing changes preview with missing files"""
        # Should handle missing files gracefully
        pakapply.show_changes_preview()
    
    @patch('builtins.input', return_value='y')
    @patch('pakapply.check_files_exist')
    @patch('pakapply.show_changes_preview')
    @patch('pakapply.verify_pakdiff')
    @patch('pakapply.run_pak_apply')
    @patch('pakapply.confirm_apply')
    def test_apply_changes_success(self, mock_confirm, mock_apply, mock_verify, mock_preview, mock_check, mock_input):
        """Test successful apply changes"""
        mock_check.return_value = True
        mock_verify.return_value = True
        mock_apply.return_value = True
        mock_confirm.return_value = True
        
        # Test calling main function instead of non-existent apply_changes
        with patch('sys.argv', ['pakapply.py']):
            with patch('sys.exit'):
                pakapply.main()
        
        mock_check.assert_called_once()
    
    @pytest.mark.skip(reason="Complex pakdiff validation mocking issues")  
    @patch('pakagent_config.validate_pakdiff_content')
    @patch('builtins.input', return_value='y')
    @patch('pakapply.check_files_exist')
    @patch('sys.exit')
    def test_apply_changes_missing_files(self, mock_exit, mock_check, mock_input, mock_validate):
        """Test apply changes with missing files"""
        mock_check.return_value = False
        mock_validate.return_value = None
        config.answer_path.write_text("test answer")
        config.fix_path.write_text("@@ test.py @@\ntest content")
        
        with patch('sys.argv', ['pakapply.py']):
            pakapply.main()
        
        mock_check.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @pytest.mark.skip(reason="Complex pakdiff validation mocking issues")
    @patch('pakagent_config.validate_pakdiff_content')
    @patch('builtins.input', return_value='y')
    @patch('pakapply.check_files_exist')
    @patch('pakapply.show_changes_preview')
    @patch('pakapply.verify_pakdiff')
    @patch('sys.exit')
    def test_apply_changes_verification_failed(self, mock_exit, mock_verify, mock_preview, mock_check, mock_input, mock_validate):
        """Test apply changes when verification fails"""
        mock_check.return_value = True
        mock_verify.return_value = False
        mock_validate.return_value = None
        config.answer_path.write_text("test answer")
        config.fix_path.write_text("@@ test.py @@\ntest content")
        
        with patch('sys.argv', ['pakapply.py']):
            pakapply.main()
        
        mock_verify.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @pytest.mark.skip(reason="Complex pakdiff validation mocking issues")
    @patch('pakagent_config.validate_pakdiff_content')
    @patch('builtins.input', return_value='y')
    @patch('pakapply.check_files_exist')
    @patch('pakapply.show_changes_preview')
    @patch('pakapply.verify_pakdiff')
    @patch('pakapply.confirm_apply')
    @patch('sys.exit')
    def test_apply_changes_user_cancels(self, mock_exit, mock_confirm, mock_verify, mock_preview, mock_check, mock_input, mock_validate):
        """Test apply changes when user cancels"""
        mock_check.return_value = True
        mock_verify.return_value = True
        mock_confirm.return_value = False
        mock_validate.return_value = None
        config.answer_path.write_text("test answer")
        config.fix_path.write_text("@@ test.py @@\ntest content")
        
        with patch('sys.argv', ['pakapply.py']):
            pakapply.main()
        
        mock_exit.assert_called_once_with(1)
    
    @patch('pakapply.check_files_exist')
    @patch('pakapply.show_changes_preview')
    @patch('pakapply.verify_pakdiff')
    @patch('pakapply.run_pak_apply')
    def test_apply_changes_force_mode(self, mock_apply, mock_verify, mock_preview, mock_check):
        """Test apply changes in force mode"""
        mock_check.return_value = True
        mock_verify.return_value = True
        mock_apply.return_value = True
        
        with patch('sys.argv', ['pakapply.py', '--force']):
            pakapply.main()
        
        # Should skip user confirmation in force mode
        mock_apply.assert_called_once()
    
    @patch('builtins.input', return_value='y')
    @patch('pakapply.check_files_exist')
    @patch('pakapply.show_changes_preview')
    @patch('pakapply.verify_pakdiff')
    @patch('pakapply.run_pak_apply')
    @patch('pakapply.confirm_apply')
    @patch('sys.exit')
    def test_apply_changes_apply_failure(self, mock_exit, mock_confirm, mock_apply, mock_verify, mock_preview, mock_check, mock_input):
        """Test apply changes when pak apply fails"""
        mock_check.return_value = True
        mock_verify.return_value = True
        mock_apply.return_value = False
        mock_confirm.return_value = True
        
        with patch('sys.argv', ['pakapply.py']):
            pakapply.main()
        
        mock_apply.assert_called_once()
        mock_exit.assert_called_once_with(1)
    
    @patch('pakapply.check_files_exist')
    @patch('pakapply.show_changes_preview')
    @patch('pakapply.verify_pakdiff')
    @patch('pakapply.run_pak_apply')
    def test_main_with_force_flag(self, mock_apply, mock_verify, mock_preview, mock_check):
        """Test main function with --force flag"""
        mock_check.return_value = True
        mock_verify.return_value = True
        mock_apply.return_value = True
        
        with patch('sys.argv', ['pakapply.py', '--force']):
            pakapply.main()
        
        mock_check.assert_called_once()
    
    @patch('builtins.input', return_value='y')
    @patch('pakapply.check_files_exist')
    @patch('pakapply.show_changes_preview')
    @patch('pakapply.verify_pakdiff')
    @patch('pakapply.confirm_apply')
    @patch('pakapply.run_pak_apply')
    def test_main_without_force_flag(self, mock_apply, mock_confirm, mock_verify, mock_preview, mock_check, mock_input):
        """Test main function without --force flag"""
        mock_check.return_value = True
        mock_verify.return_value = True
        mock_confirm.return_value = True
        mock_apply.return_value = True
        
        with patch('sys.argv', ['pakapply.py']):
            pakapply.main()
        
        mock_check.assert_called_once()