"""
Program a) prepare *.py *.md
Produces archive with all files compressed for review/changes to an LLM
"""
import os
import sys
import subprocess
from pathlib import Path
from pakagent_config import config, run_pak_command, safe_file_operation, logger, sanitize_file_pattern
def send_files(file_patterns):
    """Send files matching patterns to session archive"""
    if not file_patterns:
        file_patterns = ["*.py", "*.md"]
    
    # Sanitize all file patterns for security
    sanitized_patterns = []
    for pattern in file_patterns:
        try:
            sanitized_pattern = sanitize_file_pattern(pattern)
            sanitized_patterns.append(sanitized_pattern)
        except ValueError as e:
            logger.error(f"❌ Invalid file pattern '{pattern}': {e}")
            return False
    
    logger.info(f"Collecting files matching: {', '.join(sanitized_patterns)}")
    
    # Show git status and suggest workflow
    config.suggest_git_workflow()
    
    pak_extensions = []
    pak_paths = []
    for pattern in sanitized_patterns:
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
    
    logger.info(f"Packaging files to {config.archive_path}...")
    success, output = run_pak_command(pak_args)
    
    if success:
        if config.archive_path.exists():
            size = config.archive_path.stat().st_size
            logger.info(f"✅ Archive created: {config.archive_path} ({size:,} bytes)")
            
            # Safe file preview
            def preview_archive():
                with open(config.archive_path, 'r') as f:
                    lines = f.readlines()[:10]
                    logger.info("\nArchive preview (first 10 lines):")
                    for i, line in enumerate(lines, 1):
                        logger.info(f"{i:2}: {line.rstrip()}")
                    if len(lines) == 10:
                        logger.info("    ...")
            
            safe_file_operation(preview_archive)
        else:
            logger.error("❌ Archive file was not created")
            return False
    else:
        logger.error(f"❌ Failed to create archive: {output}")
        return False
    return True
def main():
    """Main function"""
    if len(sys.argv) == 1:
        # Default: let send_files handle default patterns
        file_patterns = []
        logger.info("Using default patterns: *.py *.md")
    else:
        file_patterns = sys.argv[1:]
        logger.info(f"Using specified patterns: {' '.join(file_patterns)}")
    success = send_files(file_patterns)
    if success:
        logger.info(f"\n🚀 Ready for next step: python modify.py 'your modification request'")
        logger.info(f"📁 Session directory: {config.session_dir}")
    else:
        sys.exit(1)
if __name__ == "__main__":
    main()
