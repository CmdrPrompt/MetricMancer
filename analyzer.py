import os
import re
from config import LANGUAGES

class FileAnalyzer:
    def __init__(self, filepath, root_dir, ext):
        self.filepath = filepath
        self.root_dir = root_dir
        self.ext = ext
        self.config = LANGUAGES.get(ext)
        self.code = ""

    def load(self):
        try:
            with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
                self.code = f.read()
            return True
        except Exception as e:
            print(f"⚠️ Kunde inte läsa {self.filepath}: {e}")
            return False

    def analyze(self):
        return {
            'language': self.config['name'],
            'root': self.root_dir,
            'path': os.path.relpath(self.filepath, self.root_dir),
            'functions': self._count_functions(),
            'complexity': self._calculate_complexity(),
            'grade': None
        }

    def _calculate_complexity(self):
        return 1 + sum(len(re.findall(p, self.code)) for p in self.config['patterns'])

    def _count_functions(self):
        return len(re.findall(self.config['function_pattern'], self.code))

def analyze_file(filepath, root_dir, ext):
    analyzer = FileAnalyzer(filepath, root_dir, ext)
    return analyzer.analyze() if analyzer.load() else None
