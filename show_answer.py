import os

def read_file(filename):
    """Reads a file and returns its content as a list of lines."""
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        return []
    except Exception as e:
        print(f"Error reading file {filename}: {e}")
        return []

def parse_pakdiff(pakdiff_lines):
    """Parses pakdiff content and extracts a summary of changes."""
    summary = []
    current_file = None
    current_method = None
    for line in pakdiff_lines:
        line = line.strip()
        if line.startswith("FILE:"):
            current_file = line[5:].strip()
            current_method = None
        elif line.startswith("FIND_METHOD:"):
            current_method = line[12:].strip()
            summary.append(f"{current_file}: {current_method}")
    return summary

def display_window(title, content, height=10, width=40, start_line=0):
    """Displays a window with the given content."""
    print("-" * (width + 4))
    print(f"| {title:^{width+2}} |")
    print("-" * (width + 4))

    for i in range(start_line, min(start_line + height, len(content))):
        line = content[i].strip()
        print(f"| {line[:width]:<{width+2}} |")  # Truncate and pad

    # Fill remaining lines with blanks
    for i in range(min(height, max(0, height - len(content) + start_line))):
        print(f"| {' ':<{width+2}} |")

    print("-" * (width + 4))
    return min(start_line + height, len(content))

def show_answer():
    """Displays the answer, pakdiff summary, and method content in separate windows."""
    answer_file = "/tmp/answer"
    pakdiff_file = "/tmp/fix"

    answer_lines = read_file(answer_file)
    pakdiff_lines = read_file(pakdiff_file)
    pakdiff_summary = parse_pakdiff(pakdiff_lines)

    if not answer_lines or not pakdiff_lines:
        print("Could not display answer due to missing files.")
        return

    answer_start_line = 0
    summary_start_line = 0
    method_start_line = 0

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear the screen

        answer_end_line = display_window("Answer", answer_lines, start_line=answer_start_line)
        summary_end_line = display_window("Pakdiff Summary", pakdiff_summary, start_line=summary_start_line)
        method_content = []
        if pakdiff_summary and summary_start_line < len(pakdiff_summary):
            # Find the corresponding method content in pakdiff_lines
            selected_summary = pakdiff_summary[summary_start_line]
            filename, method_name = selected_summary.split(": ")
            method_content = [line for line in pakdiff_lines if method_name in line]

        display_window("Method Content", method_content, start_line=method_start_line)

        print("\nNavigation: a(top) z(bottom) s(up) x(down) d(next method) c(prev method) q(uit)")
        key = input("Enter command: ").lower()

        if key == 'a':
            answer_start_line = 0
        elif key == 'z':
            answer_start_line = max(0, len(answer_lines) - 10)
        elif key == 's':
            answer_start_line = max(0, answer_start_line - 10)
        elif key == 'x':
            answer_start_line = min(len(answer_lines) - 10, answer_start_line + 10)
        elif key == 'd':
            summary_start_line = min(len(pakdiff_summary) - 10, summary_start_line + 1)
        elif key == 'c':
            summary_start_line = max(0, summary_start_line - 1)
        elif key == 'q':
            break
        else:
            print("Invalid command.")

if __name__ == "__main__":
    show_answer()
