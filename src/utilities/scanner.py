import os
from src.config import LANGUAGES

class Scanner:
    def __init__(self, config):
        self.config = config

    def scan(self, directories):
        from src.utilities.debug import debug_print
        files = []
        debug_print(f"[DEBUG] Scanner.scan: directories={directories}")
        for root_dir in directories:
            abs_root_dir = os.path.abspath(root_dir)
            if not os.path.isdir(abs_root_dir):
                debug_print(f"⚠️ Folder '{abs_root_dir}' doesn't exist – skipping.")
                continue
            for root, _, file_list in os.walk(abs_root_dir):
                for file in file_list:
                    ext = os.path.splitext(file)[1]
                    if ext in LANGUAGES:
                        full_path = os.path.abspath(os.path.join(root, file))
                        debug_print(f"[DEBUG] Scanner.scan: abs_root_dir={abs_root_dir}, full_path={full_path}, ext={ext}")
                        files.append({
                            'path': full_path,
                            'root': abs_root_dir,
                            'ext': ext
                        })
        debug_print(f"[DEBUG] Scanner.scan: total code files found={len(files)}")
        return files
