"""
Program d) apply
Applies answer and fix (pakdiff) to current codebase with git integration
"""
import os
import sys
import subprocess
from pathlib import Path
from pakagent_config import config, run_pak_command, check_required_files
def check_files_exist():
    """Check if required files exist"""
    if not check_required_files(config.answer_path, config.fix_path):
        print("Run 'python modify.py \"your request\"' first to generate these files.")
        return False
    return True
def run_pak_apply(pakdiff_file):
    """Apply pakdiff using pak command"""
    args = ["-ad", str(pakdiff_file), "."]
    success, output = run_pak_command(args)
    if success and output:
        print("Output:", output)
    return success
def verify_pakdiff(pakdiff_file):
    """Verify pakdiff format before applying"""
    print("Verifying pakdiff format...")
    args = ["-vd", str(pakdiff_file)]
    success, output = run_pak_command(args, timeout=60)
    
    if success:
        print("✅ Pakdiff format is valid")
        return True
    elif "not found" in output or "not available" in output:
        print("⚠️  Pak verify command not available, skipping verification")
        return True
    else:
        print(f"❌ Pakdiff format validation failed: {output}")
        return False
def show_changes_preview():
    """Show a preview of what will be changed"""
    try:
        with open(config.answer_path, "r") as f:
            answer = f.read()
        with open(config.fix_path, "r") as f:
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
    """Main function with git integration"""
    print("🔧 Starting pakdiff application process...")
    
    if not check_files_exist():
        sys.exit(1)
    
    show_changes_preview()
    
    # Check git status
    if config.is_git_repo:
        clean, status = config.check_git_status()
        if not clean:
            print(f"\n⚠️  Git Status: {status}")
            if "--force" not in sys.argv:
                proceed = input("Continue anyway? (y/N): ").strip().lower()
                if proceed not in ['y', 'yes']:
                    print("❌ Application cancelled")
                    sys.exit(0)
    
    force_mode = "--force" in sys.argv
    use_git_branch = "--git-branch" in sys.argv or config.is_git_repo
    
    if not force_mode:
        if not confirm_apply():
            print("❌ Application cancelled")
            sys.exit(0)
    
    if not verify_pakdiff(config.fix_path):
        if not force_mode:
            print("❌ Pakdiff verification failed. Use --force to skip verification.")
            sys.exit(1)
        else:
            print("⚠️  Continuing despite verification failure (--force used)")
    
    print("\n🚀 Applying pakdiff to codebase...")
    
    if use_git_branch and config.is_git_repo:
        branch_name = "pakagent-changes"
        try:
            with config.git_branch_context(branch_name):
                success = run_pak_apply(config.fix_path)
                if success:
                    # Offer to commit changes
                    if not force_mode:
                        commit = input("Commit changes to this branch? (y/N): ").strip().lower()
                        if commit in ['y', 'yes']:
                            try:
                                subprocess.run(['git', 'add', '.'], check=True)
                                subprocess.run(['git', 'commit', '-m', 'Apply pakagent modifications'], check=True)
                                print("✅ Changes committed to branch")
                            except subprocess.CalledProcessError:
                                print("⚠️  Could not commit changes")
        except Exception as e:
            print(f"❌ Git branch operation failed: {e}")
            success = False
    else:
        success = run_pak_apply(config.fix_path)
    
    if success:
        print("\n✅ SUCCESS! Changes have been applied to your codebase.")
        if config.is_git_repo:
            print("📝 Next steps:")
            print("   git status          # See what changed")
            print("   git diff            # Review changes")
            print("   git add . && git commit -m 'Apply changes'  # Commit if satisfied")
        else:
            print("📝 Consider initializing git for better change tracking")
    else:
        print("\n❌ FAILED! Changes could not be applied.")
        print("💡 Use 'python revert.py' to restore original files if needed")
        sys.exit(1)
if __name__ == "__main__":
    main()