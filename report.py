
from report_data import ReportDataBuilder
from report_renderer import ReportRenderer
from report_writer import ReportWriter

class ReportGenerator:
    def __init__(self, results, threshold=20.0, template_dir='templates', template_file='report.html', problem_file_threshold=None):
        self.results = results
        self.threshold = threshold
        self.template_dir = template_dir
        self.template_file = template_file
        self.problem_file_threshold = problem_file_threshold if problem_file_threshold is not None else threshold

    def generate(self, output_file='komplexitet_rapport.html'):
        data_builder = ReportDataBuilder(self.results, self.threshold)
        # Pass problem_file_threshold to data_builder if supported
        if hasattr(data_builder, 'problem_file_threshold'):
            data_builder.problem_file_threshold = self.problem_file_threshold
        renderer = ReportRenderer(self.template_dir, self.template_file, self.threshold)
        structured = data_builder.prepare_structured_data()
        problem_roots = data_builder.find_problematic_roots()
        html = renderer.render(structured, problem_roots)
        ReportWriter.write_html(html, output_file)
        print(f"✅ Report generated: {output_file}")

def generate_html_report(results, output_file='komplexitet_rapport.html', threshold=20.0, problem_file_threshold=None):
    ReportGenerator(results, threshold, problem_file_threshold=problem_file_threshold).generate(output_file)
