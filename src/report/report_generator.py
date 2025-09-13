from .report_data_collector import ReportDataCollector
from .report_data_analyzer import ReportDataAnalyzer
from .report_renderer import ReportRenderer
from .report_writer import ReportWriter
from .report_interface import ReportInterface


class ReportGenerator(ReportInterface):
	def __init__(self, repo_info, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, template_dir='src/report/templates', template_file='report.html'):
		self.repo_info = repo_info
		self.results = repo_info.results
		self.threshold_low = threshold_low
		self.threshold_high = threshold_high
		self.problem_file_threshold = problem_file_threshold
		self.template_dir = template_dir
		self.template_file = template_file

	def generate(self, output_file='complexity_report.html', report_links=None):
		from .html_report_format import HTMLReportFormat
		from src.utilities.debug import debug_print
		format_strategy = HTMLReportFormat(self.template_dir, self.template_file)
		format_strategy.print_report(
			self.repo_info,
			debug_print,
			output_file=output_file,
			threshold_low=self.threshold_low,
			threshold_high=self.threshold_high,
			problem_file_threshold=self.problem_file_threshold
		)
