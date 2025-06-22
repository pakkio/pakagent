"""
Program d) apply
Applies answer and fix (pakdiff) to current codebase with git integration
"""
import os
import sys
import subprocess
from pathlib import Path
from pakagent_config import config, run_pak_command, check_required_files, logger, validate_pakdiff_content
def check_files_exist():
    """Check if required files exist"""
    if not check_required_files(config.answer_path, config.fix_path):
        logger.error("Run 'python modify.py \"your request\"' first to generate these files.")
        return False
    return True
def run_pak_apply(pakdiff_file):
    """Apply pakdiff using pak command"""
    args = ["-ad", str(pakdiff_file), "."]
    success, output = run_pak_command(args)
    if success and output:
        logger.info("Output:", output)
    return success
def verify_pakdiff(pakdiff_file):
    """Verify pakdiff format and content safety before applying"""
    logger.info("Verifying pakdiff format and content...")
    
    # First, validate the content for security
    try:
        with open(pakdiff_file, 'r') as f:
            content = f.read()
        
        # Validate pakdiff content for security and format
        validate_pakdiff_content(content)
        logger.info("✅ Pakdiff content validation passed")
        
    except Exception as e:
        logger.error(f"❌ Pakdiff content validation failed: {e}")
        return False
    
    # Then use pak tool verification if available
    args = ["-vd", str(pakdiff_file)]
    success, output = run_pak_command(args, timeout=60)
    
    if success:
        logger.info("✅ Pakdiff format is valid")
        return True
    elif "not found" in output or "not available" in output:
        logger.warning("⚠️  Pak verify command not available, content validation only")
        return True
    else:
        logger.error(f"❌ Pakdiff format validation failed: {output}")
        return False
def show_changes_preview():
    """Show a preview of what will be changed"""
    try:
        with open(config.answer_path, "r") as f:
            answer = f.read()
        with open(config.fix_path, "r") as f:
            pakdiff = f.read()
        
        logger.info("\n" + "="*50)
        logger.info("CHANGES PREVIEW")
        logger.info("="*50)
        logger.info("\n📋 ANALYSIS:")
        logger.info(answer[:500] + ("..." if len(answer) > 500 else ""))
        
        logger.info("\n🔧 PAKDIFF SUMMARY:")
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
        
        logger.info(f"Files to modify: {len(files_affected)}")
        for file_path in sorted(files_affected):
            logger.info(f"  - {file_path}")
        
        if methods_affected:
            logger.info(f"Methods to modify: {len(methods_affected)}")
            for method in methods_affected[:5]:
                logger.info(f"  - {method}")
            if len(methods_affected) > 5:
                logger.info(f"  ... and {len(methods_affected) - 5} more")
        
        logger.info("="*50)
    except Exception as e:
        logger.warning(f"⚠️  Could not show preview: {e}")
def confirm_apply():
    """Ask user for confirmation before applying changes"""
    try:
        response = input("\nApply these changes? (y/N): ").strip().lower()
        return response in ['y', 'yes']
    except KeyboardInterrupt:
        logger.info("\nCancelled by user")
        return False
def main():
    """Main function with git integration"""
    logger.info("🔧 Starting pakdiff application process...")
    
    if not check_files_exist():
        sys.exit(1)
    
    show_changes_preview()
    
    # Check git status
    if config.is_git_repo:
        clean, status = config.check_git_status()
        if not clean:
            logger.warning(f"\n⚠️  Git Status: {status}")
            if "--force" not in sys.argv:
                proceed = input("Continue anyway? (y/N): ").strip().lower()
                if proceed not in ['y', 'yes']:
                    logger.info("❌ Application cancelled")
                    sys.exit(0)
    
    force_mode = "--force" in sys.argv
    # Only use git branch context if explicitly requested
    use_git_branch = ("--git-branch" in sys.argv) and config.is_git_repo
    
    if not force_mode:
        if not confirm_apply():
            logger.info("❌ Application cancelled")
            sys.exit(0)
    
    if not verify_pakdiff(config.fix_path):
        if not force_mode:
            logger.error("❌ Pakdiff verification failed. Use --force to skip verification.")
            sys.exit(1)
        else:
            logger.warning("⚠️  Continuing despite verification failure (--force used)")
    
    logger.info("\n🚀 Applying pakdiff to codebase...")
    
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
                                logger.info("✅ Changes committed to branch")
                            except subprocess.CalledProcessError:
                                logger.warning("⚠️  Could not commit changes")
        except Exception as e:
            logger.error(f"❌ Git branch operation failed: {e}")
            success = False
    else:
        success = run_pak_apply(config.fix_path)
    
    if success:
        logger.info("\n✅ SUCCESS! Changes have been applied to your codebase.")
        if config.is_git_repo:
            logger.info("📝 Next steps:")
            logger.info("   git status          # See what changed")
            logger.info("   git diff            # Review changes")
            logger.info("   git add . && git commit -m 'Apply changes'  # Commit if satisfied")
        else:
            logger.info("📝 Consider initializing git for better change tracking")
    else:
        logger.error("\n❌ FAILED! Changes could not be applied.")
        logger.info("💡 Use 'python revert.py' to restore original files if needed")
        sys.exit(1)
if __name__ == "__main__":
    main()
