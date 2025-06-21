#!/usr/bin/env python3
"""
Program a) send *.py *.md
Produces /tmp/archive.txt with all files compressed for review/changes to an LLM
"""

import os
import sys
import subprocess
from pathlib import Path

def run_pak_command(args):
    """Execute pak command with given arguments"""
    try:
        cmd = ["pak"] + args
        print(f"Running: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print("Pak command successful")
            return True, result.stdout
        else:
            print(f"Pak command failed: {result.stderr}")
            return False, result.stderr
            
    except subprocess.TimeoutExpired:
        print("Pak command timed out")
        return False, "Timeout"
    except FileNotFoundError:
        print("Error: 'pak' command not found. Make sure pak is installed and in PATH.")
        return False, "Command not found"
    except Exception as e:
        print(f"Error running pak command: {e}")
        return False, str(e)

def send_files(file_patterns):
    """Send files matching patterns to /tmp/archive.txt"""
    
    # Default patterns if none provided
    if not file_patterns:
        file_patterns = ["*.py", "*.md"]
    
    print(f"Collecting files matching: {', '.join(file_patterns)}")
    
    # Convert patterns to pak-compatible format
    pak_extensions = []
    pak_paths = []
    
    for pattern in file_patterns:
        if pattern.startswith("*."):
            # Extension pattern like *.py
            ext = pattern[2:]
            pak_extensions.append(ext)
        else:
            # File path or directory
            pak_paths.append(pattern)
    
    # Build pak command
    pak_args = []
    
    # Add paths (default to current directory if none specified)
    if pak_paths:
        pak_args.extend(pak_paths)
    else:
        pak_args.append(".")
    
    # Add extensions filter
    if pak_extensions:
        pak_args.extend(["-t", ",".join(pak_extensions)])
    
    # Add compression and output
    pak_args.extend(["-c", "smart", "-o", "/tmp/archive.txt"])
    
    print(f"Packaging files to /tmp/archive.txt...")
    success, output = run_pak_command(pak_args)
    
    if success:
        # Check if file was created and show stats
        archive_path = Path("/tmp/archive.txt")
        if archive_path.exists():
            size = archive_path.stat().st_size
            print(f"✅ Archive created: /tmp/archive.txt ({size:,} bytes)")
            
            # Show first few lines as preview
            try:
                with open(archive_path, 'r') as f:
                    lines = f.readlines()[:10]
                    print("\nArchive preview (first 10 lines):")
                    for i, line in enumerate(lines, 1):
                        print(f"{i:2}: {line.rstrip()}")
                    if len(lines) == 10:
                        print("    ...")
            except Exception as e:
                print(f"Could not preview archive: {e}")
        else:
            print("❌ Archive file was not created")
            return False
    else:
        print(f"❌ Failed to create archive: {output}")
        return False
    
    return True

def main():
    """Main function"""
    # Use default patterns if no arguments provided
    if len(sys.argv) == 1:
        file_patterns = ["*.py", "*.md"]  # Default patterns
        print("Using default patterns: *.py *.md")
    else:
        file_patterns = sys.argv[1:]
        print(f"Using specified patterns: {' '.join(file_patterns)}")
    
    success = send_files(file_patterns)
    
    if success:
        print("\n🚀 Ready for next step: python modify.py 'your modification request'")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()