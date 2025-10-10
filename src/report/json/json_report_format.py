import json
import os
from dataclasses import is_dataclass, asdict
from src.report.report_format_strategy import ReportFormatStrategy
from src.kpis.model import RepoInfo, ScanDir, File, Function
from src.kpis.base_kpi import BaseKPI
from typing import Any, List

class JSONReportFormat(ReportFormatStrategy):

    def _to_dict(self, obj: Any) -> Any:
        """
        Recursively converts dataclass objects (RepoInfo, ScanDir, File, etc.)
        into a dictionary suitable for JSON serialization.
        """
        if isinstance(obj, dict):
            return {k: self._to_dict(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._to_dict(v) for v in obj]
        from src.kpis.base_kpi import BaseKPI
        if is_dataclass(obj):
            # Use asdict for a deep conversion of the dataclass
            return self._to_dict(asdict(obj))
        if isinstance(obj, BaseKPI):
            return self._to_dict(obj.value)
        return obj

    def _collect_flat_list(self, scan_dir: ScanDir, level: str) -> List[dict]:
        """
        Recursively traverses the data model to produce a flat list of
        file, function, and package (folder) data, suitable for machine processing.
        Only git-tracked files are included.
        """
        def is_tracked_file(file_obj: File):
            co = file_obj.kpis.get('Code Ownership')
            if not co or not hasattr(co, 'value') or not isinstance(co.value, dict):
                return True
            return not (co.value.get('ownership') == 'N/A')

        items = []
        repo_name = getattr(scan_dir, 'repo_name', None)
        timestamp = getattr(scan_dir, 'timestamp', None) if hasattr(scan_dir, 'timestamp') else None
        component = getattr(scan_dir, 'component', None) if hasattr(scan_dir, 'component') else None
        team = getattr(scan_dir, 'team', None) if hasattr(scan_dir, 'team') else None

        # Add package/folder-level aggregated KPIs
        def kpi_value(kpis, key):
            kpi = kpis.get(key)
            return kpi.value if kpi and hasattr(kpi, 'value') else None

        package_complexity = kpi_value(scan_dir.kpis, 'complexity')
        package_churn = kpi_value(scan_dir.kpis, 'churn')
        package_hotspot = kpi_value(scan_dir.kpis, 'hotspot')
        package_shared_ownership = kpi_value(scan_dir.kpis, 'Shared Ownership')
        # Aggregate all unique owners from files and subdirs
        owners_set = set()
        for file in scan_dir.files.values():
            co_val = kpi_value(file.kpis, 'Code Ownership')
            if co_val and isinstance(co_val, dict):
                owners_set.update(co_val.keys())
        for subdir in scan_dir.scan_dirs.values():
            subdir_co_val = kpi_value(subdir.kpis, 'Code Ownership')
            if subdir_co_val and isinstance(subdir_co_val, dict):
                owners_set.update(subdir_co_val.keys())
        package_code_ownership = list(owners_set)
        items.append({
            "filename": scan_dir.scan_dir_path,
            "package": scan_dir.scan_dir_path,
            "cyclomatic_complexity": package_complexity,
            "churn": package_churn,
            "hotspot_score": package_hotspot,
            "code_ownership": package_code_ownership,
            "shared_ownership": package_shared_ownership,
            "repo_name": repo_name, "component": component, "team": team, "timestamp": timestamp
        })

        for file_obj in scan_dir.files.values():
            if not is_tracked_file(file_obj):
                continue
            file_churn = kpi_value(file_obj.kpis, 'churn')
            code_ownership_value = kpi_value(file_obj.kpis, 'Code Ownership')
            shared_ownership_value = kpi_value(file_obj.kpis, 'Shared Ownership')
            file_complexity = kpi_value(file_obj.kpis, 'complexity')
            file_hotspot = kpi_value(file_obj.kpis, 'hotspot')

            if level == "function":
                for func_obj in file_obj.functions:
                    func_complexity = kpi_value(func_obj.kpis, 'complexity')
                    func_code_ownership_value = kpi_value(func_obj.kpis, 'Code Ownership')
                    func_shared_ownership_value = kpi_value(func_obj.kpis, 'Shared Ownership')
                    items.append({
                        "filename": file_obj.file_path,
                        "function_name": func_obj.name,
                        "cyclomatic_complexity": func_complexity,
                        "churn": file_churn,
                        "hotspot_score": func_complexity * file_churn if func_complexity and file_churn else 0,
                        "code_ownership": func_code_ownership_value,
                        "shared_ownership": func_shared_ownership_value,
                        "repo_name": repo_name, "component": component, "team": team, "timestamp": timestamp
                    })
            else: # level == "file"
                items.append({
                    "filename": file_obj.file_path,
                    "cyclomatic_complexity": file_complexity,
                    "churn": file_churn,
                    "hotspot_score": file_hotspot,
                    "code_ownership": code_ownership_value,
                    "shared_ownership": shared_ownership_value,
                    "repo_name": repo_name, "component": component, "team": team, "timestamp": timestamp
                })

        for sub_dir in scan_dir.scan_dirs.values():
            items.extend(self._collect_flat_list(sub_dir, level))

        return items

    def get_report_data(self, repo_info: RepoInfo, level: str = "file", hierarchical: bool = False) -> Any:
        """
        Serializes the RepoInfo object into a JSON-compatible data structure.

        Args:
            repo_info: The RepoInfo object to serialize.
            level: 'file' or 'function' for flat list output.
            hierarchical: If True, prints the full hierarchical structure.
                          Otherwise, prints a flat list based on 'level'.
        
        Returns:
            A dictionary (for hierarchical) or a list of dictionaries (for flat).
        """
        if hierarchical:
            return self._to_dict(repo_info)
        else:
            return self._collect_flat_list(repo_info, level)
