from src.report.report_format_strategy import ReportFormatStrategy
from src.kpis.model import RepoInfo, ScanDir, File
from typing import List
import sys
import csv

class CLICSVReportFormat(ReportFormatStrategy):

    def _collect_flat_list(self, scan_dir: ScanDir, level: str) -> List[dict]:
        """Recursively traverses the data model to produce a flat list for CSV."""
        items = []
        for file_obj in scan_dir.files.values():
            file_churn = file_obj.kpis.get('churn').value if file_obj.kpis.get('churn') else None

            if level == "function":
                for func_obj in file_obj.functions:
                    func_complexity = func_obj.kpis.get('complexity').value if func_obj.kpis.get('complexity') else None
                    items.append({
                        "filename": file_obj.file_path,
                        "function_name": func_obj.name,
                        "cyclomatic_complexity": func_complexity,
                        "churn": file_churn,
                        "hotspot_score": func_complexity * file_churn if func_complexity and file_churn else None,
                    })
            else: # level == "file"
                items.append({
                    "filename": file_obj.file_path,
                    "cyclomatic_complexity": file_obj.kpis.get('complexity').value if file_obj.kpis.get('complexity') else None,
                    "churn": file_churn,
                    "hotspot_score": file_obj.kpis.get('hotspot').value if file_obj.kpis.get('hotspot') else None,
                })

        for sub_dir in scan_dir.scan_dirs.values():
            items.extend(self._collect_flat_list(sub_dir, level))
        return items

    def print_report(self, repo_info: RepoInfo, debug_print, level="file"):
        writer = csv.writer(sys.stdout, delimiter=';', lineterminator='\n')
        
        flat_data = self._collect_flat_list(repo_info, level)
        if not flat_data:
            return

        # Dynamically create header from keys of the first item
        header = list(flat_data[0].keys())
        # Add repo_name to header
        header.append("repo_name")
        writer.writerow(header)

        if level == "function":
            for item in flat_data:
                writer.writerow([item.get(h) for h in header[:-1]] + [repo_info.repo_name])