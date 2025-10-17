import unittest
from unittest.mock import MagicMock
from src.report.cli.cli_report_format import CLIReportFormat
from src.kpis.model import RepoInfo, ScanDir, File


class TestCLISharedOwnershipFormat(unittest.TestCase):
    def setUp(self):
        self.format_strategy = CLIReportFormat()

    def test_format_file_stats_with_shared_ownership(self):
        """Test that file stats include shared ownership information."""
        # Create mock file with KPIs
        file_obj = MagicMock(spec=File)
        file_obj.name = "test.py"

        # Mock complexity, churn, hotspot KPIs
        complexity_kpi = MagicMock()
        complexity_kpi.value = 5

        churn_kpi = MagicMock()
        churn_kpi.value = 3

        hotspot_kpi = MagicMock()
        hotspot_kpi.value = 15.0

        # Mock shared ownership KPI
        shared_ownership_kpi = MagicMock()
        shared_ownership_kpi.value = {
            'num_significant_authors': 2,
            'authors': ['Alice', 'Bob'],
            'threshold': 20.0
        }

        file_obj.kpis = {
            'complexity': complexity_kpi,
            'churn': churn_kpi,
            'hotspot': hotspot_kpi,
            'Shared Ownership': shared_ownership_kpi
        }

        result = self.format_strategy._format_file_stats(file_obj)

        # Verify shared ownership is included
        self.assertIn("Shared: 2 authors (Alice, Bob)", result)
        self.assertIn("[C:5, Churn:3, Hotspot:15.0]", result)

    def test_format_file_stats_single_owner(self):
        """Test formatting when file has single owner."""
        file_obj = MagicMock(spec=File)

        complexity_kpi = MagicMock()
        complexity_kpi.value = 3

        shared_ownership_kpi = MagicMock()
        shared_ownership_kpi.value = {
            'num_significant_authors': 1,
            'authors': ['Carol'],
            'threshold': 20.0
        }

        file_obj.kpis = {
            'complexity': complexity_kpi,
            'churn': None,
            'hotspot': None,
            'Shared Ownership': shared_ownership_kpi
        }

        result = self.format_strategy._format_file_stats(file_obj)

        self.assertIn("Shared: Single owner (Carol)", result)

    def test_format_file_stats_no_shared_ownership(self):
        """Test formatting when shared ownership is N/A."""
        file_obj = MagicMock(spec=File)

        complexity_kpi = MagicMock()
        complexity_kpi.value = 2

        shared_ownership_kpi = MagicMock()
        shared_ownership_kpi.value = {'shared_ownership': 'N/A'}

        file_obj.kpis = {
            'complexity': complexity_kpi,
            'Shared Ownership': shared_ownership_kpi
        }

        result = self.format_strategy._format_file_stats(file_obj)

        self.assertIn("Shared: N/A", result)


if __name__ == '__main__':
    unittest.main()
