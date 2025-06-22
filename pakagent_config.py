#!/usr/bin/env python3
"""
PakAgent Configuration and Utilities
Centralized temp file management and git integration
"""
import os
import sys
import tempfile
import subprocess
import atexit
import shutil
import logging
import re
from pathlib import Path
from contextlib import contextmanager

class PakAgentConfig:
    """Centralized configuration and temp file management"""
    
    def __init__(self):
        # Determine base temp/session directory (env override or system temp)
        tmp_env = os.environ.get("PAKAGENT_TMP_DIR")
        if tmp_env:
            base_tmp = Path(tmp_env)
        else:
            base_tmp = Path(tempfile.gettempdir())
        # Ensure directory exists
        try:
            base_tmp.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        self.tmp_dir = base_tmp
        # Session directory (string) is the base temp directory
        self.session_dir = str(base_tmp)

        # Paths for archive, analysis, and fix files
        # File paths for archive, analysis, and fix
        self.archive_path = Path(self.session_dir) / "archive.txt"
        self.answer_path = Path(self.session_dir) / "answer"
        self.fix_path = Path(self.session_dir) / "fix"

        # Git integration flags
        self.is_git_repo = self.check_git_repo()
        self.original_branch = self.get_current_branch() if self.is_git_repo else None
        
    def cleanup(self):
        """Clean up temp files on exit - only if explicitly requested"""
        # Don't auto-cleanup session files to allow workflow continuity
        # Session cleanup happens when reset_session() is called
        pass
    
    def check_git_repo(self):
        """Check if current directory is a git repository"""
        try:
            result = subprocess.run(['git', 'rev-parse', '--git-dir'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_current_branch(self):
        """Get current git branch"""
        try:
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def check_git_status(self):
        """Check git status for uncommitted changes"""
        if not self.is_git_repo:
            return True, "Not a git repository"
        
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                changes = result.stdout.strip()
                if changes:
                    return False, f"Uncommitted changes:\n{changes}"
                return True, "Working directory clean"
        except Exception as e:
            return False, f"Git status check failed: {e}"
        
        return False, "Unknown git status"
    
    @contextmanager
    def git_branch_context(self, branch_name):
        """Context manager for safe git branch operations"""
        if not self.is_git_repo:
            yield
            return
        
        original_branch = self.get_current_branch()
        branch_created = False
        
        try:
            # Check if branch exists
            result = subprocess.run(['git', 'branch', '--list', branch_name], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                # Create new branch
                subprocess.run(['git', 'checkout', '-b', branch_name], 
                             capture_output=True, text=True, check=True)
                branch_created = True
                logger.info(f"✅ Created and switched to branch: {branch_name}")
            else:
                # Switch to existing branch
                subprocess.run(['git', 'checkout', branch_name], 
                             capture_output=True, text=True, check=True)
                logger.info(f"✅ Switched to branch: {branch_name}")
            
            yield
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git branch operation failed: {e}")
            raise
        finally:
            # Return to original branch
            if original_branch and original_branch != branch_name:
                try:
                    subprocess.run(['git', 'checkout', original_branch], 
                                 capture_output=True, text=True, check=True)
                    logger.info(f"✅ Returned to branch: {original_branch}")
                    
                    # Optionally clean up created branch
                    if branch_created:
                        response = input(f"Delete created branch '{branch_name}'? (y/N): ").strip().lower()
                        if response in ['y', 'yes']:
                            subprocess.run(['git', 'branch', '-d', branch_name], 
                                         capture_output=True, text=True)
                            logger.info(f"✅ Deleted branch: {branch_name}")
                except:
                    logger.warning(f"⚠️  Could not return to original branch: {original_branch}")
    
    def suggest_git_workflow(self):
        """Suggest git workflow for the current operation"""
        if not self.is_git_repo:
            logger.info("💡 Consider initializing git: git init")
            return
        
        clean, status = self.check_git_status()
        if not clean:
            logger.warning("⚠️  Git status:")
            logger.warning(status)
            logger.info("💡 Consider committing changes first: git add . && git commit -m 'Save work'")
        
        logger.info("💡 Suggested git workflow:")
        logger.info("   git checkout -b pakagent-changes")
        logger.info("   # Apply pakagent changes")
        logger.info("   git add .")
        logger.info("   git commit -m 'Apply pakagent modifications'")
        logger.info("   git checkout main && git merge pakagent-changes")
    
    def reset_session(self):
        """Reset the session by creating a new temp directory"""
        # Clean up current session
        try:
            if hasattr(self, 'session_dir') and Path(self.session_dir).exists():
                shutil.rmtree(self.session_dir)
        except Exception as e:
            logger.warning(f"Warning: Could not clean up old session directory: {e}")
        
        # Create new session
        self.session_dir = tempfile.mkdtemp(prefix="pakagent_")
        session_file = Path.home() / ".pakagent_session"
        with open(session_file, 'w') as f:
            f.write(self.session_dir)
        
        # Update paths
        self.archive_path = Path(self.session_dir) / "archive.txt"
        self.answer_path = Path(self.session_dir) / "answer"
        self.fix_path = Path(self.session_dir) / "fix"
        
        logger.info(f"🔄 Reset session directory: {self.session_dir}")
    
    def cleanup_session(self):
        """Clean up the current session completely"""
        try:
            if hasattr(self, 'session_dir') and Path(self.session_dir).exists():
                shutil.rmtree(self.session_dir)
            # Remove session file
            session_file = Path.home() / ".pakagent_session"
            if session_file.exists():
                session_file.unlink()
            logger.info("🧹 Session cleaned up successfully")
        except Exception as e:
            logger.warning(f"Warning: Could not clean up session: {e}")

# Global config instance
config = PakAgentConfig()

# Configure logging
def setup_logging():
    """Setup centralized logging configuration"""
    log_level = os.environ.get("PAKAGENT_LOG_LEVEL", "INFO").upper()
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logs directory if it doesn't exist
    logs_dir = Path.home() / ".pakagent" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=[
            logging.FileHandler(logs_dir / "pakagent.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set library loggers to WARNING to reduce noise
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    return logging.getLogger("pakagent")

# Setup logging on import
logger = setup_logging()

# Security functions
def sanitize_file_pattern(pattern):
    """Sanitize file patterns to prevent command injection"""
    if not isinstance(pattern, str):
        raise ValueError("File pattern must be a string")
    
    # Remove any dangerous characters
    dangerous_chars = [';', '&', '|', '`', '$', '(', ')', '{', '}', '<', '>', '"', "'", '\\']
    for char in dangerous_chars:
        if char in pattern:
            logger.warning(f"Removing dangerous character '{char}' from pattern: {pattern}")
            pattern = pattern.replace(char, '')
    
    # Ensure pattern is reasonable (alphanumeric, dots, stars, forward slashes only)
    if not re.match(r'^[a-zA-Z0-9_.*/-]+$', pattern):
        raise ValueError(f"Invalid file pattern: {pattern}")
    
    # Prevent path traversal
    if '..' in pattern:
        raise ValueError("Path traversal not allowed in file patterns")
    
    return pattern

def sanitize_file_path(path):
    """Sanitize file paths to prevent path traversal"""
    if not isinstance(path, (str, Path)):
        raise ValueError("Path must be a string or Path object")
    
    path_str = str(path)
    
    # Prevent path traversal
    if '..' in path_str:
        raise ValueError("Path traversal not allowed")
    
    # Ensure path doesn't start with dangerous prefixes
    dangerous_prefixes = ['/etc/', '/usr/', '/bin/', '/sbin/', '/root/', '/sys/', '/proc/']
    for prefix in dangerous_prefixes:
        if path_str.startswith(prefix):
            raise ValueError(f"Access to system directory {prefix} not allowed")
    
    return path_str

def mask_sensitive_data(text, patterns=None):
    """Mask sensitive data like API keys in log messages"""
    if not isinstance(text, str):
        return text
    
    if patterns is None:
        patterns = [
            # API keys (various formats)
            (r'Bearer\s+[A-Za-z0-9_-]{20,}', 'Bearer ***MASKED***'),
            (r'api[_-]?key["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})', r'api_key: "***MASKED***"'),
            (r'OPENROUTER_API_KEY["\']?\s*[:=]\s*["\']?([A-Za-z0-9_-]{20,})', r'OPENROUTER_API_KEY: "***MASKED***"'),
            # Keys in various contexts (key:, with key:, etc.)
            (r'key[:\s]+[A-Za-z0-9_-]{20,}', 'key: ***MASKED***'),
            # Test keys and similar patterns
            (r'test-key-[A-Za-z0-9_-]{20,}', '***MASKED***'),
            # Generic long alphanumeric strings that might be keys (more conservative)
            (r'[A-Za-z0-9_-]{45,}', '***MASKED***'),
        ]
    
    masked_text = text
    for pattern, replacement in patterns:
        masked_text = re.sub(pattern, replacement, masked_text, flags=re.IGNORECASE)
    
    return masked_text

def validate_pakdiff_content(content):
    """Validate pakdiff content format and safety"""
    if not isinstance(content, str):
        raise ValueError("Pakdiff content must be a string")
    
    if not content.strip():
        raise ValueError("Pakdiff content is empty")
    
    lines = content.split('\n')
    valid_sections = ['FILE:', 'FIND_METHOD:', 'UNTIL_EXCLUDE:', 'REPLACE_WITH:', 'SECTION:']
    
    file_count = 0
    in_replace_section = False
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        # Check for valid section headers
        if any(line.startswith(section) for section in valid_sections):
            if line.startswith('FILE:'):
                file_count += 1
                file_path = line[5:].strip()
                try:
                    sanitize_file_path(file_path)
                except ValueError as e:
                    raise ValueError(f"Invalid file path at line {line_num}: {e}")
            elif line.startswith('REPLACE_WITH:'):
                in_replace_section = True
            elif line.startswith(('FIND_METHOD:', 'UNTIL_EXCLUDE:', 'SECTION:')):
                in_replace_section = False
        elif in_replace_section:
            # Validate code content in REPLACE_WITH sections
            # Check for potentially dangerous code patterns
            dangerous_patterns = [
                r'import\s+os.*system',
                r'subprocess\.',
                r'eval\s*\(',
                r'exec\s*\(',
                r'__import__',
                r'open\s*\([^)]*["\'][/\\]etc',
            ]
            
            for pattern in dangerous_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    logger.warning(f"Potentially dangerous code pattern detected at line {line_num}: {pattern}")
    
    if file_count == 0:
        raise ValueError("No FILE: sections found in pakdiff")
    
    logger.info(f"Pakdiff validation completed: {file_count} files to modify")
    return True

def run_pak_command(args, timeout=300):
    """Execute pak command with proper error handling and input sanitization"""
    try:
        # Sanitize arguments to prevent command injection
        sanitized_args = []
        for arg in args:
            if isinstance(arg, str):
                # For file patterns and paths, apply appropriate sanitization
                if arg.startswith(('-t', '-o', '-ad', '-vd')) or '.' in arg or '/' in arg:
                    if arg not in ['-t', '-o', '-ad', '-vd', '-c', 'medium', 'smart', 'low']:
                        try:
                            if '*' in arg or '?' in arg:
                                arg = sanitize_file_pattern(arg)
                            else:
                                arg = sanitize_file_path(arg)
                        except ValueError as e:
                            logger.error(f"❌ Invalid argument: {e}")
                            return False, str(e)
                sanitized_args.append(arg)
            else:
                sanitized_args.append(str(arg))
        
        cmd = ["pak"] + sanitized_args
        # Mask sensitive data in command logging
        masked_cmd = [mask_sensitive_data(str(part)) for part in cmd]
        logger.info(f"Running: {' '.join(masked_cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            logger.info("✅ Pak command successful")
            return True, result.stdout
        else:
            # Mask sensitive data in error output
            masked_stderr = mask_sensitive_data(result.stderr)
            logger.error(f"❌ Pak command failed: {masked_stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        msg = f"pak command timed out after {timeout}s"
        logger.error(f"❌ {msg}")
        return False, msg
    except FileNotFoundError:
        msg = "pak command not found"
        logger.error(f"❌ Error: {msg}. Make sure pak is installed and in PATH.")
        return False, msg
    except Exception as e:
        masked_error = mask_sensitive_data(str(e))
        logger.error(f"❌ Error running pak command: {masked_error}")
        return False, str(e)

def safe_file_operation(operation, *args, **kwargs):
    """Wrapper for safe file operations with error handling"""
    try:
        return operation(*args, **kwargs)
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        return None
    except PermissionError as e:
        logger.error(f"❌ Permission denied: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ File operation failed: {e}")
        return None

def check_required_files(*file_paths):
    """Check if all required files exist"""
    missing = []
    for path in file_paths:
        if not Path(path).exists():
            missing.append(str(path))
    
    if missing:
        logger.error(f"❌ Missing required files: {', '.join(missing)}")
        return False
    return True
    
def get_requests_session(retries=5, backoff_factor=0.5, status_forcelist=None):
    """
    Create a requests.Session with retry strategy.
    Retries on specified HTTP status codes and connection errors.
    """
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    if status_forcelist is None:
        status_forcelist = [429, 500, 502, 503, 504]
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=["HEAD", "GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session
