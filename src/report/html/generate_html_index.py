from src.report.html.report_renderer import ReportRenderer
import os

def generate_html_index(repos, report_files, output_file='index.html'):
    """
    repos: List of repo_info objects (GitRepoInfo)
    report_files: List of dicts with 'href', 'name', and 'repo_info' (optional)
    output_file: Output HTML file name
    """
    # Prepare summary data for each repo
    repo_summaries = []
    for rf in report_files:
        repo_info = rf['repo_info']
        scan_dir = rf.get('scan_dir')
        summary = {
            'repo_name': getattr(repo_info, 'git_folder_name', None) or getattr(repo_info, 'repo_name', ''),
            'scan_dir': os.path.basename(scan_dir) if scan_dir else '',
            'kpis': {},
            'report_file': rf['href']
        }
        # KPIs: calculate summary (avg complexity, avg churn, avg grade)
        results = getattr(repo_info, 'results', {})
        complexities = []
        churns = []
        grades = []
        for lang, roots in results.items():
            for root, files in roots.items():
                # Endast filer i detta scan_dir
                if scan_dir and os.path.abspath(root) != os.path.abspath(scan_dir):
                    continue
                for f in files:
                    if 'complexity' in f:
                        complexities.append(f['complexity'])
                    if 'churn' in f:
                        churns.append(f['churn'])
                    if 'grade' in f:
                        grades.append(f['grade'])
        def avg(lst):
            return round(sum(lst)/len(lst), 2) if lst else None
        summary['kpis']['avg_complexity'] = avg(complexities)
        summary['kpis']['avg_churn'] = avg(churns)
        # Use label for avg_grade (Low, Medium, High)
        from src.complexity.metrics import grade as grade_label
        avg_grade_val = avg(complexities)
        label = grade_label(avg_grade_val) if avg_grade_val is not None else None
        summary['kpis']['avg_grade'] = label
        # Add emoji for overall grade (Low=✅, Medium=⚠️, High=❌)
        def grade_emoji(val):
            if val is None:
                return ''
            v = str(val).lower()
            if v.startswith('l'):
                return '✅'
            elif v.startswith('m'):
                return '⚠️'
            elif v.startswith('h'):
                return '❌'
            return ''
        summary['kpis']['grade_emoji'] = grade_emoji(label)
        repo_summaries.append(summary)
    # Hämta timestamp från första repo_info som har det
    timestamp = None
    for repo_info in repos:
        ts = getattr(repo_info, 'timestamp', None)
        if ts:
            timestamp = ts
            break
    # Render index.html using a template
    renderer = ReportRenderer(template_dir='src/report/templates', template_file='index.html')
    html = renderer.env.get_template('index.html').render(
        repo_summaries=repo_summaries,
        report_files=report_files,
        timestamp=timestamp
    )
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\u2705 Index page generated: {output_file}")
