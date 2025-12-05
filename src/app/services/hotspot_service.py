"""
Service for extracting and displaying code hotspots.

This service encapsulates hotspot analysis logic, improving separation
of concerns and testability.
"""

from typing import Optional, List
from src.app.hierarchy.data_converter import DataConverter
from src.analysis.hotspot_analyzer import (
    extract_hotspots_from_data,
    format_hotspots_table,
    save_hotspots_to_file,
    print_hotspots_summary
)
from src.utilities.path_helpers import normalize_output_path


class HotspotService:
    """
    Service for extracting and displaying code hotspots.

    This class encapsulates the logic for:
    - Extracting hotspots from analyzed repositories
    - Displaying hotspots to console or saving to file
    - Aggregating hotspots from multiple repositories
    """

    def __init__(self, threshold: int, output_path: Optional[str], report_folder: str):
        """
        Initialize HotspotService.

        Args:
            threshold: Minimum hotspot score to include
            output_path: Optional file path to save hotspots (None = print to console)
            report_folder: Base folder for report output
        """
        self.threshold = threshold
        self.output_path = output_path
        self.report_folder = report_folder

    def analyze(self, repo_infos: List) -> None:
        """
        Run hotspot analysis on repositories.

        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        all_hotspots = self._extract_hotspots(repo_infos)

        if not all_hotspots:
            print(f"\n✅ No hotspots found above threshold {self.threshold}.")
            return

        self._display_or_save(all_hotspots)

    def _extract_hotspots(self, repo_infos: List) -> List:
        """
        Extract hotspots from all repo_infos.

        Args:
            repo_infos: List of RepoInfo objects

        Returns:
            List of hotspot dictionaries
        """
        all_hotspots = []
        for repo_info in repo_infos:
            # Convert repo_info to dict format using DataConverter
            repo_data = DataConverter.convert_repo_info_to_dict(repo_info)
            hotspots = extract_hotspots_from_data(repo_data, self.threshold)
            all_hotspots.extend(hotspots)
        return all_hotspots

    def _display_or_save(self, all_hotspots: List) -> None:
        """
        Display hotspots to console or save to file.

        Args:
            all_hotspots: List of hotspot dictionaries
        """
        if self.output_path:
            output_path = normalize_output_path(self.report_folder, self.output_path)
            save_hotspots_to_file(all_hotspots, output_path, show_risk_categories=True)
            print_hotspots_summary(all_hotspots)
        else:
            print("\n" + format_hotspots_table(all_hotspots, show_risk_categories=True))
