import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import modify
from pakagent_config import config

class TestModify:
    
    def setup_method(self):
        """Setup for each test method"""
        self.test_dir = tempfile.mkdtemp()
        self.original_archive_path = config.archive_path
        self.original_answer_path = config.answer_path
        self.original_fix_path = config.fix_path
        
        config.archive_path = Path(self.test_dir) / "test_archive.txt"
        config.answer_path = Path(self.test_dir) / "test_answer.txt"
        config.fix_path = Path(self.test_dir) / "test_fix.txt"
    
    def teardown_method(self):
        """Cleanup after each test method"""
        config.archive_path = self.original_archive_path
        config.answer_path = self.original_answer_path
        config.fix_path = self.original_fix_path
        
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_read_archive_success(self):
        """Test successful archive reading"""
        content = "test archive content"
        config.archive_path.write_text(content)
        
        result = modify.read_archive()
        assert result == content
    
    def test_read_archive_missing_file(self):
        """Test reading non-existent archive"""
        result = modify.read_archive()
        assert result is None
    
    def test_read_archive_file_error(self):
        """Test reading archive with file error"""
        config.archive_path.write_text("content")
        config.archive_path.chmod(0o000)  # Remove read permissions
        
        result = modify.read_archive()
        assert result is None
        
        config.archive_path.chmod(0o644)  # Restore permissions
    
    @patch.dict(os.environ, {}, clear=True)
    def test_classify_request_no_api_key_text(self):
        """Test request classification without API key - text request"""
        result = modify.classify_request("what do you think about this code?")
        assert result is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_classify_request_no_api_key_code(self):
        """Test request classification without API key - code request"""
        result = modify.classify_request("add logging to the functions")
        assert result is False
    
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'})
    @patch('modify.requests.post')
    def test_classify_request_with_api_text(self, mock_post):
        """Test request classification with API - text response"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'TEXT_RESPONSE'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = modify.classify_request("explain this code")
        assert result is True
    
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'})
    @patch('modify.requests.post')
    def test_classify_request_with_api_code(self, mock_post):
        """Test request classification with API - code change"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'CODE_CHANGE'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = modify.classify_request("add error handling")
        assert result is False
    
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'})
    @patch('modify.requests.post')
    def test_classify_request_api_error(self, mock_post):
        """Test request classification with API error"""
        mock_post.side_effect = Exception("API Error")
        
        result = modify.classify_request("add logging")
        # Should fallback to keyword detection
        assert result is False
    
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'})
    @patch('requests.post')
    def test_call_llm_success(self, mock_post):
        """Test successful LLM API call"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'LLM response content'}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        result = modify.call_llm("test prompt", "test archive")
        assert result == "LLM response content"
    
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'})
    @patch('requests.post')
    def test_call_llm_failure(self, mock_post):
        """Test failed LLM API call"""
        mock_post.side_effect = Exception("API Error")
        
        result = modify.call_llm("test prompt", "test archive")
        assert result is None
    
    def test_parse_llm_response_code_change(self):
        """Test parsing LLM response for code changes"""
        response = """
        Analysis of the request.
        
        PAKDIFF_START
        # This is a pakdiff
        @@ file.py @@
        def function():
            pass
        PAKDIFF_END
        """
        
        answer, pakdiff = modify.parse_llm_response(response)
        
        assert "Analysis of the request" in answer
        assert "# This is a pakdiff" in pakdiff
        assert "@@ file.py @@" in pakdiff
    
    def test_parse_llm_response_text_only(self):
        """Test parsing LLM response for text-only responses"""
        response = "This is just a text response without any code changes."
        
        answer, pakdiff = modify.parse_llm_response(response)
        
        assert answer.strip() == response.strip()
        assert pakdiff.strip() == ""
    
    def test_parse_llm_response_multiple_pakdiff_blocks(self):
        """Test parsing LLM response with multiple pakdiff blocks"""
        response = """
        Analysis here.
        
        PAKDIFF_START
        First pakdiff block
        PAKDIFF_END
        
        More text.
        
        PAKDIFF_START
        Second pakdiff block
        PAKDIFF_END
        """
        
        answer, pakdiff = modify.parse_llm_response(response)
        
        assert "Analysis here" in answer
        assert "More text" in answer
        assert "First pakdiff block" in pakdiff
        assert "Second pakdiff block" in pakdiff
    
    @patch('modify.read_archive')
    @patch('modify.classify_request')
    @patch('modify.call_llm')
    @patch('modify.parse_llm_response')
    def test_process_instructions_text_response(self, mock_parse, mock_llm, mock_classify, mock_read):
        """Test processing instructions for text response"""
        mock_read.return_value = "archive content"
        mock_classify.return_value = True  # Text response
        mock_llm.return_value = "LLM text response"
        mock_parse.return_value = ("text response", "")
        
        modify.process_instructions("explain this code")
        
        mock_classify.assert_called_once_with("explain this code")
        mock_llm.assert_called_once()
        assert config.answer_path.exists()
        assert "text response" in config.answer_path.read_text()
    
    @patch('modify.read_archive')
    @patch('modify.classify_request')
    @patch('modify.call_llm')
    @patch('modify.parse_llm_response')
    def test_process_instructions_code_change(self, mock_parse, mock_llm, mock_classify, mock_read):
        """Test processing instructions for code changes"""
        mock_read.return_value = "archive content"
        mock_classify.return_value = False  # Code change
        mock_llm.return_value = "LLM response with pakdiff"
        mock_parse.return_value = ("analysis", "pakdiff content")
        
        modify.process_instructions("add logging")
        
        mock_classify.assert_called_once_with("add logging")
        mock_llm.assert_called_once()
        assert config.answer_path.exists()
        assert config.fix_path.exists()
        assert "analysis" in config.answer_path.read_text()
        assert "pakdiff content" in config.fix_path.read_text()
    
    @patch('modify.read_archive')
    def test_process_instructions_no_archive(self, mock_read):
        """Test processing instructions when archive is missing"""
        mock_read.return_value = None
        
        modify.process_instructions("test instruction")
        
        # Should not create output files when archive is missing
        assert not config.answer_path.exists()
        assert not config.fix_path.exists()
    
    @patch('modify.process_instructions')
    def test_main_with_args(self, mock_process):
        """Test main function with command line arguments"""
        with patch('sys.argv', ['modify.py', 'add', 'logging', 'to', 'functions']):
            modify.main()
        mock_process.assert_called_once_with("add logging to functions")
    
    @patch('builtins.input', return_value='test instruction')
    @patch('modify.process_instructions')
    def test_main_without_args(self, mock_process, mock_input):
        """Test main function without command line arguments"""
        with patch('sys.argv', ['modify.py']):
            modify.main()
        mock_process.assert_called_once_with("test instruction")