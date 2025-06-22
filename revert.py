#!/usr/bin/env python3
"""
Program e) revert - Restore original files from archive
Uses pak -x archive.txt to restore files to their original state
before any pakdiff modifications were applied.
"""
import os
import sys
import subprocess
from pathlib import Path
from pakagent_config import config, run_pak_command

def check_archive():
    """Check if archive file exists"""
    if not config.archive_path.exists():
        print(f"❌ Archive file {config.archive_path} not found")
        print("Run 'python send.py' first to create the archive")
        return False
    
    try:
        size = config.archive_path.stat().st_size
        print(f"📦 Archive found: {size:,} bytes")
        return True
    except Exception as e:
        print(f"❌ Error reading archive: {e}")
        return False

def confirm_revert():
    """Ask user to confirm revert operation"""
    print("\n⚠️  WARNING: This will restore all files to their original state!")
    print("   Any changes made after creating the archive will be LOST.")
    print("   Make sure you have committed important changes to git first.")
    
    while True:
        response = input("\nDo you want to continue? (yes/no): ").lower().strip()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")

def revert_files():
    """Revert files using pak -x"""
    print("🔄 Reverting files from archive...")
    args = ["-x", str(config.archive_path)]
    success, output = run_pak_command(args, timeout=60)
    
    if success:
        print("✅ Files successfully reverted to original state")
        if output.strip():
            print(f"📄 Output: {output.strip()}")
    
    return success

def main():
    """Main function"""
    print("🔙 PakAgent Revert Tool")
    print(f"Restores files to their original state from {config.archive_path}")
    
    # Check for --force flag
    force = '--force' in sys.argv
    
    if not check_archive():
        sys.exit(1)
    
    # Show git status
    if config.is_git_repo:
        clean, status = config.check_git_status()
        if not clean:
            print(f"\n⚠️  Current git status:\n{status}")
    
    # Confirm operation unless --force is used
    if not force and not confirm_revert():
        print("❌ Revert cancelled by user")
        sys.exit(1)
    
    if revert_files():
        print("\n🚀 Revert completed successfully!")
        print("💡 Next steps:")
        if config.is_git_repo:
            print("   git status           # Check what changed")
            print("   git diff             # Review the changes")
        print("   python send.py ...   # Create new archive if needed")
    else:
        print("❌ Revert failed")
        sys.exit(1)

if __name__ == "__main__":
    main()