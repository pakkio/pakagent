"""
Program b) pakmod "try doing this"
Uses archive and implements via LLM what is asked,
receiving back from LLM in structured form answer and fix (pakdiff format)
"""
import os
import sys
import requests
import re
import argparse
from pathlib import Path
from dotenv import load_dotenv
from pakagent_config import config, check_required_files, get_requests_session, logger, mask_sensitive_data, validate_pakdiff_content
def read_archive():
    """Read the archive file created by prepare.py"""
    if not check_required_files(config.archive_path):
        logger.error("Run 'python prepare.py' first to create the archive.")
        return None
    try:
        with open(config.archive_path, 'r') as f:
            content = f.read()
        logger.info(f"📄 Loaded archive: {len(content):,} characters")
        return content
    except Exception as e:
        logger.error(f"❌ Error reading archive: {e}")
        return None
def classify_request(instructions):
    """Use LLM to classify if request is question or code modification"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        # Fallback to keyword detection if no API key
        text_keywords = ['what', 'why', 'how', 'explain', 'describe', 'think', 'opinion', 'pensi', 'cosa', 'quale', 'perché', 'come', 'ascii', 'schema', 'diagram', 'visualize', 'draw', 'documentation', 'docs']
        return any(keyword in instructions.lower() for keyword in text_keywords)
    
    classification_prompt = f"""Classify this request as either "TEXT_RESPONSE" or "CODE_CHANGE".

REQUEST: {instructions}

Rules:
- TEXT_RESPONSE: User wants explanation, analysis, opinion, information, diagrams, schemas, ASCII art, documentation, or any visual/textual output
- CODE_CHANGE: User wants to modify, add, fix, or implement actual code files

Examples:
- "cosa ne pensi" → TEXT_RESPONSE
- "what do you think" → TEXT_RESPONSE  
- "explain this code" → TEXT_RESPONSE
- "make an ascii schema" → TEXT_RESPONSE
- "draw a diagram" → TEXT_RESPONSE
- "create documentation" → TEXT_RESPONSE
- "visualize the architecture" → TEXT_RESPONSE
- "add logging" → CODE_CHANGE
- "fix the bug" → CODE_CHANGE
- "implement authentication" → CODE_CHANGE
- "refactor this method" → CODE_CHANGE

Respond with only: TEXT_RESPONSE or CODE_CHANGE"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku:beta"),
                "messages": [{"role": "user", "content": classification_prompt}],
                "max_tokens": 10,
                "temperature": 0.0
            },
            timeout=30
        )
        if response.status_code == 200:
            result = response.json()
            classification = result["choices"][0]["message"]["content"].strip()
            return classification == "TEXT_RESPONSE"
        else:
            # Fallback to keyword detection
            text_keywords = ['what', 'why', 'how', 'explain', 'describe', 'think', 'opinion', 'pensi', 'cosa', 'quale', 'perché', 'come', 'ascii', 'schema', 'diagram', 'visualize', 'draw', 'documentation', 'docs']
            return any(keyword in instructions.lower() for keyword in text_keywords)
    except Exception:
        # Fallback to keyword detection
        text_keywords = ['what', 'why', 'how', 'explain', 'describe', 'think', 'opinion', 'pensi', 'cosa', 'quale', 'perché', 'come', 'ascii', 'schema', 'diagram', 'visualize', 'draw', 'documentation', 'docs']
        return any(keyword in instructions.lower() for keyword in text_keywords)

def send_to_llm(archive_content, instructions, is_question=False):
    """Send modification request to LLM"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("❌ Error: OPENROUTER_API_KEY not found in environment")
        logger.error("Set it in .env file or environment variables")
        return None
    
    if is_question:
        # For text responses (questions, schemas, diagrams, etc.), just ask for analysis without pakdiff
        prompt = f"""You are an expert code assistant. Please analyze the provided codebase and respond to the following request.

REQUEST: {instructions}

Please provide a detailed response based on the codebase provided below. If asked for diagrams, schemas, or ASCII art, feel free to create them using text characters.

CODEBASE:
{archive_content}

Please provide your response:"""
    else:
        # For modifications, use the full pakdiff format
        prompt = f"""You are an expert code assistant. I need you to analyze the provided codebase and implement the requested changes.
TASK: {instructions}
INSTRUCTIONS:
1. First, provide a detailed explanation of what you're going to do
2. Then provide the implementation as pakdiff v4.3.0 format
Your response should be structured EXACTLY like this:
[Your detailed explanation of the changes you will make]
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
PAKDIFF FORMAT RULES:
- Use FIND_METHOD for modifying existing methods/functions
- Use SECTION: GLOBAL_PREAMBLE for imports, global variables, constants
- Use empty FIND_METHOD for adding new methods at end of file
- Include proper UNTIL_EXCLUDE boundaries
- Separate multiple changes with blank lines
CODEBASE:
{archive_content}
Please implement the requested changes now:"""
    try:
        session = get_requests_session()
        logger.info("🤖 Sending request to LLM...")
        response = session.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku:beta"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": int(os.environ.get("OPENROUTER_MAX_TOKENS", "4000")),
                "temperature": float(os.environ.get("OPENROUTER_TEMPERATURE", "0.1"))
            },
            timeout=120
        )
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            # Mask sensitive data in API error response
            masked_response = mask_sensitive_data(response.text)
            logger.error(f"❌ API error {response.status_code}: {masked_response}")
            return None
    except Exception as e:
        # Mask sensitive data in exception messages
        masked_error = mask_sensitive_data(str(e))
        logger.error(f"❌ Error calling LLM API: {masked_error}")
        return None
def parse_llm_response(response_text, is_question=False):
    """Parse LLM response into answer and pakdiff components"""
    if not response_text:
        return None, None
    
    # For questions, no pakdiff expected
    if is_question:
        return response_text.strip(), ""
    
    sections = response_text.split("## IMPLEMENTATION")
    if len(sections) < 2:
        analysis = response_text
        implementation_section = response_text
    else:
        analysis = sections[0].replace("## ANALYSIS AND PLAN", "").strip()
        implementation_section = sections[1]
    pakdiff_pattern = r'```(?:pakdiff)?\s*\n(.*?)\n```'
    pakdiff_matches = re.findall(pakdiff_pattern, implementation_section, re.DOTALL)
    if pakdiff_matches:
        pakdiff_content = pakdiff_matches[0].strip()
    elif 'PAKDIFF_START' in implementation_section and 'PAKDIFF_END' in implementation_section:
        blocks = re.findall(r'PAKDIFF_START\s*(.*?)\s*PAKDIFF_END', implementation_section, re.DOTALL)
        pakdiff_content = '\n'.join(b.strip() for b in blocks if b.strip())
    else:
        pakdiff_content = ''
    return analysis, pakdiff_content
def save_outputs(answer_text, pakdiff_text):
    """Save answer and pakdiff to session files with validation"""
    try:
        # Save answer file
        with open(config.answer_path, "w") as f:
            f.write(answer_text)
        logger.info(f"✅ Saved analysis to {config.answer_path}")
        
        # Validate pakdiff before saving
        if pakdiff_text.strip():
            try:
                validate_pakdiff_content(pakdiff_text)
                logger.info("✅ Pakdiff content validated successfully")
            except ValueError as e:
                logger.warning(f"⚠️  Pakdiff validation warning: {e}")
                # Continue saving but warn user
        
        # Save pakdiff file
        with open(config.fix_path, "w") as f:
            f.write(pakdiff_text)
        
        # Report accurate status based on content
        if pakdiff_text.strip():
            logger.info(f"✅ Saved pakdiff to {config.fix_path}")
        else:
            logger.warning(f"⚠️  No valid pakdiff generated - empty file saved to {config.fix_path}")
        return True
    except Exception as e:
        masked_error = mask_sensitive_data(str(e))
        logger.error(f"❌ Error saving outputs: {masked_error}")
        return False
    
def call_llm(instructions, archive_content):
    """Send a simple LLM request for content without classification logic."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        logger.error("❌ Error: OPENROUTER_API_KEY not found in environment")
        return None
    # Prepare a minimal prompt combining instructions and archive
    prompt = f"TASK: {instructions}\nCODEBASE:\n{archive_content}"
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku:beta"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": int(os.environ.get("OPENROUTER_MAX_TOKENS", "4000")),
                "temperature": float(os.environ.get("OPENROUTER_TEMPERATURE", "0.1"))
            },
            timeout=120
        )
        response.raise_for_status()
        data = response.json()
        return data.get("choices", [])[0].get("message", {}).get("content")
    except Exception:
        return None

def process_instructions(instruction, force_pakdiff=False):
    """High-level processing: classify, call LLM, parse, and save outputs."""
    # Classify request (override if --pakdiff is used)
    is_question = False if force_pakdiff else classify_request(instruction)
    # Load code archive
    archive_content = read_archive()
    if archive_content is None:
        return False
    # Get LLM response
    if force_pakdiff:
        response = send_to_llm(archive_content, instruction, is_question=False)
    else:
        response = call_llm(instruction, archive_content)
    if not response:
        return False
    # Parse response into analysis and pakdiff
    answer_text, pakdiff_text = parse_llm_response(response, is_question)
    # Save to files
    return save_outputs(answer_text, pakdiff_text)
def main():
    """Main entrypoint for modify CLI."""
    parser = argparse.ArgumentParser(
        description="Generate code modifications using LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "instruction", 
        nargs="*", 
        help="Modification instruction (if not provided, will prompt)"
    )
    parser.add_argument(
        "--pakdiff", 
        action="store_true", 
        help="Force pakdiff format output (skips text classification)"
    )
    
    args = parser.parse_args()
    
    # Determine instruction: CLI args or interactive input
    if not args.instruction:
        try:
            instruction = input("Enter modification request: ").strip()
        except (KeyboardInterrupt, EOFError):
            return
    else:
        instruction = " ".join(args.instruction)
    
    # Delegate to process_instructions
    process_instructions(instruction, force_pakdiff=args.pakdiff)

if __name__ == "__main__":
    main()
