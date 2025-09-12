from .report_format_strategy import ReportFormatStrategy
from .report_data_collector import ReportDataCollector
from .report_data_analyzer import ReportDataAnalyzer
from .report_renderer import ReportRenderer
from .report_writer import ReportWriter

class HTMLReportFormat(ReportFormatStrategy):
    def __init__(self, template_dir='src/report/templates', template_file='report.html'):
        self.template_dir = template_dir
        self.template_file = template_file

    def print_report(self, repo_info, debug_print, output_file='complexity_report.html', threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None):
        import glob
        import os
        collector = ReportDataCollector(repo_info, threshold_low, threshold_high)
        analyzer = ReportDataAnalyzer(repo_info, threshold_high, problem_file_threshold, threshold_low, threshold_high)
        renderer = ReportRenderer(self.template_dir, self.template_file, threshold_low, threshold_high)
        structured = collector.prepare_structured_data()
        problem_roots = analyzer.find_problematic_roots()

        # Bygg rapportlänkar: hitta alla rapportfiler i aktuell katalog
        report_dir = os.path.dirname(os.path.abspath(output_file)) or "."
        pattern = os.path.join(report_dir, "code-kpi-report-ComplexityScanner-*.html")
        report_files = sorted(glob.glob(pattern))
        links = []
        current_file = os.path.basename(output_file)
        for f in report_files:
            name = os.path.splitext(os.path.basename(f))[0].replace("code-kpi-report-ComplexityScanner-", "")
            links.append({
                "href": os.path.basename(f),
                "name": name,
                "selected": os.path.basename(f) == current_file
            })

        html = renderer.render(
            structured,
            problem_roots,
            problem_file_threshold=problem_file_threshold,
            threshold_low=threshold_low,
            threshold_high=threshold_high,
            report_links=links
        )
        ReportWriter.write_html(html, output_file)
        print(f"\u2705 Report generated: {output_file}")
