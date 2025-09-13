
from .report_interface import ReportInterface



class ReportGenerator(ReportInterface):
	"""
	Main entry point for generating reports from the analyzed repository data.
	Uses a strategy pattern to select the report format (HTML by default).
	"""
	def __init__(self, repo_info, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, template_dir='src/report/templates', template_file='report.html'):
		"""
		Initialize the ReportGenerator.
		Args:
			repo_info: The analyzed repository data model (RepoInfo).
			threshold_low: Lower threshold for complexity grading.
			threshold_high: Upper threshold for complexity grading.
			problem_file_threshold: Threshold for flagging problematic files.
			template_dir: Directory containing report templates.
			template_file: Template file to use for HTML reports.
		"""
		self.repo_info = repo_info
		self.threshold_low = threshold_low
		self.threshold_high = threshold_high
		self.problem_file_threshold = problem_file_threshold
		self.template_dir = template_dir
		self.template_file = template_file

	def generate(self, output_file='complexity_report.html', report_links=None):
		"""
		Generate a report using the selected format strategy (HTML by default).
		Args:
			output_file: Output filename for the report.
			report_links: Optional links to include in the report.
		"""
		from src.report.html.html_report_format import HTMLReportFormat
		from src.utilities.debug import debug_print
		format_strategy = HTMLReportFormat(self.template_dir, self.template_file)
		format_strategy.print_report(
			self.repo_info,
			debug_print,
			output_file=output_file,
			threshold_low=self.threshold_low,
			threshold_high=self.threshold_high,
			problem_file_threshold=self.problem_file_threshold,
			report_links=report_links,
			# kwargs may include level, hierarchical, etc. (not used by HTML report)
		)
