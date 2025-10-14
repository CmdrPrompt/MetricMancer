"""
Test suite that demonstrates the current code churn implementation problem.

These tests are designed to FAIL with the current implementation (which counts total commits)
and PASS when the implementation is fixed to count commits per time period.

The tests validate the expected behavior according to "Your Code as a Crime Scene" methodology.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.kpis.codechurn.kpi import ChurnKPI
from src.kpis.codechurn.kpi import ChurnKPI


class TestCodeChurnTimeBased(unittest.TestCase):
    """
    Tests that demonstrate the churn implementation should be time-based,
    not total historical commits.
    """

    def setUp(self):
        self.repo_scan_pairs = [("/fake/repo", "/fake/repo/src")]
        
    @patch('src.kpis.codechurn.code_churn.Repository')
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root')
    @patch('os.path.isdir')
    def test_churn_should_be_commits_per_month_not_total(self, mock_isdir, mock_find_git, mock_repository):
        """
        EXPECTED TO FAIL with current implementation.
        
        This test demonstrates that churn should be calculated as commits per time period,
        not total commits throughout history.
        
        Scenario: A file has 12 commits over 6 months = 2 commits/month
        Current implementation will return 12 (total)
        Expected implementation should return 2.0 (commits/month)
        """
        # Setup
        mock_find_git.return_value = "/fake/repo"
        mock_isdir.return_value = True
        
        # Create mock commits spanning 6 months
        base_date = datetime(2024, 1, 1)
        mock_commits = []
        
        for i in range(12):  # 12 commits over 6 months
            mock_commit = MagicMock()
            mock_commit.hash = f"abc{i:03d}"
            mock_commit.author_date = base_date + timedelta(days=i*15)  # Every 15 days
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/main.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = mock_commits
        mock_repository.return_value = mock_repo_instance
        
        # Test with 6 month period
        analyzer = CodeChurnAnalyzer(self.repo_scan_pairs, time_period_months=6)
        churn_data = analyzer.analyze()
        
        expected_file_path = "/fake/repo/src/main.py"
        
        # Current implementation will return 12 (total commits)
        # Expected implementation should return 2.0 (12 commits / 6 months)
        self.assertIn(expected_file_path, churn_data)
        
        # This assertion will FAIL with current implementation
        # because current implementation returns total commits (12)
        # but should return commits per month (2.0)
        self.assertEqual(churn_data[expected_file_path], 2.0,
                        "Churn should be commits per month (12 commits / 6 months = 2.0), "
                        "not total commits (12)")

    @patch('src.kpis.codechurn.code_churn.Repository')
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root')
    @patch('os.path.isdir')
    def test_churn_should_filter_by_time_period(self, mock_isdir, mock_find_git, mock_repository):
        """
        EXPECTED TO FAIL with current implementation.
        
        Tests that only commits within the specified time period are counted.
        
        Scenario: File has 20 total commits, but only 6 in last 3 months
        Expected: 2.0 commits/month (6 commits / 3 months)
        Current: Will count all 20 commits
        """
        # Setup
        mock_find_git.return_value = "/fake/repo"
        mock_isdir.return_value = True
        
        now = datetime.now()
        three_months_ago = now - timedelta(days=90)
        
        mock_commits = []
        
        # Add 14 old commits (before 3 months ago) - should be ignored
        for i in range(14):
            mock_commit = MagicMock()
            mock_commit.hash = f"old{i:03d}"
            mock_commit.author_date = now - timedelta(days=120 + i)  # More than 3 months ago
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/utils.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        # Add 6 recent commits (within last 3 months) - should be counted
        for i in range(6):
            mock_commit = MagicMock()
            mock_commit.hash = f"new{i:03d}"
            mock_commit.author_date = now - timedelta(days=30 + i*10)  # Within last 3 months
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/utils.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = mock_commits
        mock_repository.return_value = mock_repo_instance
        
        # Test with 3 month period
        analyzer = CodeChurnAnalyzer(self.repo_scan_pairs, time_period_months=3)
        churn_data = analyzer.analyze()
        
        expected_file_path = "/fake/repo/src/utils.py"
        
        # This assertion will FAIL with current implementation
        # Current: counts all 20 commits
        # Expected: counts only 6 recent commits and divides by 3 months = 2.0
        self.assertIn(expected_file_path, churn_data)
        self.assertEqual(churn_data[expected_file_path], 2.0,
                        "Should only count commits within time period (6 commits / 3 months = 2.0), "
                        "not all historical commits (20)")

    def test_churn_kpi_should_have_correct_unit_and_description(self):
        """
        EXPECTED TO FAIL with current implementation.
        
        Tests that ChurnKPI has correct unit and description for time-based measurement.
        """
        kpi = ChurnKPI()
        
        # These assertions will FAIL with current implementation
        self.assertEqual(kpi.unit, "commits/month",
                        "ChurnKPI unit should be 'commits/month', not 'commits'")
        
        self.assertIn("per month", kpi.description.lower(),
                     "ChurnKPI description should mention time-based measurement")

    @patch('src.kpis.codechurn.code_churn.Repository')
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root')
    @patch('os.path.isdir')
    def test_different_time_periods_give_different_rates(self, mock_isdir, mock_find_git, mock_repository):
        """
        EXPECTED TO FAIL with current implementation.
        
        Tests that different time periods result in different commits/month rates
        for the same set of commits.
        
        Scenario: 12 commits in last 6 months
        - 6 month analysis: 12 commits / 6 months = 2.0 commits/month  
        - 3 month analysis: 12 commits / 3 months = 4.0 commits/month
        """
        # Setup
        mock_find_git.return_value = "/fake/repo"
        mock_isdir.return_value = True
        
        # Create 12 commits within last 3 months
        now = datetime.now()
        mock_commits = []
        
        for i in range(12):
            mock_commit = MagicMock()
            mock_commit.hash = f"commit{i:03d}"
            mock_commit.author_date = now - timedelta(days=7 * i)  # One per week for 12 weeks
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/feature.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = mock_commits
        mock_repository.return_value = mock_repo_instance
        
        # Test with 6 months
        analyzer_6m = CodeChurnAnalyzer(self.repo_scan_pairs, time_period_months=6)
        churn_data_6m = analyzer_6m.analyze()
        
        # Test with 3 months  
        analyzer_3m = CodeChurnAnalyzer(self.repo_scan_pairs, time_period_months=3)
        churn_data_3m = analyzer_3m.analyze()
        
        expected_file_path = "/fake/repo/src/feature.py"
        
        # These assertions will FAIL with current implementation
        # Current implementation returns same value (12) regardless of time period
        # Expected: 6 months = 2.0, 3 months = 4.0
        self.assertEqual(churn_data_6m[expected_file_path], 2.0,
                        "6 month analysis: 12 commits / 6 months = 2.0 commits/month")
        
        self.assertEqual(churn_data_3m[expected_file_path], 4.0,
                        "3 month analysis: 12 commits / 3 months = 4.0 commits/month")
        
        # The rates should be different
        self.assertNotEqual(churn_data_6m[expected_file_path], churn_data_3m[expected_file_path],
                           "Different time periods should yield different commits/month rates")

    @patch('src.kpis.codechurn.code_churn.Repository')
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root')
    @patch('os.path.isdir')
    def test_realistic_hotspot_values_after_churn_fix(self, mock_isdir, mock_find_git, mock_repository):
        """
        EXPECTED TO FAIL with current implementation.
        
        Tests that hotspot values become realistic when churn is time-based.
        
        This demonstrates the core problem: current churn values make hotspots unrealistically high.
        """
        # Setup
        mock_find_git.return_value = "/fake/repo"
        mock_isdir.return_value = True
        
        # Simulate a file with moderate recent activity: 6 commits in 3 months
        now = datetime.now()
        mock_commits = []
        
        for i in range(6):
            mock_commit = MagicMock()
            mock_commit.hash = f"recent{i:03d}"
            mock_commit.author_date = now - timedelta(days=15 * i)  # Every 2 weeks
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/complex_module.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = mock_commits
        mock_repository.return_value = mock_repo_instance
        
        # Calculate churn
        analyzer = CodeChurnAnalyzer(self.repo_scan_pairs, time_period_months=3)
        churn_data = analyzer.analyze()
        
        expected_file_path = "/fake/repo/src/complex_module.py"
        churn_per_month = churn_data[expected_file_path]
        
        # Expected churn: 6 commits / 3 months = 2.0 commits/month
        self.assertEqual(churn_per_month, 2.0)
        
        # Simulate typical complexity value
        complexity = 15
        
        # Calculate hotspot score
        hotspot_score = complexity * churn_per_month
        
        # This should be a reasonable hotspot score: 15 * 2.0 = 30
        # Current implementation would give: 15 * 6 = 90 (too high!)
        expected_hotspot = 30.0
        self.assertEqual(hotspot_score, expected_hotspot,
                        f"Hotspot should be reasonable: {complexity} complexity * {churn_per_month} churn/month = {expected_hotspot}")
        
        # Verify it falls in reasonable range for Crime Scene methodology
        self.assertLessEqual(hotspot_score, 75,
                           "Hotspot scores should be in reasonable range for Crime Scene analysis")


if __name__ == '__main__':
    unittest.main()