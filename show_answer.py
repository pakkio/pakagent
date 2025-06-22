import curses
import os
from typing import List, Tuple, Dict, Any
from pakagent_config import config

def read_file(filename: str) -> List[str]:
    """Reads a file and returns its content as a list of lines."""
    try:
        with open(filename, 'r') as f:
            return f.readlines()
    except FileNotFoundError:
        return [f"Error: File not found: {filename}"]
    except Exception as e:
        return [f"Error reading file {filename}: {e}"]

def parse_pakdiff(pakdiff_lines: List[str]) -> Tuple[List[str], Dict[str, List[str]]]:
    """Parses pakdiff content and extracts summary and method content."""
    summary = []
    method_content = {}
    current_file = None
    current_method = None
    current_content = []
    in_replace_with = False
    
    for line in pakdiff_lines:
        line = line.rstrip()
        
        if line.startswith("FILE:"):
            if current_file and current_method:
                key = f"{current_file}: {current_method}"
                method_content[key] = current_content[:]
            current_file = line[5:].strip()
            current_method = None
            current_content = []
            in_replace_with = False
            
        elif line.startswith("FIND_METHOD:"):
            if current_file and current_method:
                key = f"{current_file}: {current_method}"
                method_content[key] = current_content[:]
            current_method = line[12:].strip()
            if not current_method:
                current_method = "[NEW METHOD]"
            summary.append(f"{current_file}: {current_method}")
            current_content = []
            in_replace_with = False
            
        elif line.startswith("SECTION:"):
            if current_file and current_method:
                key = f"{current_file}: {current_method}"
                method_content[key] = current_content[:]
            section_type = line[8:].strip()
            current_method = f"[{section_type}]"
            summary.append(f"{current_file}: {current_method}")
            current_content = []
            in_replace_with = False
            
        elif line.startswith("REPLACE_WITH:"):
            in_replace_with = True
            
        elif in_replace_with and line.strip():
            current_content.append(line)
            
    if current_file and current_method:
        key = f"{current_file}: {current_method}"
        method_content[key] = current_content[:]
        
    return summary, method_content

class ShowAnswerUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        self.height, self.width = stdscr.getmaxyx()
        
        self.answer_lines = []
        self.pakdiff_summary = []
        self.method_content = {}
        
        self.answer_start = 0
        self.answer_col = 0
        self.summary_start = 0
        self.method_start = 0
        self.method_col = 0
        self.selected_method = 0
        
        self.setup_windows()
        
    def setup_windows(self):
        """Setup the three windows side by side."""
        win_width = self.width // 3
        win_height = self.height - 3
        
        self.answer_win = curses.newwin(win_height, win_width, 1, 0)
        self.summary_win = curses.newwin(win_height, win_width, 1, win_width)
        self.method_win = curses.newwin(win_height, win_width, 1, win_width * 2)
        
        self.answer_win.box()
        self.summary_win.box()
        self.method_win.box()
        
    def load_data(self):
        """Load answer and pakdiff data."""
        self.answer_lines = read_file(str(config.answer_path))
        pakdiff_lines = read_file(str(config.fix_path))
        self.pakdiff_summary, self.method_content = parse_pakdiff(pakdiff_lines)
        
    def draw_window(self, win, title: str, content: List[str], start_line: int, start_col: int = 0, highlight_line: int = -1):
        """Draw content in a window with title and scrolling."""
        win.clear()
        win.box()
        
        height, width = win.getmaxyx()
        usable_height = height - 2
        usable_width = width - 2
        
        win.addstr(0, 2, f" {title} ", curses.A_BOLD)
        
        for i in range(usable_height):
            line_idx = start_line + i
            if line_idx < len(content):
                full_line = content[line_idx].rstrip()
                line = full_line[start_col:start_col + usable_width] if start_col < len(full_line) else ""
                attr = curses.A_REVERSE if line_idx == highlight_line else 0
                try:
                    win.addstr(i + 1, 1, line.ljust(usable_width), attr)
                except curses.error:
                    pass
                    
        win.refresh()
        
    def get_current_method_content(self) -> List[str]:
        """Get content for currently selected method."""
        if not self.pakdiff_summary or self.selected_method >= len(self.pakdiff_summary):
            return []
        
        selected_key = self.pakdiff_summary[self.selected_method]
        return self.method_content.get(selected_key, [])
        
    def draw_all_windows(self):
        """Draw all three windows."""
        self.draw_window(self.answer_win, "Answer", self.answer_lines, self.answer_start, self.answer_col)
        
        self.draw_window(self.summary_win, "Pakdiff Summary", self.pakdiff_summary, 
                        self.summary_start, 0, self.selected_method)
        
        method_content = self.get_current_method_content()
        self.draw_window(self.method_win, "Method Detail", method_content, self.method_start, self.method_col)
        
        help_text = "Controls: ↑↓←→(answer) PgUp/PgDn(summary) +/-*/(method) a/z s/x d/c(nav) q(uit)"
        try:
            self.stdscr.addstr(self.height - 1, 0, help_text[:self.width - 1])
        except curses.error:
            pass
        self.stdscr.refresh()
        
    def handle_input(self):
        """Handle keyboard input and navigation."""
        while True:
            # Display archive immediately upon startup and after each input
            self.draw_all_windows()
            key = self.stdscr.getch()
            
            if key == ord('q'):
                break
            elif key == curses.KEY_UP:
                self.answer_start = max(0, self.answer_start - 1)
            elif key == curses.KEY_DOWN:
                if self.answer_start + 10 < len(self.answer_lines):
                    self.answer_start += 1
            elif key == curses.KEY_LEFT:
                self.answer_col = max(0, self.answer_col - 5)
            elif key == curses.KEY_RIGHT:
                self.answer_col += 5
            elif key == curses.KEY_PPAGE:
                self.selected_method = max(0, self.selected_method - 1)
                self.method_start = 0
                if self.selected_method < self.summary_start:
                    self.summary_start = self.selected_method
            elif key == curses.KEY_NPAGE:
                if self.selected_method < len(self.pakdiff_summary) - 1:
                    self.selected_method += 1
                    self.method_start = 0
                    win_height = self.summary_win.getmaxyx()[0] - 2
                    if self.selected_method >= self.summary_start + win_height:
                        self.summary_start = self.selected_method - win_height + 1
            elif key == ord('+'):
                method_content = self.get_current_method_content()
                if self.method_start + 10 < len(method_content):
                    self.method_start += 1
            elif key == ord('-'):
                self.method_start = max(0, self.method_start - 1)
            elif key == ord('*'):
                self.method_col = max(0, self.method_col - 5)
            elif key == ord('/'):
                self.method_col += 5
            elif key == ord('a'):
                self.answer_start = 0
                self.answer_col = 0
            elif key == ord('z'):
                self.answer_start = max(0, len(self.answer_lines) - 10)
            elif key == ord('s'):
                self.selected_method = 0
                self.summary_start = 0
                self.method_start = 0
            elif key == ord('x'):
                self.selected_method = len(self.pakdiff_summary) - 1
                win_height = self.summary_win.getmaxyx()[0] - 2
                self.summary_start = max(0, len(self.pakdiff_summary) - win_height)
                self.method_start = 0
            elif key == ord('d'):
                self.method_start = 0
                self.method_col = 0
            elif key == ord('c'):
                method_content = self.get_current_method_content()
                self.method_start = max(0, len(method_content) - 10)

def main():
    """Main function to display the three-window interface with immediate archive display."""
    def curses_main(stdscr):
        ui = ShowAnswerUI(stdscr)
        ui.load_data()
        
        # Load archive if it exists
        try:
            archive_lines = read_file(str(config.archive_path))
            if archive_lines and not archive_lines[0].startswith("Error:"):
                ui.answer_lines = archive_lines + ["", "=== PAKDIFF ANSWER ===", ""] + ui.answer_lines
        except:
            pass
        
        if not ui.answer_lines or not ui.pakdiff_summary:
            stdscr.addstr(0, 0, f"Error: Could not load {config.answer_path} or {config.fix_path} files")
            stdscr.refresh()
            stdscr.getch()
            return
            
        ui.handle_input()
    
    curses.wrapper(curses_main)
def show_answer():
    """Legacy function name for compatibility."""
    main()

if __name__ == "__main__":
    main()
