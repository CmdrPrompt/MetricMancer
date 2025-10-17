from src.report.report_format_strategy import ReportFormatStrategy
from src.report.report_renderer import ReportRenderer
from src.report.report_writer import ReportWriter
from src.kpis.model import RepoInfo


class HTMLReportFormat(ReportFormatStrategy):
    def __init__(self, template_dir='src/report/templates', template_file='report.html'):
        self.template_dir = template_dir
        self.template_file = template_file

    def print_report(self, repo_info: RepoInfo, debug_print, output_file='complexity_report.html',
                     threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, report_links=None, **kwargs):
        """
        Generates an HTML report directly from a RepoInfo object.
        """
        renderer = ReportRenderer(
            template_dir=self.template_dir,
            template_file=self.template_file,
            threshold_low=threshold_low,
            threshold_high=threshold_high
        )

        html = renderer.render(
            repo_info=repo_info,
            problem_file_threshold=problem_file_threshold,
            report_links=report_links
        )

        ReportWriter.write_html(html, output_file)
        print(f"[OK] Report generated: {output_file}")
