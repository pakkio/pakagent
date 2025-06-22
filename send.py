"""
Program a) send *.py *.md
Produces archive with all files compressed for review/changes to an LLM
"""
import os
import sys
import subprocess
from pathlib import Path
from pakagent_config import config, run_pak_command, safe_file_operation
def send_files(file_patterns):
    """Send files matching patterns to session archive"""
    if not file_patterns:
        file_patterns = ["*.py", "*.md"]
    
    print(f"Collecting files matching: {', '.join(file_patterns)}")
    
    # Show git status and suggest workflow
    config.suggest_git_workflow()
    
    pak_extensions = []
    pak_paths = []
    for pattern in file_patterns:
        if pattern.startswith("*."):
            ext = pattern[2:]
            pak_extensions.append(ext)
        else:
            pak_paths.append(pattern)
    
    pak_args = []
    if pak_paths:
        pak_args.extend(pak_paths)
    else:
        pak_args.append(".")
    if pak_extensions:
        pak_args.extend(["-t", ",".join(pak_extensions)])
    pak_args.extend(["-c", "medium", "-o", str(config.archive_path)])
    
    print(f"Packaging files to {config.archive_path}...")
    success, output = run_pak_command(pak_args)
    
    if success:
        if config.archive_path.exists():
            size = config.archive_path.stat().st_size
            print(f"✅ Archive created: {config.archive_path} ({size:,} bytes)")
            
            # Safe file preview
            def preview_archive():
                with open(config.archive_path, 'r') as f:
                    lines = f.readlines()[:10]
                    print("\nArchive preview (first 10 lines):")
                    for i, line in enumerate(lines, 1):
                        print(f"{i:2}: {line.rstrip()}")
                    if len(lines) == 10:
                        print("    ...")
            
            safe_file_operation(preview_archive)
        else:
            print("❌ Archive file was not created")
            return False
    else:
        print(f"❌ Failed to create archive: {output}")
        return False
    return True
def main():
    """Main function"""
    if len(sys.argv) == 1:
        file_patterns = ["*.py", "*.md"]
        print("Using default patterns: *.py *.md")
    else:
        file_patterns = sys.argv[1:]
        print(f"Using specified patterns: {' '.join(file_patterns)}")
    success = send_files(file_patterns)
    if success:
        print(f"\n🚀 Ready for next step: python modify.py 'your modification request'")
        print(f"📁 Session directory: {config.session_dir}")
    else:
        sys.exit(1)
if __name__ == "__main__":
    main()