"""
Program d) apply
Applies /tmp/answer and /tmp/fix (pakdiff) to current codebase
"""
import os
import sys
import subprocess
from pathlib import Path
def check_files_exist():
    """Check if required files exist"""
    answer_path = Path("/tmp/answer")
    fix_path = Path("/tmp/fix")
    missing = []
    if not answer_path.exists():
        missing.append("/tmp/answer")
    if not fix_path.exists():
        missing.append("/tmp/fix")
    if missing:
        print(f"❌ Missing required files: {', '.join(missing)}")
        print("Run 'python modify.py \"your request\"' first to generate these files.")
        return False
    return True
def run_pak_apply(pakdiff_file):
    """Apply pakdiff using pak command"""
    try:
        cmd = ["pak", "-ad", pakdiff_file, "."]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            print("✅ Pakdiff applied successfully")
            if result.stdout:
                print("Output:", result.stdout)
            return True
        else:
            print(f"❌ Pakdiff application failed: {result.stderr}")
            if result.stdout:
                print("Output:", result.stdout)
            return False
    except subprocess.TimeoutExpired:
        print("❌ Pak apply command timed out")
        return False
    except FileNotFoundError:
        print("❌ Error: 'pak' command not found. Make sure pak is installed and in PATH.")
        return False
    except Exception as e:
        print(f"❌ Error running pak apply: {e}")
        return False
def verify_pakdiff(pakdiff_file):
    """Verify pakdiff format before applying"""
    try:
        cmd = ["pak", "-vd", pakdiff_file]
        print(f"Verifying pakdiff format...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("✅ Pakdiff format is valid")
            return True
        else:
            print(f"❌ Pakdiff format validation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Pakdiff verification timed out")
        return False
    except FileNotFoundError:
        print("⚠️  'pak' verify command not available, skipping verification")
        return True
    except Exception as e:
        print(f"⚠️  Error verifying pakdiff: {e}")
        return True
def show_changes_preview():
    """Show a preview of what will be changed"""
    try:
        with open("/tmp/answer", "r") as f:
            answer = f.read()
        with open("/tmp/fix", "r") as f:
            pakdiff = f.read()
        print("\n" + "="*50)
        print("CHANGES PREVIEW")
        print("="*50)
        print("\n📋 ANALYSIS:")
        print(answer[:500] + ("..." if len(answer) > 500 else ""))
        print("\n🔧 PAKDIFF SUMMARY:")
        lines = pakdiff.split('\n')
        files_affected = set()
        methods_affected = []
        for line in lines:
            if line.startswith("FILE:"):
                file_path = line[5:].strip()
                files_affected.add(file_path)
            elif line.startswith("FIND_METHOD:"):
                method = line[12:].strip()
                if method:
                    methods_affected.append(method)
        print(f"Files to modify: {len(files_affected)}")
        for file_path in sorted(files_affected):
            print(f"  - {file_path}")
        if methods_affected:
            print(f"Methods to modify: {len(methods_affected)}")
            for method in methods_affected[:5]:
                print(f"  - {method}")
            if len(methods_affected) > 5:
                print(f"  ... and {len(methods_affected) - 5} more")
        print("="*50)
    except Exception as e:
        print(f"⚠️  Could not show preview: {e}")
def confirm_apply():
    """Ask user for confirmation before applying changes"""
    try:
        response = input("\nApply these changes? (y/N): ").strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        print("\nCancelled by user")
        return False
def main():
    """Main function"""
    print("🔧 Starting pakdiff application process...")
    if not check_files_exist():
        sys.exit(1)
    show_changes_preview()
    if "--force" not in sys.argv:
        if not confirm_apply():
            print("❌ Application cancelled")
            sys.exit(0)
    if not verify_pakdiff("/tmp/fix"):
        if "--force" not in sys.argv:
            print("❌ Pakdiff verification failed. Use --force to skip verification.")
            sys.exit(1)
        else:
            print("⚠️  Continuing despite verification failure (--force used)")
    print("\n🚀 Applying pakdiff to codebase...")
    success = run_pak_apply("/tmp/fix")
    if success:
        print("\n✅ SUCCESS! Changes have been applied to your codebase.")
        print("📝 Don't forget to:")
        print("   - Review the changes with 'git diff'")
        print("   - Test your code")
        print("   - Commit the changes if satisfied")
    else:
        print("\n❌ FAILED! Changes could not be applied.")
        print("Check the error messages above for details.")
        sys.exit(1)
if __name__ == "__main__":
    main()