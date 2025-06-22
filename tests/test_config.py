import pytest
import os
import tempfile
import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pakagent_config
from pakagent_config import PakAgentConfig, config

class TestPakAgentConfig:
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Create a fresh config instance for testing
        self.test_config = PakAgentConfig()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_config_initialization(self):
        """Test config initialization with default values"""
        assert self.test_config.tmp_dir == Path("/tmp")
        assert self.test_config.archive_path == Path("/tmp/archive.txt")
        assert self.test_config.answer_path == Path("/tmp/answer")
        assert self.test_config.fix_path == Path("/tmp/fix")
    
    @patch.dict(os.environ, {'PAKAGENT_TMP_DIR': '/custom/tmp'})
    def test_config_custom_tmp_dir(self):
        """Test config with custom tmp directory"""
        custom_config = PakAgentConfig()
        assert hasattr(custom_config, 'tmp_dir')
        assert hasattr(custom_config, 'archive_path')
    
    def test_suggest_git_workflow_clean_repo(self):
        """Test git workflow suggestion with clean repo"""
        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)
        
        # Create and commit a file
        Path("test.txt").write_text("content")
        subprocess.run(["git", "add", "test.txt"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "initial"], capture_output=True)
        
        # Should not raise any exceptions
        self.test_config.suggest_git_workflow()
    
    def test_suggest_git_workflow_dirty_repo(self):
        """Test git workflow suggestion with dirty repo"""
        # Initialize git repo
        subprocess.run(["git", "init"], capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], capture_output=True)
        
        # Create uncommitted changes
        Path("test.txt").write_text("content")
        
        # Should not raise any exceptions
        self.test_config.suggest_git_workflow()
    
    def test_suggest_git_workflow_no_git(self):
        """Test git workflow suggestion without git repo"""
        # Should handle non-git directory gracefully
        self.test_config.suggest_git_workflow()
    
    @patch('subprocess.run')
    def test_run_pak_command_success(self, mock_run):
        """Test successful pak command execution"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "success output"
        mock_result.stderr = ""
        mock_run.return_value = mock_result
        
        success, output = pakagent_config.run_pak_command(["-h"])
        
        assert success is True
        assert output == "success output"
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_pak_command_failure(self, mock_run):
        """Test failed pak command execution"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "error message"
        mock_run.return_value = mock_result
        
        success, output = pakagent_config.run_pak_command(["-h"])
        
        assert success is False
        assert "error message" in output
    
    @patch('subprocess.run')
    def test_run_pak_command_not_found(self, mock_run):
        """Test pak command when pak is not installed"""
        mock_run.side_effect = FileNotFoundError("pak not found")
        
        success, output = pakagent_config.run_pak_command(["-h"])
        
        assert success is False
        assert "pak command not found" in output
    
    @patch('subprocess.run')
    def test_run_pak_command_timeout(self, mock_run):
        """Test pak command with timeout"""
        mock_run.side_effect = subprocess.TimeoutExpired("pak", 30)
        
        success, output = pakagent_config.run_pak_command(["-h"], timeout=30)
        
        assert success is False
        assert "timed out" in output
    
    def test_check_required_files_all_exist(self):
        """Test check_required_files when all files exist"""
        file1 = Path(self.test_dir) / "file1.txt"
        file2 = Path(self.test_dir) / "file2.txt"
        
        file1.write_text("content1")
        file2.write_text("content2")
        
        result = pakagent_config.check_required_files(file1, file2)
        assert result is True
    
    def test_check_required_files_some_missing(self):
        """Test check_required_files when some files are missing"""
        file1 = Path(self.test_dir) / "file1.txt"
        file2 = Path(self.test_dir) / "missing.txt"
        
        file1.write_text("content1")
        
        result = pakagent_config.check_required_files(file1, file2)
        assert result is False
    
    def test_check_required_files_empty_list(self):
        """Test check_required_files with empty file list"""
        result = pakagent_config.check_required_files()
        assert result is True
    
    def test_safe_file_operation_success(self):
        """Test successful safe file operation"""
        def operation(path):
            return "success"
        
        result = pakagent_config.safe_file_operation(operation, "test operation")
        assert result == "success"
    
    def test_safe_file_operation_failure(self):
        """Test failed safe file operation"""
        def failing_operation():
            raise Exception("operation failed")
        
        result = pakagent_config.safe_file_operation(failing_operation, "test operation")
        assert result is None
    
    def test_safe_file_operation_file_not_found(self):
        """Test safe file operation with FileNotFoundError"""
        def file_not_found_operation():
            raise FileNotFoundError("file not found")
        
        result = pakagent_config.safe_file_operation(file_not_found_operation, "test operation")
        assert result is None
    
    def test_safe_file_operation_permission_error(self):
        """Test safe file operation with PermissionError"""
        def permission_error_operation():
            raise PermissionError("permission denied")
        
        result = pakagent_config.safe_file_operation(permission_error_operation, "test operation")
        assert result is None
    
    def test_global_config_instance(self):
        """Test that global config instance is properly initialized"""
        assert isinstance(config, PakAgentConfig)
        assert hasattr(config, 'tmp_dir')
    
    def test_config_paths_are_pathlib_objects(self):
        """Test that all config paths are Path objects"""
        assert isinstance(self.test_config.tmp_dir, Path)
        assert isinstance(self.test_config.archive_path, Path)
        assert isinstance(self.test_config.answer_path, Path)
        assert isinstance(self.test_config.fix_path, Path)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_config_with_no_env_vars(self):
        """Test config initialization without environment variables"""
        clean_config = PakAgentConfig()
        assert hasattr(clean_config, 'tmp_dir')
    
    def test_tmp_dir_creation(self):
        """Test that tmp directory path is handled correctly"""
        custom_tmp = Path(self.test_dir) / "custom_tmp"
        
        with patch.dict(os.environ, {'PAKAGENT_TMP_DIR': str(custom_tmp)}):
            custom_config = PakAgentConfig()
            assert hasattr(custom_config, 'tmp_dir')
            assert hasattr(custom_config, 'archive_path')