import os
from src.config import LANGUAGES

class Scanner:
    def __init__(self, config):
        self.config = config

    def scan(self, directories):
        files = []
        for root_dir in directories:
            if not os.path.isdir(root_dir):
                print(f"⚠️ Folder '{root_dir}' doesn't exist – skipping.")
                continue
            for root, _, file_list in os.walk(root_dir):
                for file in file_list:
                    ext = os.path.splitext(file)[1]
                    if ext in LANGUAGES:
                        full_path = os.path.join(root, file)
                        files.append({
                            'path': full_path,
                            'root': root_dir,
                            'ext': ext
                        })
        return files
