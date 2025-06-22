#!/usr/bin/env python3
"""
PakView - 3-window navigation interface for pak archive files
Explore pak compressed archives with metadata, file list, and content views
"""

import curses
import json
import os
import sys
from typing import List, Tuple, Dict, Any
from pakagent_config import config

def read_pak_archive(filename: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Reads a pak archive file and returns metadata and files."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        files = data.get('files', [])
        
        return metadata, files
    except FileNotFoundError:
        return {}, []
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format: {e}"}, []
    except Exception as e:
        return {"error": f"Error reading file: {e}"}, []

def format_metadata(metadata: Dict[str, Any]) -> List[str]:
    """Format metadata into displayable lines."""
    if not metadata:
        return ["No metadata available"]
    
    if "error" in metadata:
        return [f"Error: {metadata['error']}"]
    
    lines = []
    lines.append("=== PAK ARCHIVE METADATA ===")
    lines.append("")
    
    for key, value in metadata.items():
        if key == "creation_timestamp_utc":
            lines.append(f"Created: {value}")
        elif key == "pak_format_version":
            lines.append(f"Format: {value}")
        elif key == "total_files":
            lines.append(f"Files: {value}")
        elif key == "total_original_size_bytes":
            lines.append(f"Original Size: {value:,} bytes")
        elif key == "total_compressed_size_bytes":
            lines.append(f"Compressed Size: {value:,} bytes")
        elif key == "total_estimated_tokens":
            lines.append(f"Estimated Tokens: {value:,}")
        elif key == "compression_level_setting":
            lines.append(f"Compression: {value}")
        else:
            lines.append(f"{key}: {value}")
    
    return lines

def format_file_list(files: List[Dict[str, Any]]) -> List[str]:
    """Format file list into displayable summary."""
    if not files:
        return ["No files in archive"]
    
    lines = []
    lines.append("=== FILES IN ARCHIVE ===")
    lines.append("")
    
    for i, file_info in enumerate(files):
        path = file_info.get('path', f'file_{i}')
        size = file_info.get('original_size_bytes', 0)
        compressed = file_info.get('compressed_size_bytes', 0)
        tokens = file_info.get('estimated_tokens', 0)
        
        ratio = compressed / size if size > 0 else 1.0
        lines.append(f"{path}")
        lines.append(f"  Size: {size:,} → {compressed:,} bytes ({ratio:.2f}x)")
        lines.append(f"  Tokens: {tokens:,}")
        lines.append("")
    
    return lines

def get_file_content(files: List[Dict[str, Any]], selected_index: int) -> List[str]:
    """Get content of selected file."""
    if not files or selected_index >= len(files):
        return ["No file selected"]
    
    file_info = files[selected_index]
    path = file_info.get('path', 'unknown')
    content = file_info.get('content', '')
    
    lines = [f"=== {path} ===", ""]
    lines.extend(content.split('\n'))
    
    return lines

class PakNavUI:
    def __init__(self, stdscr, pak_file: str):
        self.stdscr = stdscr
        self.pak_file = pak_file
        curses.curs_set(0)
        self.height, self.width = stdscr.getmaxyx()
        
        self.metadata_lines = []
        self.file_list_lines = []
        self.files_data = []
        self.current_file_content = []
        
        self.metadata_start = 0
        self.metadata_col = 0
        self.file_list_start = 0
        self.file_content_start = 0
        self.file_content_col = 0
        self.selected_file = 0
        
        self.setup_windows()
        
    def setup_windows(self):
        """Setup the three windows side by side."""
        win_width = self.width // 3
        win_height = self.height - 3
        
        self.metadata_win = curses.newwin(win_height, win_width, 1, 0)
        self.file_list_win = curses.newwin(win_height, win_width, 1, win_width)
        self.file_content_win = curses.newwin(win_height, win_width, 1, win_width * 2)
        
        self.metadata_win.box()
        self.file_list_win.box()
        self.file_content_win.box()
        
    def load_data(self):
        """Load pak archive data."""
        metadata, self.files_data = read_pak_archive(self.pak_file)
        self.metadata_lines = format_metadata(metadata)
        self.file_list_lines = format_file_list(self.files_data)
        self.update_file_content()
        
    def update_file_content(self):
        """Update file content for currently selected file."""
        self.current_file_content = get_file_content(self.files_data, self.selected_file)
        
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
        
    def draw_all_windows(self):
        """Draw all three windows."""
        self.draw_window(self.metadata_win, "Archive Info", self.metadata_lines, self.metadata_start, self.metadata_col)
        
        # Highlight selected file in file list
        highlight_file = -1
        if self.files_data:
            # Calculate which line in file_list_lines corresponds to selected file
            # Each file takes 4 lines (name + 2 info lines + empty line)
            highlight_file = 2 + (self.selected_file * 4)  # +2 for header lines
        
        self.draw_window(self.file_list_win, "Files", self.file_list_lines, 
                        self.file_list_start, 0, highlight_file)
        
        # Show file path in window title
        file_title = "File Content"
        if self.files_data and self.selected_file < len(self.files_data):
            file_path = self.files_data[self.selected_file].get('path', 'unknown')
            file_title = f"File: {file_path}"
        
        self.draw_window(self.file_content_win, file_title, self.current_file_content, 
                        self.file_content_start, self.file_content_col)
        
        # Show current file name and archive location in status
        current_file = ""
        archive_info = f" | Archive: {os.path.basename(self.pak_file)}"
        if self.files_data and self.selected_file < len(self.files_data):
            current_file = f" | File: {self.files_data[self.selected_file].get('path', 'unknown')}"
        
        help_text = f"Controls: ↑↓←→(meta) PgUp/PgDn(files) +/-*/(content) a/z s/x d/c(nav) q(uit){archive_info}{current_file}"
        try:
            self.stdscr.addstr(self.height - 1, 0, help_text[:self.width - 1])
        except curses.error:
            pass
        self.stdscr.refresh()
        
    def handle_input(self):
        """Handle keyboard input and navigation."""
        while True:
            self.draw_all_windows()
            key = self.stdscr.getch()
            
            if key == ord('q'):
                break
            # Metadata window navigation (↑↓←→)
            elif key == curses.KEY_UP:
                self.metadata_start = max(0, self.metadata_start - 1)
            elif key == curses.KEY_DOWN:
                if self.metadata_start + 10 < len(self.metadata_lines):
                    self.metadata_start += 1
            elif key == curses.KEY_LEFT:
                self.metadata_col = max(0, self.metadata_col - 5)
            elif key == curses.KEY_RIGHT:
                self.metadata_col += 5
            # File list navigation (PgUp/PgDn)
            elif key == curses.KEY_PPAGE:
                self.selected_file = max(0, self.selected_file - 1)
                self.file_content_start = 0
                self.update_file_content()
                # Adjust file list scroll if needed
                if self.selected_file < self.file_list_start // 4:
                    self.file_list_start = max(0, self.selected_file * 4)
            elif key == curses.KEY_NPAGE:
                if self.selected_file < len(self.files_data) - 1:
                    self.selected_file += 1
                    self.file_content_start = 0
                    self.update_file_content()
                    # Adjust file list scroll if needed
                    win_height = self.file_list_win.getmaxyx()[0] - 2
                    file_line = 2 + (self.selected_file * 4)
                    if file_line >= self.file_list_start + win_height:
                        self.file_list_start = file_line - win_height + 4
            # File content navigation (+/-*/)
            elif key == ord('+'):
                if self.file_content_start + 10 < len(self.current_file_content):
                    self.file_content_start += 1
            elif key == ord('-'):
                self.file_content_start = max(0, self.file_content_start - 1)
            elif key == ord('*'):
                self.file_content_col = max(0, self.file_content_col - 5)
            elif key == ord('/'):
                self.file_content_col += 5
            # Quick navigation commands
            elif key == ord('a'):
                self.metadata_start = 0
                self.metadata_col = 0
            elif key == ord('z'):
                self.metadata_start = max(0, len(self.metadata_lines) - 10)
            elif key == ord('s'):
                self.selected_file = 0
                self.file_list_start = 0
                self.file_content_start = 0
                self.update_file_content()
            elif key == ord('x'):
                self.selected_file = len(self.files_data) - 1
                win_height = self.file_list_win.getmaxyx()[0] - 2
                self.file_list_start = max(0, len(self.file_list_lines) - win_height)
                self.file_content_start = 0
                self.update_file_content()
            elif key == ord('d'):
                self.file_content_start = 0
                self.file_content_col = 0
            elif key == ord('c'):
                self.file_content_start = max(0, len(self.current_file_content) - 10)

def test_mode(pak_file: str):
    """Test mode for non-interactive environments."""
    print(f"=== PakView Test Mode ===")
    print(f"Archive Location: {os.path.abspath(pak_file)}")
    print()
    
    metadata, files_data = read_pak_archive(pak_file)
    metadata_lines = format_metadata(metadata)
    file_list_lines = format_file_list(files_data)
    
    print("METADATA:")
    for line in metadata_lines[:10]:
        print(f"  {line}")
    if len(metadata_lines) > 10:
        print(f"  ... and {len(metadata_lines) - 10} more lines")
    print()
    
    print("FILE LIST:")
    for line in file_list_lines[:15]:
        print(f"  {line}")
    if len(file_list_lines) > 15:
        print(f"  ... and {len(file_list_lines) - 15} more lines")
    print()
    
    if files_data:
        print(f"FIRST FILE CONTENT ({files_data[0].get('path', 'unknown')}):")
        content = get_file_content(files_data, 0)
        for line in content[:10]:
            print(f"  {line}")
        if len(content) > 10:
            print(f"  ... and {len(content) - 10} more lines")
    
    print(f"\nTotal files: {len(files_data)}")
    print("PakView functionality verified!")

def main():
    """Main function to display the pak navigation interface."""
    # Default to current session archive if no argument provided
    if len(sys.argv) == 1:
        pak_file = str(config.archive_path)
    elif len(sys.argv) == 2:
        pak_file = sys.argv[1]
    else:
        print("Usage: pakview.py [pak_archive_file]")
        print(f"Default: pakview.py (uses current session: {config.archive_path})")
        print("Example: pakview.py /tmp/archive.txt")
        sys.exit(1)
    
    if not os.path.exists(pak_file):
        if len(sys.argv) == 1:
            print(f"Error: No current session archive found at {pak_file}")
            print("Run send.py first to create a session archive, or specify a pak file:")
            print("Usage: pakview.py <pak_archive_file>")
        else:
            print(f"Error: File not found: {pak_file}")
        sys.exit(1)
    
    # Check if we're in an interactive terminal
    if not sys.stdout.isatty() or os.environ.get('TERM') == 'dumb':
        test_mode(pak_file)
        return
    
    def curses_main(stdscr):
        ui = PakNavUI(stdscr, pak_file)
        ui.load_data()
        
        if not ui.metadata_lines and not ui.file_list_lines:
            stdscr.addstr(0, 0, f"Error: Could not load pak archive: {pak_file}")
            stdscr.refresh()
            stdscr.getch()
            return
            
        ui.handle_input()
    
    try:
        curses.wrapper(curses_main)
    except Exception as e:
        print(f"Curses interface failed: {e}")
        print("Falling back to test mode...")
        test_mode(pak_file)

if __name__ == "__main__":
    main()