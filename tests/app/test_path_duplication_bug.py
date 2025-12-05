"""
Test for path duplication bug fix.

This test verifies that when --review-output or --report-filename contains a path,
it doesn't get duplicated when joined with report_folder.

Bug: output/output/review_strategy.md (should be output/review_strategy.md)
"""

import os
import tempfile
import shutil
import unittest
from unittest.mock import patch, MagicMock
import warnings


class TestPathDuplicationBug(unittest.TestCase):
    """Tests for path duplication bug in review-output and report-filename."""

    def setUp(self):
        """Create a temporary directory for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.test_src_dir = os.path.join(self.test_dir, 'test_src')
        os.makedirs(self.test_src_dir)

        # Create a dummy Python file
        test_file = os.path.join(self.test_src_dir, 'dummy.py')
        with open(test_file, 'w') as f:
            f.write('def test(): pass\n')

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    @patch('src.utilities.git_helpers.get_current_branch')
    @patch('src.analysis.code_review_advisor.generate_review_report')
    def test_review_output_with_folder_path_no_duplication(self, mock_generate, mock_get_branch):
        """
        🔴 RED TEST: Verify that review_output with path doesn't duplicate report_folder.

        When review_output='output/review_strategy.md' and report_folder='output',
        the final path should be 'output/review_strategy.md', NOT 'output/output/review_strategy.md'.
        """
        from src.app.metric_mancer_app import MetricMancerApp
        from src.config.app_config import AppConfig

        mock_get_branch.return_value = None

        # Test case: review_output already contains 'output/' prefix
        config = AppConfig(
            directories=[self.test_src_dir],
            report_folder='output',
            review_strategy=True,
            review_output='output/review_strategy.md'  # Contains path prefix
        )

        app = MetricMancerApp(config=config)

        # Create mock repo_info
        mock_repo_info = MagicMock()
        mock_repo_info.file_stats = {}
        mock_repo_info.directory_stats = {}

        with patch('src.app.metric_mancer_app.DataConverter.convert_repo_info_to_dict_with_ownership') as mock_convert:
            mock_convert.return_value = {
                'files': {},
                'scan_dirs': {}
            }

            # Run the method
            app._run_review_strategy_analysis([mock_repo_info])

        # Verify generate_review_report was called
        self.assertTrue(mock_generate.called)

        # Get the output_file argument
        call_args = mock_generate.call_args
        output_file = call_args[1]['output_file']  # keyword argument

        # Assert: Should NOT have duplicated 'output/'
        self.assertNotIn('output/output/', output_file,
                         f"Path should not have duplicated 'output/': {output_file}")

        # Assert: Should end with the expected path
        self.assertTrue(output_file.endswith('output/review_strategy.md'),
                        f"Path should end with 'output/review_strategy.md', got: {output_file}")

    @patch('src.utilities.git_helpers.get_current_branch')
    @patch('src.analysis.code_review_advisor.generate_review_report')
    def test_review_output_without_folder_path_works(self, mock_generate, mock_get_branch):
        """
        Verify that review_output without path prefix works correctly.

        When review_output='review_strategy.md' (just filename) and report_folder='output',
        the final path should be 'output/review_strategy.md'.
        """
        from src.app.metric_mancer_app import MetricMancerApp
        from src.config.app_config import AppConfig

        mock_get_branch.return_value = None

        # Test case: review_output is just a filename
        config = AppConfig(
            directories=[self.test_src_dir],
            report_folder='output',
            review_strategy=True,
            review_output='review_strategy.md'  # Just filename, no path
        )

        app = MetricMancerApp(config=config)

        # Create mock repo_info
        mock_repo_info = MagicMock()
        mock_repo_info.file_stats = {}
        mock_repo_info.directory_stats = {}

        with patch('src.app.metric_mancer_app.DataConverter.convert_repo_info_to_dict_with_ownership') as mock_convert:
            mock_convert.return_value = {
                'files': {},
                'scan_dirs': {}
            }

            # Run the method
            app._run_review_strategy_analysis([mock_repo_info])

        # Verify generate_review_report was called
        self.assertTrue(mock_generate.called)

        # Get the output_file argument
        call_args = mock_generate.call_args
        output_file = call_args[1]['output_file']

        # Assert: Should have correct path
        self.assertTrue(output_file.endswith('output/review_strategy.md'),
                        f"Path should end with 'output/review_strategy.md', got: {output_file}")

        # Assert: Should NOT have duplicated 'output/'
        self.assertNotIn('output/output/', output_file,
                         f"Path should not have duplicated 'output/': {output_file}")

    def test_report_filename_path_handling(self):
        """
        🔴 RED TEST: Verify that report_filename with path doesn't duplicate report_folder.

        Similar to review_output, when report_filename contains a path prefix,
        it should not be duplicated.
        """
        from src.report.report_helpers import get_output_filename
        from argparse import Namespace

        # Test case 1: report_filename with 'output/' prefix
        args = Namespace(
            report_filename='output/custom_report.json',
            output_format='json',
            with_date=False,
            auto_report_filename=False
        )

        filename = get_output_filename(args)

        # The function should return just the filename or handle paths correctly
        # We'll need to check how this is used in conjunction with report_folder
        self.assertEqual(filename, 'output/custom_report.json',
                         f"Expected 'output/custom_report.json', got: {filename}")

    def test_path_normalization_helper(self):
        """
        Test helper function for normalizing output paths.

        This test defines the expected behavior for a path normalization function
        that should prevent duplication.
        """
        # This is a specification test - defining what we want
        test_cases = [
            # (report_folder, filename, expected_output)
            ('output', 'review_strategy.md', 'output/review_strategy.md'),
            ('output', 'output/review_strategy.md', 'output/review_strategy.md'),
            ('output', './output/review_strategy.md', 'output/review_strategy.md'),
            ('custom_output', 'review.md', 'custom_output/review.md'),
            ('custom_output', 'custom_output/review.md', 'custom_output/review.md'),
            ('', 'review.md', 'review.md'),
            ('output', 'subfolder/review.md', 'output/subfolder/review.md'),
        ]

        for report_folder, filename, expected in test_cases:
            with self.subTest(report_folder=report_folder, filename=filename):
                # This function doesn't exist yet - we'll create it in GREEN phase
                from src.utilities.path_helpers import normalize_output_path
                result = normalize_output_path(report_folder, filename)
                self.assertEqual(result, expected,
                                 f"normalize_output_path('{report_folder}', '{filename}') "
                                 f"should return '{expected}', got '{result}'")


if __name__ == '__main__':
    unittest.main()
