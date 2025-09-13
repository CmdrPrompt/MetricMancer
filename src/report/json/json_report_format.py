import json
from src.report.report_format_strategy import ReportFormatStrategy

class JSONReportFormat(ReportFormatStrategy):
    def print_report(self, repo_info, debug_print, level="file"):
        import os
        import json
        root = getattr(repo_info, 'repo_root', None)
        repo_name = getattr(repo_info, 'git_folder_name', None) or getattr(repo_info, 'repo_name', None)
        timestamp = getattr(repo_info, 'timestamp', None)
        component = getattr(repo_info, 'component', None)
        team = getattr(repo_info, 'team', None)
        results = getattr(repo_info, 'results', {})
        output = []
        # File-level: print all files in a single JSON array
        if level == 'file':
            for language in results:
                for scan_root in results[language]:
                    files = results[language][scan_root]
                    for file in files:
                        file_path = file.get('path', '')
                        abs_path = os.path.abspath(file_path) if not os.path.isabs(file_path) else file_path
                        rel_path = os.path.relpath(abs_path, root) if root else file_path
                        rel_path = rel_path.replace('..', '').lstrip('/')
                        complexity = file.get('complexity', None)
                        churn = file.get('churn', None)
                        grade = file.get('grade', None)
                        if complexity is not None and churn is not None:
                            try:
                                hotspot_score = round(float(complexity) * float(churn), 1)
                            except Exception:
                                hotspot_score = None
                        else:
                            hotspot_score = None
                        file_json = {
                            "filename": rel_path,
                            "cyclomatic_complexity": complexity,
                            "churn": churn,
                            "hotspot_score": hotspot_score,
                            "grade": grade,
                            "repo_name": repo_name,
                            "component": component,
                            "team": team,
                            "timestamp": timestamp
                        }
                        output.append(file_json)
            print(json.dumps(output, ensure_ascii=False))
        # Function-level: print all functions in a single JSON array
        elif level == 'function':
            for language in results:
                for scan_root in results[language]:
                    files = results[language][scan_root]
                    for file in files:
                        file_path = file.get('path', '')
                        abs_path = os.path.abspath(file_path) if not os.path.isabs(file_path) else file_path
                        rel_path = os.path.relpath(abs_path, root) if root else file_path
                        rel_path = rel_path.replace('..', '').lstrip('/')
                        complexity = file.get('complexity', None)
                        churn = file.get('churn', None)
                        grade = file.get('grade', None)
                        hotspot_score = None
                        if complexity is not None and churn is not None:
                            try:
                                hotspot_score = round(float(complexity) * float(churn), 1)
                            except Exception:
                                hotspot_score = None
                        if 'functions' in file and isinstance(file['functions'], list):
                            for func in file['functions']:
                                func_json = {
                                    "function_name": func.get("name", ""),
                                    "cyclomatic_complexity": func.get("complexity", None),
                                    "churn": churn,
                                    "hotspot_score": func.get("hotspot_score", hotspot_score),
                                    "grade": grade,
                                    "lines_of_code": func.get("lines_of_code", None),
                                    "filename": rel_path,
                                    "repo_name": repo_name,
                                    "component": component,
                                    "team": team,
                                    "timestamp": timestamp
                                }
                                output.append(func_json)
                        else:
                            # fallback to file-level if no functions
                            file_json = {
                                "function_name": None,
                                "cyclomatic_complexity": complexity,
                                "churn": churn,
                                "hotspot_score": hotspot_score,
                                "grade": grade,
                                "lines_of_code": None,
                                "filename": rel_path,
                                "repo_name": repo_name,
                                "component": component,
                                "team": team,
                                "timestamp": timestamp
                            }
                            output.append(file_json)
            print(json.dumps(output, ensure_ascii=False))
    def get_repo_json(self, repo_info, debug_print, level="file"):
        import os
        timestamp = getattr(repo_info, 'timestamp', None)
        root = getattr(repo_info, 'repo_root', None)
        repo_name = getattr(repo_info, 'git_folder_name', None) or getattr(repo_info, 'repo_name', None)
        scan_directories = []
        for language in getattr(repo_info, 'results', {}):
            for scan_root in repo_info.results[language]:
                files = repo_info.results[language][scan_root]
                # Gruppera filer per package
                package_map = {}
                for file in files:
                    file_path = file.get('path', '')
                    abs_path = os.path.abspath(file_path) if not os.path.isabs(file_path) else file_path
                    rel_path = os.path.relpath(abs_path, root) if root else file_path
                    rel_path = rel_path.replace('..', '').lstrip('/')  # Remove any leading ../
                    complexity = file.get('complexity', None)
                    churn = file.get('churn', None)
                    grade = file.get('grade', None)
                    package = repo_info.get_package(abs_path) if hasattr(repo_info, 'get_package') else None
                    if complexity is not None and churn is not None:
                        try:
                            hotspot_score = round(float(complexity) * float(churn), 1)
                        except Exception:
                            hotspot_score = None
                    else:
                        hotspot_score = None
                    file_json = {
                        "filename": rel_path,
                        "cyclomatic_complexity": complexity,
                        "churn": churn,
                        "hotspot_score": hotspot_score,
                        "grade": grade
                    }
                    if level == "function" and 'functions' in file and isinstance(file['functions'], list):
                        file_json["functions"] = [
                            {
                                "function_name": func.get("name", ""),
                                "cyclomatic_complexity": func.get("complexity", None),
                                "churn": churn,
                                "hotspot_score": func.get("hotspot_score", hotspot_score),
                                "grade": grade,
                                "lines_of_code": func.get("lines_of_code", None)
                            }
                            for func in file['functions']
                        ]
                    if package not in package_map:
                        package_map[package] = []
                    package_map[package].append(file_json)
                # Lägg till package-tagg per package
                packages_out = []
                for package, files_out in sorted(package_map.items()):
                    # Beräkna genomsnittliga KPI:er för package
                    complexities = [f.get("cyclomatic_complexity") for f in files_out if f.get("cyclomatic_complexity") is not None]
                    churns = [f.get("churn") for f in files_out if f.get("churn") is not None]
                    hotspot_scores = [f.get("hotspot_score") for f in files_out if f.get("hotspot_score") is not None]
                    grades = [f.get("grade") for f in files_out if f.get("grade") is not None]
                    def avg(lst):
                        return round(sum(lst)/len(lst), 1) if lst else None
                    from collections import Counter
                    avg_complexity = avg(complexities)
                    avg_churn = avg(churns)
                    avg_hotspot = avg(hotspot_scores)
                    # Definiera grade-ordning: High > Medium > Low
                    grade_order = {
                        'High ❌': 3,
                        'Medium ⚠️': 2,
                        'Low ✅': 1
                    }
                    def grade_sort_key(g):
                        return grade_order.get(g, 0)
                    max_grade = max(grades, key=grade_sort_key) if grades else None
                    packages_out.append({
                        "package": package,
                        "avg_cyclomatic_complexity": avg_complexity,
                        "avg_churn": avg_churn,
                        "avg_hotspot_score": avg_hotspot,
                        "max_grade": max_grade,
                        "files": files_out
                    })
                scan_directories.append({
                    "scan_directory": os.path.basename(scan_root),
                    "scan_directory_path": scan_root,
                    "packages": packages_out
                })
        return {
            "repo_name": repo_name,
            "repo_root": root,
            "timestamp": timestamp,
            "component": getattr(repo_info, 'component', None),
            "team": getattr(repo_info, 'team', None),
            "scan_directories": scan_directories
        }
        print(json.dumps(output, indent=2, ensure_ascii=False))
