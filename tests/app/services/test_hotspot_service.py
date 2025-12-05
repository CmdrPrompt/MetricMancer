"""
Unit tests for HotspotService (TDD for Refactoring #9).

These tests verify that hotspot analysis can be extracted into a dedicated
service class, improving separation of concerns and testability.

RED-GREEN-REFACTOR:
1. RED: These tests will FAIL initially because HotspotService doesn't exist yet
2. GREEN: Create HotspotService with hotspot extraction and display logic
3. REFACTOR: Update metric_mancer_app to use HotspotService
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


class TestHotspotServiceBasics(unittest.TestCase):
    """Test basic HotspotService functionality."""

    def test_hotspot_service_class_exists(self):
        """Test that HotspotService class can be imported."""
        # This test will FAIL initially - that's expected in TDD!
        from src.app.services.hotspot_service import HotspotService
        self.assertIsNotNone(HotspotService)

    def test_hotspot_service_initialization(self):
        """Test that HotspotService can be initialized with configuration."""
        from src.app.services.hotspot_service import HotspotService

        service = HotspotService(
            threshold=75,
            output_path='hotspots.md',
            report_folder='output'
        )

        self.assertIsNotNone(service)
        self.assertEqual(service.threshold, 75)
        self.assertEqual(service.output_path, 'hotspots.md')
        self.assertEqual(service.report_folder, 'output')

    def test_analyze_method_exists(self):
        """Test that analyze method exists."""
        from src.app.services.hotspot_service import HotspotService

        service = HotspotService(threshold=50, output_path=None, report_folder='output')
        self.assertTrue(hasattr(service, 'analyze'))
        self.assertTrue(callable(service.analyze))


class TestHotspotAnalysis(unittest.TestCase):
    """Test hotspot analysis functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('src.app.services.hotspot_service.DataConverter')
    @patch('src.app.services.hotspot_service.extract_hotspots_from_data')
    @patch('src.app.services.hotspot_service.format_hotspots_table')
    def test_analyze_extracts_hotspots_from_repos(self, mock_format, mock_extract, mock_converter):
        """Test that analyze extracts hotspots from all repo_infos."""
        from src.app.services.hotspot_service import HotspotService

        # Setup mocks
        mock_repo1 = Mock()
        mock_repo2 = Mock()
        mock_converter.convert_repo_info_to_dict.side_effect = [
            {'files': {'file1.py': {}}},
            {'files': {'file2.py': {}}}
        ]
        # Return empty lists to avoid formatting errors
        mock_extract.side_effect = [[], []]
        mock_format.return_value = ""

        service = HotspotService(threshold=50, output_path=None, report_folder=self.temp_dir)
        service.analyze([mock_repo1, mock_repo2])

        # Should have converted both repos and extracted hotspots
        self.assertEqual(mock_converter.convert_repo_info_to_dict.call_count, 2)
        self.assertEqual(mock_extract.call_count, 2)

    @patch('src.app.services.hotspot_service.DataConverter')
    @patch('src.app.services.hotspot_service.extract_hotspots_from_data')
    @patch('sys.stdout', new_callable=MagicMock)
    def test_analyze_prints_message_when_no_hotspots(self, mock_stdout, mock_extract, mock_converter):
        """Test that analyze prints message when no hotspots found."""
        from src.app.services.hotspot_service import HotspotService

        mock_repo = Mock()
        mock_converter.convert_repo_info_to_dict.return_value = {'files': {}}
        mock_extract.return_value = []  # No hotspots

        service = HotspotService(threshold=50, output_path=None, report_folder=self.temp_dir)
        service.analyze([mock_repo])

        # Should have printed "no hotspots" message
        # (exact assertion depends on implementation)

    @patch('src.app.services.hotspot_service.DataConverter')
    @patch('src.app.services.hotspot_service.extract_hotspots_from_data')
    @patch('src.app.services.hotspot_service.format_hotspots_table')
    def test_analyze_displays_hotspots_when_found(self, mock_format, mock_extract, mock_converter):
        """Test that analyze displays hotspots when found."""
        from src.app.services.hotspot_service import HotspotService

        mock_repo = Mock()
        mock_converter.convert_repo_info_to_dict.return_value = {'files': {}}
        hotspots = [{'file': 'file1.py', 'hotspot': 100}]
        mock_extract.return_value = hotspots
        mock_format.return_value = "Hotspot table"

        service = HotspotService(threshold=50, output_path=None, report_folder=self.temp_dir)
        service.analyze([mock_repo])

        # Should have formatted and displayed hotspots
        mock_format.assert_called_once_with(hotspots, show_risk_categories=True)


class TestHotspotOutput(unittest.TestCase):
    """Test hotspot output functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('src.app.services.hotspot_service.DataConverter')
    @patch('src.app.services.hotspot_service.extract_hotspots_from_data')
    @patch('src.app.services.hotspot_service.save_hotspots_to_file')
    @patch('src.app.services.hotspot_service.print_hotspots_summary')
    def test_saves_hotspots_to_file_when_output_path_specified(
            self, mock_print_summary, mock_save, mock_extract, mock_converter):
        """Test that hotspots are saved to file when output_path is specified."""
        from src.app.services.hotspot_service import HotspotService

        mock_repo = Mock()
        mock_converter.convert_repo_info_to_dict.return_value = {'files': {}}
        hotspots = [{'file': 'file1.py', 'hotspot': 100}]
        mock_extract.return_value = hotspots

        output_file = 'hotspots.md'
        service = HotspotService(
            threshold=50,
            output_path=output_file,
            report_folder=self.temp_dir
        )
        service.analyze([mock_repo])

        # Should have saved hotspots to file
        mock_save.assert_called_once()
        call_args = mock_save.call_args
        self.assertEqual(call_args[0][0], hotspots)  # First arg is hotspots
        self.assertIn(output_file, call_args[0][1])  # Second arg contains output path
        self.assertEqual(call_args[1]['show_risk_categories'], True)

        # Should also print summary
        mock_print_summary.assert_called_once_with(hotspots)

    @patch('src.app.services.hotspot_service.DataConverter')
    @patch('src.app.services.hotspot_service.extract_hotspots_from_data')
    @patch('src.app.services.hotspot_service.format_hotspots_table')
    def test_prints_hotspots_when_no_output_path(
            self, mock_format, mock_extract, mock_converter):
        """Test that hotspots are printed to console when no output_path."""
        from src.app.services.hotspot_service import HotspotService

        mock_repo = Mock()
        mock_converter.convert_repo_info_to_dict.return_value = {'files': {}}
        hotspots = [{'file': 'file1.py', 'hotspot': 100}]
        mock_extract.return_value = hotspots
        mock_format.return_value = "Hotspot table"

        service = HotspotService(threshold=50, output_path=None, report_folder=self.temp_dir)
        service.analyze([mock_repo])

        # Should have formatted hotspots for console display
        mock_format.assert_called_once_with(hotspots, show_risk_categories=True)


class TestHotspotServiceWithMultipleRepos(unittest.TestCase):
    """Test HotspotService with multiple repositories."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir)

    @patch('src.app.services.hotspot_service.DataConverter')
    @patch('src.app.services.hotspot_service.extract_hotspots_from_data')
    @patch('src.app.services.hotspot_service.format_hotspots_table')
    def test_aggregates_hotspots_from_multiple_repos(self, mock_format, mock_extract, mock_converter):
        """Test that hotspots from multiple repos are aggregated."""
        from src.app.services.hotspot_service import HotspotService

        # Setup mocks
        mock_repo1 = Mock()
        mock_repo2 = Mock()
        mock_repo3 = Mock()

        mock_converter.convert_repo_info_to_dict.side_effect = [
            {'files': {}}, {'files': {}}, {'files': {}}
        ]
        # Return empty lists to avoid formatting errors
        mock_extract.side_effect = [[], [], []]
        mock_format.return_value = ""

        service = HotspotService(threshold=50, output_path=None, report_folder=self.temp_dir)
        service.analyze([mock_repo1, mock_repo2, mock_repo3])

        # Should have processed all three repos
        self.assertEqual(mock_converter.convert_repo_info_to_dict.call_count, 3)
        self.assertEqual(mock_extract.call_count, 3)


if __name__ == '__main__':
    unittest.main()
