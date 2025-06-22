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
from pathlib import Path
from contextlib import contextmanager

class PakAgentConfig:
    """Centralized configuration and temp file management"""
    
    def __init__(self):
        # Use persistent session directory across program runs
        session_file = Path.home() / ".pakagent_session"
        
        if session_file.exists():
            # Reuse existing session directory
            with open(session_file, 'r') as f:
                self.session_dir = f.read().strip()
            if not Path(self.session_dir).exists():
                # Session dir was cleaned up, create new one
                self.session_dir = tempfile.mkdtemp(prefix="pakagent_")
                with open(session_file, 'w') as f:
                    f.write(self.session_dir)
        else:
            # Create new session directory
            self.session_dir = tempfile.mkdtemp(prefix="pakagent_")
            with open(session_file, 'w') as f:
                f.write(self.session_dir)
        
        self.archive_path = Path(self.session_dir) / "archive.txt"
        self.answer_path = Path(self.session_dir) / "answer"
        self.fix_path = Path(self.session_dir) / "fix"
        
        # Register cleanup
        atexit.register(self.cleanup)
        
        # Git integration
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
                print(f"✅ Created and switched to branch: {branch_name}")
            else:
                # Switch to existing branch
                subprocess.run(['git', 'checkout', branch_name], 
                             capture_output=True, text=True, check=True)
                print(f"✅ Switched to branch: {branch_name}")
            
            yield
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git branch operation failed: {e}")
            raise
        finally:
            # Return to original branch
            if original_branch and original_branch != branch_name:
                try:
                    subprocess.run(['git', 'checkout', original_branch], 
                                 capture_output=True, text=True, check=True)
                    print(f"✅ Returned to branch: {original_branch}")
                    
                    # Optionally clean up created branch
                    if branch_created:
                        response = input(f"Delete created branch '{branch_name}'? (y/N): ").strip().lower()
                        if response in ['y', 'yes']:
                            subprocess.run(['git', 'branch', '-d', branch_name], 
                                         capture_output=True, text=True)
                            print(f"✅ Deleted branch: {branch_name}")
                except:
                    print(f"⚠️  Could not return to original branch: {original_branch}")
    
    def suggest_git_workflow(self):
        """Suggest git workflow for the current operation"""
        if not self.is_git_repo:
            print("💡 Consider initializing git: git init")
            return
        
        clean, status = self.check_git_status()
        if not clean:
            print("⚠️  Git status:")
            print(status)
            print("💡 Consider committing changes first: git add . && git commit -m 'Save work'")
        
        print("💡 Suggested git workflow:")
        print("   git checkout -b pakagent-changes")
        print("   # Apply pakagent changes")
        print("   git add .")
        print("   git commit -m 'Apply pakagent modifications'")
        print("   git checkout main && git merge pakagent-changes")
    
    def reset_session(self):
        """Reset the session by creating a new temp directory"""
        # Clean up current session
        try:
            if hasattr(self, 'session_dir') and Path(self.session_dir).exists():
                shutil.rmtree(self.session_dir)
        except Exception as e:
            print(f"Warning: Could not clean up old session directory: {e}")
        
        # Create new session
        self.session_dir = tempfile.mkdtemp(prefix="pakagent_")
        session_file = Path.home() / ".pakagent_session"
        with open(session_file, 'w') as f:
            f.write(self.session_dir)
        
        # Update paths
        self.archive_path = Path(self.session_dir) / "archive.txt"
        self.answer_path = Path(self.session_dir) / "answer"
        self.fix_path = Path(self.session_dir) / "fix"
        
        print(f"🔄 Reset session directory: {self.session_dir}")
    
    def cleanup_session(self):
        """Clean up the current session completely"""
        try:
            if hasattr(self, 'session_dir') and Path(self.session_dir).exists():
                shutil.rmtree(self.session_dir)
            # Remove session file
            session_file = Path.home() / ".pakagent_session"
            if session_file.exists():
                session_file.unlink()
            print("🧹 Session cleaned up successfully")
        except Exception as e:
            print(f"Warning: Could not clean up session: {e}")

# Global config instance
config = PakAgentConfig()

def run_pak_command(args, timeout=300):
    """Execute pak command with proper error handling"""
    try:
        cmd = ["pak"] + args
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print("✅ Pak command successful")
            return True, result.stdout
        else:
            print(f"❌ Pak command failed: {result.stderr}")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print(f"❌ Pak command timed out after {timeout}s")
        return False, "Timeout"
    except FileNotFoundError:
        print("❌ Error: 'pak' command not found. Make sure pak is installed and in PATH.")
        return False, "Command not found"
    except Exception as e:
        print(f"❌ Error running pak command: {e}")
        return False, str(e)

def safe_file_operation(operation, *args, **kwargs):
    """Wrapper for safe file operations with error handling"""
    try:
        return operation(*args, **kwargs)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return None
    except PermissionError as e:
        print(f"❌ Permission denied: {e}")
        return None
    except Exception as e:
        print(f"❌ File operation failed: {e}")
        return None

def check_required_files(*file_paths):
    """Check if all required files exist"""
    missing = []
    for path in file_paths:
        if not Path(path).exists():
            missing.append(str(path))
    
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        return False
    return True