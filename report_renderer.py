from jinja2 import Environment, FileSystemLoader

class ReportRenderer:
    def __init__(self, template_dir='templates', template_file='report.html', threshold=20.0):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template_file = template_file
        self.threshold = threshold

    def render(self, structured, problem_roots):
        template = self.env.get_template(self.template_file)
        return template.render(languages=structured, problem_roots=problem_roots, threshold=self.threshold)
