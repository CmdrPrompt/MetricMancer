from .report_data_collector import ReportDataCollector
from .report_data_analyzer import ReportDataAnalyzer
from .report_renderer import ReportRenderer
from .report_writer import ReportWriter

class ReportGenerator:
	def __init__(self, results, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, template_dir='src/templates', template_file='report.html'):
		self.results = results
		self.threshold_low = threshold_low
		self.threshold_high = threshold_high
		self.problem_file_threshold = problem_file_threshold
		self.template_dir = template_dir
		self.template_file = template_file

	def generate(self, output_file='komplexitet_rapport.html'):
		collector = ReportDataCollector(self.results, self.threshold_low, self.threshold_high)
		analyzer = ReportDataAnalyzer(self.results, self.threshold_high, self.problem_file_threshold, self.threshold_low, self.threshold_high)
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
		print(f"✅ Report generated: {output_file}")
