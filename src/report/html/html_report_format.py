from src.report.report_format_strategy import ReportFormatStrategy
from src.report.html.report_data_collector import ReportDataCollector
from src.report.html.report_data_analyzer import ReportDataAnalyzer
from src.report.html.report_renderer import ReportRenderer
from src.report.html.report_writer import ReportWriter

class HTMLReportFormat(ReportFormatStrategy):
    def __init__(self, template_dir='src/report/templates', template_file='report.html'):
        self.template_dir = template_dir
        self.template_file = template_file

    def print_report(self, repo_info, debug_print, output_file='complexity_report.html', threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, report_links=None, with_churn=False, with_complexity=False, scan_dir=None):
        # Om scan_dir är angiven, filtrera results till endast denna root
        import copy
        import os
        filtered_repo_info = repo_info
        if scan_dir:
            filtered_repo_info = copy.deepcopy(repo_info)
            filtered_results = {}
            for lang, roots in repo_info.results.items():
                filtered_roots = {root: files for root, files in roots.items() if os.path.abspath(root).startswith(os.path.abspath(scan_dir))}
                if filtered_roots:
                    filtered_results[lang] = filtered_roots
            filtered_repo_info.results = filtered_results
        else:
            scan_dir = None
        collector = ReportDataCollector(filtered_repo_info, threshold_low, threshold_high)
        analyzer = ReportDataAnalyzer(filtered_repo_info, threshold_high, problem_file_threshold, threshold_low, threshold_high)
        renderer = ReportRenderer(self.template_dir, self.template_file, threshold_low, threshold_high)
        structured = collector.prepare_structured_data()
        # Bygg ett träd av filer och mappar för HTML
        from src.utilities.tree_printer import TreePrinter
        def build_tree_lines(node, prefix="", is_last=True):
            lines = []
            # Dela upp i filer och mappar
            files = [(name, value) for name, value in node.items() if not isinstance(value, dict)]
            dirs = [(name, value) for name, value in node.items() if isinstance(value, dict)]
            files_sorted = sorted(files, key=lambda x: x[0].lower())
            dirs_sorted = sorted(dirs, key=lambda x: x[0].lower())
            items = files_sorted + dirs_sorted
            for idx, (name, value) in enumerate(items):
                last = idx == len(items) - 1
                connector = "└── " if last else "├── "
                if isinstance(value, dict):
                    lines.append(f"{prefix}{connector}{name}")
                    extension = "    " if last else "│   "
                    lines.extend(build_tree_lines(value, prefix + extension, is_last=last))
                else:
                    lines.append(f"{prefix}{connector}{name} {value}")
            return lines

        # Generic summary line for all reports; can be overridden if needed
        summary_line = None
        timestamp = getattr(repo_info, 'timestamp', None)
        # För scan_dir-rapport: visa bara repo-namn och scan_dir
        repo_name = getattr(repo_info, 'git_folder_name', None) or getattr(repo_info, 'repo_name', None) or ''
        scan_dir_display = scan_dir if scan_dir else ''
        if repo_name:
            summary_line = f"Software KPI Report - {repo_name} [{os.path.basename(scan_dir_display)}]\nKPIs: [Complexity, Churn, Grade]"
        else:
            summary_line = f"Software KPI Report [{os.path.basename(scan_dir_display)}]\nKPIs: [Complexity, Churn, Grade]"
        if timestamp:
            summary_line = f"{summary_line}\nTimestamp: {timestamp}"

        tree = None
        scan_dir_lines = []
        tree_lines = []
        if isinstance(structured, list) and structured and isinstance(structured[0], dict) and 'roots' in structured[0]:
            # Filtrera så att endast aktuellt scan_dir inkluderas
            scan_dir_lines = []
            for language, roots in getattr(filtered_repo_info, 'results', {}).items():
                for root in roots:
                    if scan_dir and os.path.abspath(root) == os.path.abspath(scan_dir):
                        scan_dir_lines.append(f"│ Scan-dir: {root} (Language: {getattr(filtered_repo_info, 'language', 'unknown')})")
            file_tuples = []
            # Filtrera structured[0]['roots'] till endast aktuellt scan_dir
            filtered_roots = []
            for root in structured[0]['roots']:
                if scan_dir and hasattr(root, 'path') and os.path.abspath(root.path).startswith(os.path.abspath(scan_dir)):
                    filtered_roots.append(root)
            for root in filtered_roots:
                for file in getattr(root, 'files', []):
                    import os
                    # Visa endast filer som ligger under scan_dir
                    if scan_dir and hasattr(file, 'path') and os.path.abspath(file.path).startswith(os.path.abspath(scan_dir)):
                        rel_path = os.path.relpath(file.path, root.path) if hasattr(file, 'path') and hasattr(root, 'path') and file.path.startswith(root.path) else getattr(file, 'path', '')
                        stats_str = f"[C:{getattr(file, 'complexity', '?')}, Churn:{getattr(file, 'churn', '?')}, Grade:{getattr(file, 'grade', '?')}]"
                        file_tuples.append((rel_path, stats_str))
            if file_tuples:
                tree = TreePrinter().build_tree(file_tuples)
            if tree:
                tree_lines = build_tree_lines(tree, prefix="", is_last=True)
        # Ensure all are lists
        scan_dir_lines = scan_dir_lines if scan_dir_lines else []
        tree_lines = tree_lines if tree_lines else []
        # Only join if at least one line exists
        if summary_line or scan_dir_lines or tree_lines:
            tree_text = "\n".join([summary_line] + scan_dir_lines + tree_lines)
        else:
            tree_text = ""

        # Hotspot-analys ska också bara använda filtered_repo_info
        problem_roots = analyzer.find_problematic_roots()
        # Filtrera hotspot-analys till endast aktuellt scan_dir om det är satt
        if scan_dir:
            problem_roots = [root for root in problem_roots if os.path.abspath(root.get('root','')) == os.path.abspath(scan_dir)]
        # Always include the current file in the report_links list, marked as selected (not a hyperlink)
        current_file = output_file
        links = []
        found_current = False
        if report_links:
            for link in report_links:
                if (hasattr(link, 'href') and link.href == current_file) or (isinstance(link, dict) and link.get('href') == current_file):
                    # Mark as selected
                    links.append({**link, 'selected': True})
                    found_current = True
                else:
                    links.append({**link, 'selected': False})
        # If not found, add the current file as selected
        if not found_current:
            # Use the same <Repo> [<folder>] (filename (Current report)) format as in app.py
            git_folder = getattr(repo_info, 'git_folder_name', None)
            repo_name = getattr(repo_info, 'repo_name', None)
            scan_dirs = getattr(repo_info, 'scan_dirs', [])
            scan_root = None
            import os
            if scan_dirs:
                scan_root = os.path.basename(os.path.normpath(scan_dirs[0]))
            repo_display = git_folder or repo_name or 'Repo'
            folder_display = scan_root or 'root'
            display_name = f"{repo_display} [{folder_display}] ({current_file}) Current source tree"
            links.append({"href": current_file, "name": display_name, "selected": True})
        # Sort links by repo name (alphabetically, ignoring case)
        def sort_key(link):
            import re
            name = link.get('name', '')
            # Match pattern: <repo> [<folder>] (...)
            m = re.match(r'([^\[]+) \[([^\]]+)\]', name)
            if m:
                repo = m.group(1).strip().lower()
                folder = m.group(2).strip().lower()
            else:
                repo = ''
                folder = ''
            main_code_folders = [
                'src', 'source', 'lib', 'app', 'core', 'main', 'implementation', 'code', 'metricmancer', 'blockasistant', 'blockassistant'
            ]
            test_folders = [
                'test', 'tests', 'unittest', 'integration', 'spec'
            ]
            folder_priority = 2
            if folder in main_code_folders:
                folder_priority = 0
            elif folder in test_folders:
                folder_priority = 1
            # Sort by repo, then folder_priority, then folder name
            return (repo, folder_priority, folder)
        links_sorted = sorted(links, key=sort_key)
        html = renderer.render(
            structured,
            problem_roots,
            repo_info=repo_info,
            tree_text=tree_text,
            problem_file_threshold=problem_file_threshold,
            threshold_low=threshold_low,
            threshold_high=threshold_high,
            report_links=links_sorted,
            with_churn=with_churn,
            with_complexity=with_complexity
        )
        ReportWriter.write_html(html, output_file)
        print(f"\u2705 Report generated: {output_file}")
