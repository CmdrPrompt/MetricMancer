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
        if is_dataclass(obj):
            # Use asdict for a deep conversion of the dataclass
            return self._to_dict(asdict(obj))
        return obj

    def _collect_flat_list(self, scan_dir: ScanDir, level: str) -> List[dict]:
        """
        Recursively traverses the data model to produce a flat list of
        file or function data, suitable for machine processing.
        """
        items = []
        
        # Add metadata from the top-level repo_info object
        repo_name = getattr(scan_dir, 'repo_name', None)
        timestamp = getattr(scan_dir, 'timestamp', None) if hasattr(scan_dir, 'timestamp') else None
        component = getattr(scan_dir, 'component', None) if hasattr(scan_dir, 'component') else None
        team = getattr(scan_dir, 'team', None) if hasattr(scan_dir, 'team') else None

        for file_obj in scan_dir.files.values():
            file_churn = file_obj.kpis.get('churn', {}).get('value')

            if level == "function":
                for func_obj in file_obj.functions:
                    func_complexity = func_obj.kpis.get('complexity', {}).get('value')
                    items.append({
                        "filename": file_obj.file_path,
                        "function_name": func_obj.name,
                        "cyclomatic_complexity": func_complexity,
                        "churn": file_churn,
                        "hotspot_score": func_complexity * file_churn if func_complexity and file_churn else 0,
                        "repo_name": repo_name, "component": component, "team": team, "timestamp": timestamp
                    })
            else: # level == "file"
                items.append({
                    "filename": file_obj.file_path,
                    "cyclomatic_complexity": file_obj.kpis.get('complexity', {}).get('value'),
                    "churn": file_churn,
                    "hotspot_score": file_obj.kpis.get('hotspot', {}).get('value'),
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
