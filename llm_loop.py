"""
LLM Interaction Loop (Producer)
Generates pakdiff files by interacting with LLM services.
"""
import os
import time
import uuid
import requests
from pakagent_config import get_requests_session, logger
import subprocess
import json
import re
from pathlib import Path
from dotenv import load_dotenv
def run_pak_command(args, cwd=None):
    """Execute pak command with given arguments"""
    try:
        cmd = ["pak"] + args
        logger.info(f"[LLM Loop] Running: {' '.join(cmd)}")
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            logger.info("[LLM Loop] Pak command successful")
            return True
        else:
            logger.info(f"[LLM Loop] Pak command failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.info("[LLM Loop] Pak command timed out")
        return False
    except Exception as e:
        logger.info(f"[LLM Loop] Error running pak command: {e}")
        return False
def pack_codebase(source_dir, output_pak):
    """Package codebase into pak file using pak v5.0.0"""
    args = [source_dir, "-t", "py,js,ts", "-c", "2", "-o", output_pak]
    return run_pak_command(args)
def send_to_llm(pak_content, instructions):
    """Send pakdiff generation request to LLM"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.info("[LLM Loop] Error: OPENROUTER_API_KEY not found")
        return None
    prompt = f"""You are a code assistant that generates pakdiff v4.3.0 format changes.
TASK: {instructions}
IMPORTANT: Respond ONLY with pakdiff format inside a markdown code block. Use this exact format:
```pakdiff
FILE: path/to/file.extension
FIND_METHOD: method_signature_to_find
UNTIL_EXCLUDE: next_method_signature_or_empty
REPLACE_WITH:
new_method_implementation
FILE: path/to/file.extension
SECTION: GLOBAL_PREAMBLE
UNTIL_EXCLUDE: first_class_or_function
REPLACE_WITH:
import statements
global variables
```
For method modifications, use FIND_METHOD and UNTIL_EXCLUDE.
For global changes (imports, constants), use SECTION: GLOBAL_PREAMBLE.
Separate multiple changes with blank lines.
CODEBASE:
{pak_content}
Generate the pakdiff now:"""
    try:
        session = get_requests_session()
        response = session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.environ.get("SEMANTIC_MODEL", "anthropic/claude-3-haiku:beta"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": int(os.environ.get("SEMANTIC_MAX_TOKENS", "4000")),
                "temperature": float(os.environ.get("SEMANTIC_TEMPERATURE", "0.1"))
            },
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            logger.info(f"[LLM Loop] API error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        logger.info(f"[LLM Loop] Error calling LLM API: {e}")
        return None
def get_pakdiff_from_llm_response(response):
    """Extract pakdiff content from LLM response"""
    if not response:
        return None
    pakdiff_pattern = r'```(?:pakdiff)?\s*\n(.*?)\n```'
    matches = re.findall(pakdiff_pattern, response, re.DOTALL)
    if matches:
        pakdiff_content = matches[0].strip()
        logger.info("[LLM Loop] Successfully extracted pakdiff from response")
        return pakdiff_content
    else:
        logger.info("[LLM Loop] No pakdiff format found in LLM response")
        logger.info(f"[LLM Loop] Response was: {response[:200]}...")
        return None
def get_next_instruction():
    """Get next instruction - in real app this could come from queue/file/UI"""
    instructions = [
        "Add logging to the add method in calculator.py",
        "Add input validation to all calculator methods",
        "Create a new multiply_with_precision method",
        "Add error handling to prevent division by zero",
        "Add unit tests for the calculator class"
    ]
    timestamp = int(time.time())
    index = timestamp % len(instructions)
    return instructions[index]
def llm_interaction_loop():
    """Main LLM interaction loop - runs continuously generating pakdiff files"""
    load_dotenv()
    WORKFLOW_DIR = os.environ["PAK_WORKFLOW_DIR"]
    SOURCE_DIR = os.environ["PAK_SOURCE_DIR"]
    logger.info(f"[LLM Loop] Starting with workflow dir: {WORKFLOW_DIR}")
    logger.info(f"[LLM Loop] Monitoring source dir: {SOURCE_DIR}")
    cycle_count = 0
    while True:
        cycle_count += 1
        logger.info(f"\n[LLM Loop] === Starting cycle #{cycle_count} ===")
        try:
            pak_file = os.path.join(WORKFLOW_DIR, "current_codebase.pak")
            logger.info(f"[LLM Loop] Packing '{SOURCE_DIR}' into '{pak_file}'...")
            if not pack_codebase(SOURCE_DIR, pak_file):
                logger.info("[LLM Loop] Packaging failed. Retrying in 30s.")
                time.sleep(30)
                continue
            instructions = get_next_instruction()
            logger.info(f"[LLM Loop] Task for this cycle: '{instructions}'")
            try:
                with open(pak_file, 'r') as f:
                    pak_content = f.read()
            except Exception as e:
                logger.info(f"[LLM Loop] Error reading pak file: {e}")
                time.sleep(30)
                continue
            logger.info("[LLM Loop] Sending request to LLM...")
            llm_response = send_to_llm(pak_content, instructions)
            if not llm_response:
                logger.info("[LLM Loop] No response from LLM. Retrying in 60s.")
                time.sleep(60)
                continue
            pakdiff_content = get_pakdiff_from_llm_response(llm_response)
            if pakdiff_content:
                diff_filename = f"change_{uuid.uuid4().hex[:8]}_{cycle_count:03d}.diff"
                diff_filepath = os.path.join(WORKFLOW_DIR, diff_filename)
                with open(diff_filepath, "w") as f:
                    f.write(f"# Generated pakdiff for: {instructions}\n")
                    f.write(f"# Cycle: {cycle_count}, Time: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(pakdiff_content)
                logger.info(f"[LLM Loop] ✅ Success! New pakdiff created: '{diff_filename}'")
                logger.info(f"[LLM Loop] Content preview: {pakdiff_content[:100]}...")
            else:
                logger.info("[LLM Loop] ❌ Failed to extract valid pakdiff from LLM response")
        except Exception as e:
            logger.info(f"[LLM Loop] ❌ Unexpected error in cycle: {e}")
        wait_time = 60
        logger.info(f"[LLM Loop] Cycle #{cycle_count} complete. Waiting {wait_time}s for next cycle...")
        time.sleep(wait_time)
if __name__ == "__main__":
    os.environ.setdefault("PAK_WORKFLOW_DIR", "/tmp/pak_test")
    os.environ.setdefault("PAK_SOURCE_DIR", os.getcwd())
    llm_interaction_loop()
