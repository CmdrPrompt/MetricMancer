from src.config import Config
from src.scanner import Scanner
from src.analyzer import Analyzer
from src.report.report_generator import ReportGenerator

class ComplexityScannerApp:
    def __init__(self, directories, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, output_file='komplexitet_rapport.html'):
        self.config = Config()
        self.scanner = Scanner(self.config)
        self.analyzer = Analyzer(self.config, threshold_low, threshold_high)
        self.directories = directories
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold
        self.output_file = output_file

    def run(self):
        files = self.scanner.scan(self.directories)
        results = self.analyzer.analyze(files)
        report = ReportGenerator(results, self.threshold_low, self.threshold_high, self.problem_file_threshold)
        report.generate(self.output_file)
