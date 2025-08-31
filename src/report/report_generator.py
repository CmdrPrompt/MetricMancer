from .report_data_collector import ReportDataCollector
from .report_data_analyzer import ReportDataAnalyzer
from .report_renderer import ReportRenderer
from .report_writer import ReportWriter
from .report_interface import ReportInterface


class ReportGenerator(ReportInterface):
	def __init__(self, repo_info, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, template_dir='src/templates', template_file='report.html'):
		self.repo_info = repo_info
		self.results = repo_info.results
		self.threshold_low = threshold_low
		self.threshold_high = threshold_high
		self.problem_file_threshold = problem_file_threshold
		self.template_dir = template_dir
		self.template_file = template_file

	def generate(self, output_file='complexity_report.html'):
		collector = ReportDataCollector(self.repo_info, self.threshold_low, self.threshold_high)
		analyzer = ReportDataAnalyzer(self.repo_info, self.threshold_high, self.problem_file_threshold, self.threshold_low, self.threshold_high)
		renderer = ReportRenderer(self.template_dir, self.template_file, self.threshold_low, self.threshold_high)
		structured = collector.prepare_structured_data()
		problem_roots = analyzer.find_problematic_roots()
		html = renderer.render(
			structured,
			problem_roots,
			problem_file_threshold=self.problem_file_threshold,
			threshold_low=self.threshold_low,
			threshold_high=self.threshold_high
		)
		ReportWriter.write_html(html, output_file)
		print(f"\u2705 Report generated: {output_file}")
