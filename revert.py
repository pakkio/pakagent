#!/usr/bin/env python3
"""
Program e) revert - Restore original files from archive
Uses pak -x /tmp/archive.txt to restore files to their original state
before any pakdiff modifications were applied.
"""
import os
import sys
import subprocess
from pathlib import Path

def check_pak_tool():
    """Check if pak tool is available"""
    try:
        result = subprocess.run(['pak', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Pak tool found: {result.stdout.strip()}")
            return True
        else:
            print("❌ Pak tool not working properly")
            return False
    except FileNotFoundError:
        print("❌ Pak tool not found in PATH")
        print("Install pak tool: https://github.com/your-pak-repo")
        return False
    except subprocess.TimeoutExpired:
        print("❌ Pak tool timeout")
        return False
    except Exception as e:
        print(f"❌ Error checking pak tool: {e}")
        return False

def check_archive():
    """Check if archive file exists"""
    archive_path = Path("/tmp/archive.txt")
    if not archive_path.exists():
        print("❌ Archive file /tmp/archive.txt not found")
        print("Run 'python send.py' first to create the archive")
        return False
    
    try:
        size = archive_path.stat().st_size
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
    try:
        print("🔄 Reverting files from archive...")
        result = subprocess.run(['pak', '-x', '/tmp/archive.txt'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ Files successfully reverted to original state")
            if result.stdout.strip():
                print(f"📄 Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Pak extraction failed (exit code {result.returncode})")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Pak extraction timeout (60s)")
        return False
    except Exception as e:
        print(f"❌ Error running pak extraction: {e}")
        return False

def main():
    """Main function"""
    print("🔙 PakAgent Revert Tool")
    print("Restores files to their original state from /tmp/archive.txt")
    
    # Check for --force flag
    force = '--force' in sys.argv
    
    if not check_pak_tool():
        sys.exit(1)
    
    if not check_archive():
        sys.exit(1)
    
    # Confirm operation unless --force is used
    if not force and not confirm_revert():
        print("❌ Revert cancelled by user")
        sys.exit(1)
    
    if revert_files():
        print("\n🚀 Revert completed successfully!")
        print("💡 Next steps:")
        print("   git status           # Check what changed")
        print("   git diff             # Review the changes")
        print("   python send.py ...   # Create new archive if needed")
    else:
        print("❌ Revert failed")
        sys.exit(1)

if __name__ == "__main__":
    main()