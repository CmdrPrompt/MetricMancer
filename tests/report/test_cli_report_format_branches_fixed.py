"""
Branch coverage test for CLI report format - demonstrates testing conditional logic.

This test file focuses on improving branch coverage by testing all conditional paths
in the CLI report formatting logic, especially file filtering and statistics calculation.
"""

from unittest.mock import MagicMock
from src.report.cli.cli_report_format import CLIReportFormat
from src.kpis.model import RepoInfo, ScanDir, File
from src.kpis.complexity.kpi import ComplexityKPI
from src.kpis.codechurn.kpi import ChurnKPI
from src.kpis.hotspot.hotspot_kpi import HotspotKPI


class TestCLIReportFormatBranches:
    """Test branch coverage for CLI report format conditional logic."""

    def setup_method(self):
        """Setup test data for each test."""
        self.formatter = CLIReportFormat()

    def create_mock_file(self, name, complexity=10, churn=5, ownership_data=None, shared_data=None):
        """Helper to create mock file with KPIs."""
        file_obj = File(
            name=name,
            file_path=f"src/{name}",
            kpis={},
            functions=[]
        )

        # Add complexity KPI
        complexity_kpi = ComplexityKPI()
        complexity_kpi.value = complexity
        complexity_kpi.name = 'complexity'
        file_obj.kpis['complexity'] = complexity_kpi

        # Add churn KPI
        churn_kpi = ChurnKPI()
        churn_kpi.value = churn
        churn_kpi.name = 'churn'
        file_obj.kpis['churn'] = churn_kpi

        # Add hotspot KPI
        hotspot_kpi = HotspotKPI()
        hotspot_kpi.value = complexity * churn
        hotspot_kpi.name = 'hotspot'
        file_obj.kpis['hotspot'] = hotspot_kpi

        # Add ownership KPI with mock object
        ownership_kpi = MagicMock()
        ownership_kpi.value = ownership_data
        ownership_kpi.name = 'Code Ownership'
        file_obj.kpis['Code Ownership'] = ownership_kpi

        # Add shared ownership KPI
        shared_kpi = MagicMock()
        shared_kpi.value = shared_data or {}
        shared_kpi.name = 'Shared Ownership'
        file_obj.kpis['Shared Ownership'] = shared_kpi

        return file_obj

    def create_repo_info(self, name="test"):
        """Helper to create RepoInfo with correct parameters."""
        return RepoInfo(
            repo_name=name,
            repo_root_path=".",
            dir_name=name,
            scan_dir_path="."
        )

    def test_file_filtering_with_valid_ownership_data(self):
        """Test file filtering branch when ownership data is valid dict."""
        # Create file with valid ownership data
        ownership_data = {"john": 60, "jane": 40}
        file_obj = self.create_mock_file("test.py", ownership_data=ownership_data)

        # Create repo with this file
        repo_info = self.create_repo_info()
        repo_info.files["test.py"] = file_obj

        # Test file filtering - should include this file
        all_files = self.formatter._collect_all_files(repo_info)
        assert len(all_files) == 1
        assert all_files[0].name == "test.py"

    def test_statistics_calculation_with_empty_file_list(self):
        """Test statistics calculation branch when no files are present."""
        # Create empty repo
        repo_info = self.create_repo_info("empty")

        # Test statistics calculation with empty file list
        stats_str, files = self.formatter._get_repo_stats(repo_info)

        assert stats_str == "[No files analyzed]"
        assert files == []

    def test_statistics_calculation_with_files_missing_kpis(self):
        """Test statistics calculation branch when files have missing KPIs."""
        # Create file with ownership but missing complexity KPI (should be treated as tracked but with 0 values)
        file_obj = self.create_mock_file("incomplete.py", complexity=0, churn=0, ownership_data={"author1": 100.0})
        # Remove complexity KPI to test missing KPI handling
        del file_obj.kpis['complexity']

        repo_info = self.create_repo_info()
        repo_info.files["incomplete.py"] = file_obj

        # Test statistics calculation - should handle missing KPIs gracefully
        stats_str, files = self.formatter._get_repo_stats(repo_info)

        # Should have default values when KPIs are missing but file is tracked
        assert "Avg. C:0" in stats_str
        assert "Avg. Churn:0" in stats_str

    def test_statistics_calculation_with_some_files_having_kpis(self):
        """Test statistics calculation branch with mixed KPI availability."""
        # Create files with different KPI availability
        file1 = self.create_mock_file("complete.py", complexity=20, churn=10, ownership_data={"author1": 100.0})
        file2 = self.create_mock_file("incomplete.py", complexity=0, churn=5, ownership_data={"author1": 100.0})
        # Remove complexity from second file to test mixed availability
        del file2.kpis['complexity']

        repo_info = self.create_repo_info()
        repo_info.files["complete.py"] = file1
        repo_info.files["incomplete.py"] = file2

        stats_str, files = self.formatter._get_repo_stats(repo_info)

        # Should calculate stats based only on files with KPIs
        assert "Avg. C:20" in stats_str  # Only one file has complexity
        assert "Avg. Churn:7.5" in stats_str  # Average of 10 and 5

    def test_ownership_display_format_with_error(self):
        """Test ownership display branch when ownership data contains error."""
        # Create file with ownership error
        ownership_data = {"error": "Git blame failed"}
        file_obj = self.create_mock_file("error_file.py", ownership_data=ownership_data)

        # Test formatting
        stats_str = self.formatter._format_file_stats(file_obj)

        assert "Ownership: ERROR" in stats_str

    def test_ownership_display_format_with_many_owners(self):
        """Test ownership display branch when there are more than 3 owners."""
        # Create file with many owners (tests the >3 owners branch)
        ownership_data = {
            "alice": 40,
            "bob": 25,
            "charlie": 15,
            "david": 10,
            "eve": 10
        }
        file_obj = self.create_mock_file("many_owners.py", ownership_data=ownership_data)

        stats_str = self.formatter._format_file_stats(file_obj)

        # Should show top 3 owners plus "more" indicator
        assert "alice 40%" in stats_str
        assert "bob 25%" in stats_str
        assert "charlie 15%" in stats_str
        assert "+ 2 more" in stats_str

    def test_ownership_display_format_with_few_owners(self):
        """Test ownership display branch when there are 3 or fewer owners."""
        # Create file with few owners (tests the <=3 owners branch)
        ownership_data = {"alice": 60, "bob": 40}
        file_obj = self.create_mock_file("few_owners.py", ownership_data=ownership_data)

        stats_str = self.formatter._format_file_stats(file_obj)

        # Should show all owners without "more" indicator
        assert "alice 60%" in stats_str
        assert "bob 40%" in stats_str
        assert "more" not in stats_str

    def test_format_file_stats_with_missing_kpi_values(self):
        """Test file stats formatting branch when KPI values are missing."""
        # Create file with missing KPI objects
        file_obj = File(name="minimal.py", file_path="src/minimal.py", kpis={}, functions=[])

        # Test formatting with missing KPIs
        stats_str = self.formatter._format_file_stats(file_obj)

        # Should handle missing KPIs with '?' placeholders
        assert "?" in stats_str

    def test_has_tracked_files_with_valid_ownership(self):
        """Test _has_tracked_files branch when files have valid ownership."""
        # Create file with valid ownership
        ownership_data = {"alice": 100}
        tracked_file = self.create_mock_file("tracked.py", ownership_data=ownership_data)

        # Create directory with tracked file
        scan_dir = ScanDir(
            dir_name="src",
            scan_dir_path="src",
            repo_root_path=".",
            repo_name="test"
        )
        scan_dir.files["tracked.py"] = tracked_file

        # Test - should find tracked file (now uses internal _is_tracked_file method)
        result = self.formatter._has_tracked_files(scan_dir)
        assert result is True

    def test_has_tracked_files_with_no_ownership(self):
        """Test _has_tracked_files branch when files have no ownership."""
        # Create file with no ownership
        untracked_file = self.create_mock_file("untracked.py", ownership_data=None)

        scan_dir = ScanDir(
            dir_name="src",
            scan_dir_path="src",
            repo_root_path=".",
            repo_name="test"
        )
        scan_dir.files["untracked.py"] = untracked_file

        # Test - should not find any tracked files (now uses internal _is_tracked_file method)
        result = self.formatter._has_tracked_files(scan_dir)
        assert result is False

    def test_collect_all_files_with_nested_structure(self):
        """Test file collection branch with deeply nested directory structure."""
        # Create deeply nested structure
        repo_info = self.create_repo_info("nested")

        # Level 1
        level1 = ScanDir(
            dir_name="level1",
            scan_dir_path="level1",
            repo_root_path=".",
            repo_name="nested"
        )
        repo_info.scan_dirs["level1"] = level1

        # Level 2
        level2 = ScanDir(
            dir_name="level2",
            scan_dir_path="level1/level2",
            repo_root_path=".",
            repo_name="nested"
        )
        level1.scan_dirs["level2"] = level2

        # Add file at level 2 with proper ownership data
        file_obj = self.create_mock_file("deep.py", complexity=10, churn=5, ownership_data={"author1": 100.0})
        level2.files["deep.py"] = file_obj

        # Test collection - should find file in nested structure
        all_files = self.formatter._collect_all_files(repo_info)
        assert len(all_files) == 1
        assert all_files[0].name == "deep.py"

    def test_statistics_calculation_with_zero_values(self):
        """Test statistics calculation branch with zero complexity/churn values."""
        # Create file with zero values but proper ownership data
        file_obj = self.create_mock_file("zero.py", complexity=0, churn=0, ownership_data={"author1": 100.0})

        repo_info = self.create_repo_info()
        repo_info.files["zero.py"] = file_obj

        # Test statistics with zero values
        stats_str, files = self.formatter._get_repo_stats(repo_info)

        assert "Avg. C:0" in stats_str
        assert "Avg. Churn:0" in stats_str
        assert "Avg. Churn:0" in stats_str

    def test_statistics_calculation_min_max_values(self):
        """Test statistics calculation branch for min/max calculations."""
        # Create files with different complexity values to test min/max
        file1 = self.create_mock_file("low.py", complexity=5, churn=2, ownership_data={"author1": 100.0})
        file2 = self.create_mock_file("high.py", complexity=25, churn=8, ownership_data={"author1": 100.0})
        file3 = self.create_mock_file("medium.py", complexity=15, churn=5, ownership_data={"author1": 100.0})

        repo_info = self.create_repo_info()
        repo_info.files["low.py"] = file1
        repo_info.files["high.py"] = file2
        repo_info.files["medium.py"] = file3

        # Test statistics calculation
        stats_str, files = self.formatter._get_repo_stats(repo_info)

        # Should have correct min, max, and average
        assert "Min C:5" in stats_str
        assert "Max C:25" in stats_str
        assert "Avg. C:15" in stats_str  # (5+25+15)/3 = 15


class TestCLIReportFormatOwnershipBranches:
    """Test ownership-specific branch logic."""

    def setup_method(self):
        self.formatter = CLIReportFormat()

    def test_ownership_with_na_format(self):
        """Test ownership branch when data has 'N/A' format."""
        # Create mock file with N/A ownership format
        file_obj = File(name="na_file.py", file_path="src/na_file.py", kpis={}, functions=[])

        # Mock ownership KPI with N/A format
        ownership_kpi = MagicMock()
        ownership_kpi.value = {"ownership": "N/A"}
        file_obj.kpis['Code Ownership'] = ownership_kpi

        stats_str = self.formatter._format_file_stats(file_obj)

        # Should not include ownership information for N/A format
        assert "Ownership:" not in stats_str or "N/A" in stats_str

    def test_ownership_with_empty_dict(self):
        """Test ownership branch when data is empty dict."""
        file_obj = File(name="empty_ownership.py", file_path="src/empty_ownership.py", kpis={}, functions=[])

        # Mock ownership KPI with empty dict
        ownership_kpi = MagicMock()
        ownership_kpi.value = {}
        file_obj.kpis['Code Ownership'] = ownership_kpi

        stats_str = self.formatter._format_file_stats(file_obj)

        # Should handle empty ownership gracefully
        assert isinstance(stats_str, str)

    def test_ownership_without_kpi(self):
        """Test ownership branch when Code Ownership KPI is missing."""
        file_obj = File(name="no_ownership.py", file_path="src/no_ownership.py", kpis={}, functions=[])

        stats_str = self.formatter._format_file_stats(file_obj)

        # Should handle missing ownership KPI gracefully
        assert "Ownership:" not in stats_str
