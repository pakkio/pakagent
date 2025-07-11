"""
Main launcher for the modular pakdiff workflow system.
Sets up shared resources and launches producer/consumer processes.
"""
import os
import tempfile
import multiprocessing
import signal
import sys
import shutil
from pathlib import Path
from dotenv import load_dotenv
from pakagent_config import logger
from llm_loop import llm_interaction_loop
from local_loop import local_application_loop
from pakdiff import show_answer
def cleanup_handler(signum, frame):
    """Handle cleanup on signal"""
    logger.info("\nReceived signal, cleaning up...")
    sys.exit(0)
def main():
    load_dotenv()
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    temp_dir = tempfile.mkdtemp(prefix="pak_workflow_")
    logger.info(f"🚀 Pakdiff workflow starting")
    logger.info(f"📁 Shared directory: {temp_dir}")
    os.makedirs(os.path.join(temp_dir, "failed"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "applied"), exist_ok=True)
    os.environ["PAK_WORKFLOW_DIR"] = temp_dir
    os.environ["PAK_SOURCE_DIR"] = os.getcwd()
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.info("⚠️  Warning: OPENROUTER_API_KEY not set. LLM loop may fail.")
    try:
        logger.info("🤖 Starting LLM interaction process...")
        llm_process = multiprocessing.Process(
            target=llm_interaction_loop, name="LLM-Producer")
        logger.info("👨‍💻 Starting local application process...")
        local_process = multiprocessing.Process(
            target=local_application_loop, name="Local-Consumer")
        llm_process.start()
        local_process.start()
        logger.info("✅ Both processes started successfully")
        logger.info("Press Ctrl+C to stop the workflow")
        llm_process.join()
        local_process.join()
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping workflow...")
        if llm_process.is_alive():
            llm_process.terminate()
        if local_process.is_alive():
            local_process.terminate()
        llm_process.join(timeout=5)
        local_process.join(timeout=5)
    except Exception as e:
        logger.info(f"❌ Error: {e}")
    finally:
        logger.info(f"🧹 Cleaning up directory: {temp_dir}")
        logger.info("Workflow finished.")
def handle_show_answer():
    """Handles the show-answer functionality."""
    try:
        show_answer()
    except Exception as e:
        logger.info(f"Error in show_answer: {e}")
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "show-answer":
        handle_show_answer()
    else:
        main()