from src.report.html.report_renderer import ReportRenderer
from src.kpis.model import RepoInfo, ScanDir, File
from typing import List


def generate_html_index(repos, report_files, output_file='index.html'):
    """
    repos: List of RepoInfo objects.
    report_files: List of dicts with 'href', 'name', and 'repo_info'.
    output_file: Output HTML file name
    """
    def _collect_all_files(scan_dir: ScanDir) -> List[File]:
        """Recursively collects all File objects from a ScanDir tree."""
        files = list(scan_dir.files.values())
        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(_collect_all_files(sub_dir))
        return files

    # Prepare summary data for each repo
    repo_summaries = []
    for rf in report_files:
        repo_info: RepoInfo = rf['repo_info']
        all_files = _collect_all_files(repo_info)

        summary = {
            'repo_name': repo_info.repo_name,
            'kpis': {},
            'report_file': rf['href']
        }

        complexities = [f.kpis['complexity'].value for f in all_files
                        if 'complexity' in f.kpis and f.kpis['complexity']]
        churns = [f.kpis['churn'].value for f in all_files if 'churn' in f.kpis and f.kpis['churn']]
        hotspots = [f.kpis['hotspot'].value for f in all_files if 'hotspot' in f.kpis and f.kpis['hotspot']]

        def avg(lst):
            return round(sum(lst) / len(lst), 2) if lst else None

        summary['kpis']['avg_complexity'] = avg(complexities)
        summary['kpis']['avg_churn'] = avg(churns)
        summary['kpis']['total_hotspot'] = round(sum(hotspots), 1) if hotspots else 0

        repo_summaries.append(summary)

    # Render index.html using a template
    renderer = ReportRenderer(template_dir='src/report/templates', template_file='index.html')
    html = renderer.env.get_template('index.html').render(
        repo_summaries=repo_summaries
    )
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\u2705 Index page generated: {output_file}")
