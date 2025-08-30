from config import LANGUAGES
from analyzer import FileAnalyzer

def analyze_file(filepath, root_dir, ext):
    config = LANGUAGES[ext]
    analyzer = FileAnalyzer(filepath, root_dir, config)
    if analyzer.load():
        return analyzer.analyze()
    return None
