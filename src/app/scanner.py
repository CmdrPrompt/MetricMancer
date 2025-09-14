import os
from pathlib import Path
from src.languages.config import LANGUAGES

class Scanner:
    def __init__(self, config):
        self.config = config

    def scan(self, directories):
        from src.utilities.debug import debug_print
        files = []
        debug_print(f"[DEBUG] Scanner.scan: directories={directories}")
        for scan_dir_str in directories:
            scan_dir = Path(scan_dir_str).resolve()
            if not scan_dir.is_dir():
                debug_print(f"[WARN] Folder '{scan_dir}' doesn't exist – skipping.")
                continue
            # If the root directory itself is hidden, skip it entirely
            if scan_dir.name.startswith('.'):
                debug_print(f"[DEBUG] Skipping hidden root directory: {scan_dir}")
                continue
            for root_str, dirs, file_list in os.walk(scan_dir):
                root_path = Path(root_str)
                # Remove hidden directories from traversal at every level
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                # If any part of the current root's path (relative to scan_dir) is hidden, skip this root
                rel_path_parts = root_path.relative_to(scan_dir).parts
                if any(part.startswith('.') for part in rel_path_parts if part != '.'):
                    debug_print(f"[DEBUG] Skipping hidden subdirectory: {root_path}")
                    continue
                for file in file_list:
                    # Skip hidden files as well
                    if file.startswith('.'):
                        continue
                    file_path = root_path / file
                    ext = file_path.suffix
                    if ext in LANGUAGES:
                        full_path = file_path.resolve()
                        debug_print(f"[DEBUG] Scanner.scan: scan_dir={scan_dir}, full_path={full_path}, ext={ext}")
                        files.append({
                            'path': str(full_path),
                            'root': str(scan_dir),
                            'ext': ext
                        })
        debug_print(f"[DEBUG] Scanner.scan: total code files found={len(files)}")
        return files
