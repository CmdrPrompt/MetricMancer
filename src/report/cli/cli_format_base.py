"""
Base class for CLI report formatters.

Provides common functionality for file collection, KPI extraction,
and ownership validation shared across all CLI formatters.
"""

from typing import List, Dict, Any
from src.kpis.model import ScanDir, File


class CLIFormatBase:
    """
    Base class providing common utilities for CLI report formatters.

    Subclasses should inherit from both this class and ReportFormatStrategy.
    """

    def _get_kpi_value(self, kpis: Dict, kpi_name: str, default: Any = 0) -> Any:
        """
        Extract KPI value with proper None handling.

        Args:
            kpis: KPI dictionary to extract from
            kpi_name: Name of the KPI to extract
            default: Default value if KPI is missing or None

        Returns:
            KPI value or default
        """
        kpi = kpis.get(kpi_name)
        if kpi and kpi.value is not None:
            return kpi.value
        return default

    def _extract_file_kpis(self, file_obj: File) -> Dict[str, Any]:
        """
        Extract common KPIs from a file object.

        Returns dict with: complexity, cognitive_complexity, churn, hotspot
        """
        return {
            'complexity': self._get_kpi_value(file_obj.kpis, 'complexity'),
            'cognitive_complexity': self._get_kpi_value(file_obj.kpis, 'cognitive_complexity'),
            'churn': self._get_kpi_value(file_obj.kpis, 'churn'),
            'hotspot': self._get_kpi_value(file_obj.kpis, 'hotspot'),
        }

    def _has_valid_ownership(self, ownership_kpi) -> bool:
        """
        Check if ownership KPI contains valid tracking data.

        Returns False for None, empty dict, or N/A format.
        Returns True for valid ownership dictionaries with author data.
        """
        if not ownership_kpi or not hasattr(ownership_kpi, 'value'):
            return False

        value = ownership_kpi.value
        if not isinstance(value, dict) or not value:
            return False

        return value.get('ownership') != 'N/A'

    def _is_tracked_file(self, file_obj: File) -> bool:
        """
        Check if a file is tracked in git based on Code Ownership KPI.

        Args:
            file_obj: File object to check

        Returns:
            True if file is git-tracked, False otherwise
        """
        return self._has_valid_ownership(file_obj.kpis.get('Code Ownership'))

    def _has_complexity_metrics(self, file_obj: File) -> bool:
        """
        Check if file has valid complexity metrics.

        Returns True if file has either cyclomatic or cognitive complexity > 0.
        """
        complexity = self._get_kpi_value(file_obj.kpis, 'complexity')
        cognitive = self._get_kpi_value(file_obj.kpis, 'cognitive_complexity')
        return complexity > 0 or cognitive > 0

    def _collect_tracked_files(self, scan_dir: ScanDir) -> List[File]:
        """
        Recursively collect all git-tracked files from a ScanDir tree.

        Args:
            scan_dir: Directory to scan

        Returns:
            List of tracked File objects
        """
        files = [f for f in scan_dir.files.values() if self._is_tracked_file(f)]
        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(self._collect_tracked_files(sub_dir))
        return files

    def _collect_files_with_metrics(self, scan_dir: ScanDir) -> List[File]:
        """
        Recursively collect all files with complexity metrics from a ScanDir tree.

        Includes both tracked and untracked files that have complexity data.
        Useful for quick-wins analysis where git history is optional.

        Args:
            scan_dir: Directory to scan

        Returns:
            List of File objects with complexity metrics
        """
        files = [f for f in scan_dir.files.values() if self._has_complexity_metrics(f)]
        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(self._collect_files_with_metrics(sub_dir))
        return files

    def _get_file_path(self, file_obj: File) -> str:
        """
        Get the file path from a File object.

        Handles different path attributes that may be present.
        """
        if hasattr(file_obj, 'file_path') and file_obj.file_path:
            return file_obj.file_path
        if hasattr(file_obj, 'path') and file_obj.path:
            return file_obj.path
        return file_obj.name
