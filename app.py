from config import Config
from scanner import Scanner
from analyzer import Analyzer
from report_generator import ReportGenerator

class ComplexityScannerApp:
    def __init__(self, directories, threshold=20.0, problem_file_threshold=None, output_file='komplexitet_rapport.html'):
        self.config = Config()
        self.scanner = Scanner(self.config)
        self.analyzer = Analyzer(self.config)
        self.directories = directories
        self.threshold = threshold
        self.problem_file_threshold = problem_file_threshold
        self.output_file = output_file

    def run(self):
        files = self.scanner.scan(self.directories)
        results = self.analyzer.analyze(files)
        report = ReportGenerator(results, self.threshold, self.problem_file_threshold)
        report.generate(self.output_file)
