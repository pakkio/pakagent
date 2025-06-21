"""
Program b) modify "try doing this"
Uses /tmp/archive.txt and implements via LLM what is asked,
receiving back from LLM in structured form /tmp/answer and /tmp/fix (pakdiff format)
"""
import os
import sys
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
def read_archive():
    """Read the archive file created by send.py"""
    archive_path = Path("/tmp/archive.txt")
    if not archive_path.exists():
        print("❌ Archive file /tmp/archive.txt not found.")
        print("Run 'python send.py' first to create the archive.")
        return None
    try:
        with open(archive_path, 'r') as f:
            content = f.read()
        print(f"📄 Loaded archive: {len(content):,} characters")
        return content
    except Exception as e:
        print(f"❌ Error reading archive: {e}")
        return None
def send_to_llm(archive_content, instructions):
    """Send modification request to LLM"""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in environment")
        print("Set it in .env file or environment variables")
        return None
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
def parse_llm_response(response_text):
    """Parse LLM response into answer and pakdiff components"""
    if not response_text:
        return None, None
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
    """Save answer and pakdiff to /tmp/ files"""
    try:
        with open("/tmp/answer", "w") as f:
            f.write(answer_text)
        print("✅ Saved analysis to /tmp/answer")
        with open("/tmp/fix", "w") as f:
            f.write(pakdiff_text)
        print("✅ Saved pakdiff to /tmp/fix")
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
    archive_content = read_archive()
    if not archive_content:
        sys.exit(1)
    response = send_to_llm(archive_content, instruction)
    if not response:
        print("❌ Failed to get response from LLM")
        sys.exit(1)
    answer_text, pakdiff_text = parse_llm_response(response)
    if not answer_text or not pakdiff_text:
        print("❌ Failed to parse LLM response properly")
        print("Raw response:")
        print(response)
        sys.exit(1)
    if save_outputs(answer_text, pakdiff_text):
        print("\n🚀 Success! Next steps:")
        print("  python show_answer.py  # Review the changes")
        print("  python apply.py        # Apply the changes")
    else:
        sys.exit(1)
if __name__ == "__main__":
    main()