from src.report.report_format_strategy import ReportFormatStrategy
from src.kpis.model import RepoInfo, ScanDir, File
from typing import List
import sys
import csv


class CLICSVReportFormat(ReportFormatStrategy):

    def _is_tracked_file(self, file_obj: File) -> bool:
        """Check if a file is tracked by git ownership."""
        co = file_obj.kpis.get('Code Ownership')
        if not co or not hasattr(co, 'value') or not isinstance(co.value, dict):
            return True
        return not (co.value.get('ownership') == 'N/A')

    def _get_file_churn(self, file_obj: File):
        """Extract churn value from file KPIs."""
        churn_kpi = file_obj.kpis.get('churn')
        return churn_kpi.value if churn_kpi else None

    def _get_kpi_value(self, obj, kpi_name):
        """Safely extract KPI value."""
        kpi = obj.kpis.get(kpi_name)
        return kpi.value if kpi else None

    def _create_file_level_item(self, file_obj: File, file_churn) -> dict:
        """Create CSV item for file-level reporting."""
        return {
            "filename": file_obj.file_path,
            "cyclomatic_complexity": self._get_kpi_value(file_obj, 'complexity'),
            "churn": file_churn,
            "hotspot_score": self._get_kpi_value(file_obj, 'hotspot'),
        }

    def _create_function_level_item(self, file_obj: File, func_obj, file_churn) -> dict:
        """Create CSV item for function-level reporting."""
        func_complexity = self._get_kpi_value(func_obj, 'complexity')
        return {
            "filename": file_obj.file_path,
            "function_name": func_obj.name,
            "cyclomatic_complexity": func_complexity,
            "churn": file_churn,
            "hotspot_score": func_complexity * file_churn if func_complexity and file_churn else None,
        }

    def _create_items_for_file(self, file_obj: File, level: str) -> List[dict]:
        """Create CSV items for a single file based on reporting level."""
        if not self._is_tracked_file(file_obj):
            return []

        file_churn = self._get_file_churn(file_obj)
        items = []

        if level == "function":
            for func_obj in file_obj.functions:
                items.append(self._create_function_level_item(file_obj, func_obj, file_churn))
        else:  # level == "file"
            items.append(self._create_file_level_item(file_obj, file_churn))

        return items

    def _collect_flat_list(self, scan_dir: ScanDir, level: str) -> List[dict]:
        """Recursively traverses the data model to produce a flat list for CSV. Only git-tracked files are included."""
        items = []

        # Process files in current directory
        for file_obj in scan_dir.files.values():
            items.extend(self._create_items_for_file(file_obj, level))

        # Recursively process subdirectories
        for sub_dir in scan_dir.scan_dirs.values():
            items.extend(self._collect_flat_list(sub_dir, level))

        return items

    def _create_header(self, flat_data: List[dict]) -> List[str]:
        """Create CSV header from data keys and add repo_name."""
        if not flat_data:
            return []
        header = list(flat_data[0].keys())
        header.append("repo_name")
        return header

    def _write_data_rows(self, writer, flat_data: List[dict], header: List[str], repo_name: str):
        """Write data rows to CSV writer."""
        for item in flat_data:
            writer.writerow([item.get(h) for h in header[:-1]] + [repo_name])

    def print_report(self, repo_info: RepoInfo, debug_print, level="file"):
        writer = csv.writer(sys.stdout, delimiter=';', lineterminator='\n')

        flat_data = self._collect_flat_list(repo_info, level)
        if not flat_data:
            return

        header = self._create_header(flat_data)
        writer.writerow(header)

        self._write_data_rows(writer, flat_data, header, repo_info.repo_name)
