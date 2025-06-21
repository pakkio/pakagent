#!/usr/bin/env python3
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

# Import the loop functions from other modules
from llm_loop import llm_interaction_loop
from local_loop import local_application_loop

def cleanup_handler(signum, frame):
    """Handle cleanup on signal"""
    print("\nReceived signal, cleaning up...")
    sys.exit(0)

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    # 1. Create a shared temporary directory for the workflow
    temp_dir = tempfile.mkdtemp(prefix="pak_workflow_")
    print(f"🚀 Pakdiff workflow starting")
    print(f"📁 Shared directory: {temp_dir}")
    
    # Create subdirectories for organization
    os.makedirs(os.path.join(temp_dir, "failed"), exist_ok=True)
    os.makedirs(os.path.join(temp_dir, "applied"), exist_ok=True)
    
    # 2. Set environment variables for the subprocesses
    os.environ["PAK_WORKFLOW_DIR"] = temp_dir
    os.environ["PAK_SOURCE_DIR"] = os.getcwd()  # Run from project root
    
    # Verify required environment variables
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("⚠️  Warning: OPENROUTER_API_KEY not set. LLM loop may fail.")
    
    # 3. Create and start the two separate processes
    try:
        print("🤖 Starting LLM interaction process...")
        llm_process = multiprocessing.Process(target=llm_interaction_loop, name="LLM-Producer")
        
        print("👨‍💻 Starting local application process...")
        local_process = multiprocessing.Process(target=local_application_loop, name="Local-Consumer")
        
        llm_process.start()
        local_process.start()
        
        print("✅ Both processes started successfully")
        print("Press Ctrl+C to stop the workflow")
        
        # Wait for processes to complete (they run indefinitely)
        llm_process.join()
        local_process.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping workflow...")
        if llm_process.is_alive():
            llm_process.terminate()
        if local_process.is_alive():
            local_process.terminate()
            
        llm_process.join(timeout=5)
        local_process.join(timeout=5)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        print(f"🧹 Cleaning up directory: {temp_dir}")
        # Optionally keep the directory for inspection
        # shutil.rmtree(temp_dir)
        print("Workflow finished.")

if __name__ == "__main__":
    main()