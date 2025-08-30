from src.fileanalyzer import FileAnalyzer
from src.config import LANGUAGES
from src.metrics import grade

class Analyzer:
    def __init__(self, config, threshold_low=10.0, threshold_high=20.0):
        self.config = config.languages
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def analyze(self, files):
        results = {}
        for file in files:
            ext = file['ext']
            config = self.config[ext]
            analyzer = FileAnalyzer(file['path'], file['root'], config)
            if analyzer.load():
                result = analyzer.analyze()
                result['grade'] = grade(result['complexity'], self.threshold_low, self.threshold_high)
                lang = result.get('language')
                root = result.get('root')
                if lang and root:
                    if lang not in results:
                        results[lang] = {}
                    if root not in results[lang]:
                        results[lang][root] = []
                    results[lang][root].append(result)
        return results
