"""
Program b) modify "try doing this"
Uses archive and implements via LLM what is asked,
receiving back from LLM in structured form answer and fix (pakdiff format)
"""
import os
import sys
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
from pakagent_config import config, check_required_files
def read_archive():
    """Read the archive file created by send.py"""
    if not check_required_files(config.archive_path):
        print("Run 'python send.py' first to create the archive.")
        return None
    try:
        with open(config.archive_path, 'r') as f:
            content = f.read()
        print(f"📄 Loaded archive: {len(content):,} characters")
        return content
    except Exception as e:
        print(f"❌ Error reading archive: {e}")
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
        print("❌ Error: OPENROUTER_API_KEY not found in environment")
        print("Set it in .env file or environment variables")
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
        print("🤖 Sending request to LLM...")
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
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            print(f"❌ API error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error calling LLM API: {e}")
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
        print("✅ Successfully extracted pakdiff from response")
    else:
        print("⚠️  No pakdiff code block found, using full implementation section")
        pakdiff_content = implementation_section.strip()
    return analysis, pakdiff_content
def save_outputs(answer_text, pakdiff_text):
    """Save answer and pakdiff to session files"""
    try:
        with open(config.answer_path, "w") as f:
            f.write(answer_text)
        print(f"✅ Saved analysis to {config.answer_path}")
        with open(config.fix_path, "w") as f:
            f.write(pakdiff_text)
        print(f"✅ Saved pakdiff to {config.fix_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving outputs: {e}")
        return False
def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python modify.py 'your modification request'")
        print("Examples:")
        print("  python modify.py 'add logging to all methods'")
        print("  python modify.py 'implement error handling'")
        print("  python modify.py 'add input validation'")
        print("  python modify.py 'refactor code for better readability'")
        return
    load_dotenv()
    instruction = " ".join(sys.argv[1:])
    print(f"🎯 Task: {instruction}")
    
    # Debug API configuration
    api_key = os.environ.get("OPENROUTER_API_KEY")
    model = os.environ.get("OPENROUTER_MODEL", "anthropic/claude-3-haiku:beta")
    max_tokens = os.environ.get("OPENROUTER_MAX_TOKENS", "4000")
    temperature = os.environ.get("OPENROUTER_TEMPERATURE", "0.1")
    
    if api_key:
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***masked***"
        print(f"🔑 API Key: {masked_key}")
        print(f"🤖 Model: {model}")
        print(f"🎛️  Max Tokens: {max_tokens}, Temperature: {temperature}")
        print("💡 To change model/settings, edit .env file:")
        print("   OPENROUTER_MODEL=anthropic/claude-3-sonnet:beta")
        print("   OPENROUTER_MAX_TOKENS=8000")
        print("   OPENROUTER_TEMPERATURE=0.2")
    else:
        print("❌ OPENROUTER_API_KEY not found")
        print("💡 Create .env file with:")
        print("   OPENROUTER_API_KEY=your_key_here")
        print("   OPENROUTER_MODEL=anthropic/claude-3-haiku:beta")
        print("   OPENROUTER_MAX_TOKENS=4000")
        print("   OPENROUTER_TEMPERATURE=0.1")
    
    # Use LLM to classify the request
    print("🔍 Classifying request type...")
    is_question = classify_request(instruction)
    print(f"📋 Request type: {'Text response' if is_question else 'Code modification'}")
    
    archive_content = read_archive()
    if not archive_content:
        sys.exit(1)
    response = send_to_llm(archive_content, instruction, is_question)
    if not response:
        print("❌ Failed to get response from LLM")
        sys.exit(1)
    answer_text, pakdiff_text = parse_llm_response(response, is_question)
    if not answer_text:
        print("❌ Failed to parse LLM response properly")
        print("Raw response:")
        print(response)
        sys.exit(1)
    
    # For text responses, pakdiff_text will be empty
    if is_question and not pakdiff_text:
        print("ℹ️  Text response detected - no pakdiff generated")
    if save_outputs(answer_text, pakdiff_text):
        print("\n🚀 Success! Next steps:")
        print("  python show_answer.py  # Review the changes")
        print("  python apply.py        # Apply the changes")
    else:
        sys.exit(1)
if __name__ == "__main__":
    main()