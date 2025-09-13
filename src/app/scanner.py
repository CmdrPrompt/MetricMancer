import os
from src.languages.config import LANGUAGES

class Scanner:
    def __init__(self, config):
        self.config = config

    def scan(self, directories):
        from src.utilities.debug import debug_print
        files = []
        debug_print(f"[DEBUG] Scanner.scan: directories={directories}")
        for scan_dir in directories:
            abs_scan_dir = os.path.abspath(scan_dir)
            if not os.path.isdir(abs_scan_dir):
                debug_print(f"⚠️ Folder '{abs_scan_dir}' doesn't exist – skipping.")
                continue
            # If the root directory itself is hidden, skip it entirely
            if os.path.basename(abs_scan_dir).startswith('.'):
                debug_print(f"[DEBUG] Skipping hidden root directory: {abs_scan_dir}")
                continue
            for root, dirs, file_list in os.walk(abs_scan_dir):
                # Remove hidden directories from traversal at every level
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                # If any part of the current root's path (relative to abs_scan_dir) is hidden, skip this root
                rel_path_parts = os.path.relpath(root, abs_scan_dir).split(os.sep)
                if any(part.startswith('.') for part in rel_path_parts if part != '.'):
                    debug_print(f"[DEBUG] Skipping hidden subdirectory: {root}")
                    continue
                for file in file_list:
                    # Skip hidden files as well
                    if file.startswith('.'):
                        continue
                    ext = os.path.splitext(file)[1]
                    if ext in LANGUAGES:
                        full_path = os.path.abspath(os.path.join(root, file))
                        debug_print(f"[DEBUG] Scanner.scan: abs_scan_dir={abs_scan_dir}, full_path={full_path}, ext={ext}")
                        files.append({
                            'path': full_path,
                            'root': abs_scan_dir,
                            'ext': ext
                        })
        debug_print(f"[DEBUG] Scanner.scan: total code files found={len(files)}")
        return files
