import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from tqdm import tqdm

from src.languages.config import LANGUAGES
from src.utilities.debug import debug_print


class Scanner:
    def __init__(self, config):
        self.config = config

    def scan(self, directories):
        files = []
        debug_print(f"[DEBUG] Scanner.scan: directories={directories}")

        def _scan_dir(path: Path, root: Path):
            local_files = []
            try:
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.name.startswith('.'):
                            continue
                        entry_path = path / entry.name
                        if entry.is_dir(follow_symlinks=False):
                            local_files.extend(_scan_dir(entry_path, root))
                        elif entry.is_file(follow_symlinks=False):
                            ext = entry_path.suffix
                            if ext in LANGUAGES:
                                full_path = entry_path.resolve()
                                debug_print(
                                    f"[DEBUG] Scanner.scan: scan_dir={root}, "
                                    f"full_path={full_path}, ext={ext}"
                                )
                                local_files.append({
                                    'path': str(full_path),
                                    'root': str(root),
                                    'ext': ext
                                })
            except Exception as e:
                debug_print(
                    f"[WARN] Unable to scan {path}: {e}"
                )
            return local_files

        def scan_one_dir(scan_dir_str):
            scan_dir = Path(scan_dir_str).resolve()
            if not scan_dir.is_dir():
                debug_print(
                    f"[WARN] Folder '{str(scan_dir)}' "
                    f"doesn't exist – skipping."
                )
                return []
            if scan_dir.name.startswith('.'):
                debug_print(
                    f"[DEBUG] Skipping hidden root directory: {scan_dir}"
                )
                return []
            return _scan_dir(scan_dir, scan_dir)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(scan_one_dir, d) for d in directories]
            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Scanning directories",
                unit="dir"
            ):
                files.extend(future.result())

        debug_print(
            f"[DEBUG] Scanner.scan: total code files found={len(files)}"
        )
        return files
