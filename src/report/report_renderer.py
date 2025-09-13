from jinja2 import Environment, FileSystemLoader
from src.kpis.model import RepoInfo, ScanDir, File
from typing import List

class ReportRenderer:
    """
    Renders the HTML report using Jinja2 templates and the analyzed repository data.
    Collects and filters files for reporting, and passes context to the template.
    """
    def __init__(self, template_dir='src/report/templates', template_file='report.html', threshold_low=10.0, threshold_high=20.0):
        """
        Initialize the ReportRenderer.
        Args:
            template_dir: Directory containing Jinja2 templates.
            template_file: Template file to use for rendering.
            threshold_low: Lower threshold for complexity grading.
            threshold_high: Upper threshold for complexity grading.
        """
        import os
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.env.filters['basename'] = lambda path: os.path.basename(path) if path else ""
        self.template_file = template_file
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def _collect_all_files(self, scan_dir: ScanDir) -> List[File]:
        """
        Recursively collect all File objects from a ScanDir tree.
        Args:
            scan_dir: The root ScanDir node.
        Returns:
            List of File objects in the entire tree.
        """
        files = list(scan_dir.files.values())
        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(self._collect_all_files(sub_dir))
        return files

    def render(self, repo_info: RepoInfo, problem_file_threshold=None, report_links=None, **kwargs):
        """
        Render the HTML report using the provided template and repository data.
        Args:
            repo_info: The analyzed repository data model (RepoInfo).
            problem_file_threshold: Optional threshold for flagging problematic files.
            report_links: Optional links to include in the report.
        Returns:
            Rendered HTML as a string.
        """
        template = self.env.get_template(self.template_file)

        # Collect all files to identify problem files
        all_files = self._collect_all_files(repo_info)

        # Filter out problem files based on the threshold
        problem_files = []
        if problem_file_threshold is not None:
            problem_files = [
                f for f in all_files 
                if f.kpis.get('complexity') and f.kpis['complexity'].value >= problem_file_threshold
            ]
            problem_files.sort(key=lambda f: f.kpis['complexity'].value, reverse=True)

        return template.render(
            repo_info=repo_info,
            problem_files=problem_files,
            threshold_low=self.threshold_low,
            threshold_high=self.threshold_high,
            problem_file_threshold=problem_file_threshold,
            report_links=report_links,
            # Skicka med grade-funktionen till templaten så den kan användas där
            grade=self.env.globals.get('grade')
        )
