from jinja2 import Environment, FileSystemLoader

class ReportRenderer:
    def __init__(self, template_dir='src/templates', template_file='report.html', threshold_low=10.0, threshold_high=20.0):
        import os
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters['basename'] = lambda path: os.path.basename(path) if path else ""
        self.template_file = template_file
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def render(self, structured, problem_roots, problem_file_threshold=None, threshold_low=None, threshold_high=None):
        template = self.env.get_template(self.template_file)
        return template.render(
            structured=structured,
            problem_roots=problem_roots,
            threshold_low=threshold_low if threshold_low is not None else self.threshold_low,
            threshold_high=threshold_high if threshold_high is not None else self.threshold_high,
            problem_file_threshold=problem_file_threshold
        )
