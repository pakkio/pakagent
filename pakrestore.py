#!/usr/bin/env python3
"""
Program e) pakrestore - Restore original files from archive
Uses pak -x archive.txt to restore files to their original state
before any pakdiff modifications were applied.
"""
import os
import sys
import subprocess
from pathlib import Path
from pakagent_config import config, run_pak_command, logger

def check_archive():
    """Check if archive file exists"""
    if not config.archive_path.exists():
        logger.info(f"❌ Archive file {config.archive_path} not found")
        logger.info("Run 'python send.py' first to create the archive")
        return False
    
    try:
        size = config.archive_path.stat().st_size
        logger.info(f"📦 Archive found: {size:,} bytes")
        return True
    except Exception as e:
        logger.info(f"❌ Error reading archive: {e}")
        return False

def confirm_revert():
    """Ask user to confirm revert operation"""
    logger.info("\n⚠️  WARNING: This will restore all files to their original state!")
    logger.info("   Any changes made after creating the archive will be LOST.")
    logger.info("   Make sure you have committed important changes to git first.")
    
    while True:
        response = input("\nDo you want to continue? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            logger.info("Please enter 'yes' or 'no'")

def revert_files():
    """Revert files using pak -x"""
    logger.info("🔄 Reverting files from archive...")
    args = ["-x", str(config.archive_path)]
    success, output = run_pak_command(args, timeout=60)
    
    if success:
        logger.info("✅ Files successfully reverted to original state")
        if output.strip():
            logger.info(f"📄 Output: {output.strip()}")
    
    return success

def main():
    """Main function"""
    logger.info("🔙 PakAgent Revert Tool")
    logger.info(f"Restores files to their original state from {config.archive_path}")
    
    # Check for --force flag
    force = '--force' in sys.argv
    
    if not check_archive():
        sys.exit(1)
    
    # Show git status
    if config.is_git_repo:
        clean, status = config.check_git_status()
        if not clean:
            logger.info(f"\n⚠️  Current git status:\n{status}")
    
    # Confirm operation unless --force is used
    if not force and not confirm_revert():
        logger.info("❌ Revert cancelled by user")
        sys.exit(1)
    
    if revert_files():
        logger.info("\n🚀 Revert completed successfully!")
        logger.info("💡 Next steps:")
        if config.is_git_repo:
            logger.info("   git status           # Check what changed")
            logger.info("   git diff             # Review the changes")
        logger.info("   python send.py ...   # Create new archive if needed")
    else:
        logger.info("❌ Revert failed")
        sys.exit(1)

if __name__ == "__main__":
    main()