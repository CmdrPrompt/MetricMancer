"""
Integration tests that demonstrate the churn problem at system level.

These tests show how the current churn implementation affects the entire analysis pipeline,
including hotspot calculations and KPI aggregation.

EXPECTED TO FAIL with current implementation.
"""

import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from src.app.analyzer import Analyzer
from src.languages.config import Config as LanguagesConfig


class TestChurnIntegrationProblem(unittest.TestCase):
    """
    Integration tests showing how churn problem affects the entire system.
    """

    def setUp(self):
        self.languages_config = LanguagesConfig()
        self.repo_scan_pairs = [("/fake/repo", "/fake/repo/src")]

    @patch('src.kpis.codechurn.code_churn.Repository')
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root')
    @patch('src.kpis.complexity.analyzer.ComplexityAnalyzer.calculate_for_file')
    @patch('src.kpis.codeownership.code_ownership.CodeOwnershipKPI.calculate')
    @patch('os.path.isdir')
    @patch('os.path.exists')
    @patch('builtins.open')
    def test_analyzer_should_produce_realistic_hotspot_values(self, mock_open, mock_exists, mock_isdir, 
                                                            mock_ownership_calc, mock_complexity_calc, 
                                                            mock_find_git, mock_repository):
        """
        EXPECTED TO FAIL with current implementation.
        
        Integration test showing that the analyzer should produce realistic hotspot values
        when churn is properly calculated as time-based.
        """
        # Setup mocks
        mock_find_git.return_value = "/fake/repo"
        mock_isdir.return_value = True
        mock_exists.return_value = True
        
        # Mock file content
        mock_file_content = """
def complex_function():
    if condition1:
        if condition2:
            if condition3:
                for i in range(10):
                    if condition4:
                        return calculate_something()
    return default_value()
"""
        mock_open.return_value.__enter__.return_value.read.return_value = mock_file_content
        
        # Mock complexity calculation - moderately complex function
        mock_complexity_calc.return_value = 15
        
        # Mock ownership calculation
        mock_ownership_calc.return_value.value = 0.8  # 80% ownership
        
        # Mock churn data - simulate moderate recent activity
        now = datetime.now()
        mock_commits = []
        
        # 9 commits over 3 months = 3 commits/month (moderate churn)
        for i in range(9):
            mock_commit = MagicMock()
            mock_commit.hash = f"commit{i:03d}"
            mock_commit.author_date = now - timedelta(days=10 * i)  # Every 10 days
            mock_commit.author.name = "Developer"
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/main.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = mock_commits
        mock_repository.return_value = mock_repo_instance
        
        # Create analyzer with 3-month churn period
        analyzer = Analyzer(self.languages_config, churn_time_period_months=3)
        
        # Analyze the repository
        repo_infos = analyzer.analyze(self.repo_scan_pairs)
        
        # Get the analyzed file
        repo_info = repo_infos["/fake/repo"]
        main_file = None
        
        def find_file_recursive(scan_dir, filename):
            """Helper to find file in nested structure"""
            if hasattr(scan_dir, 'files'):
                for file in scan_dir.files:
                    if file.path.endswith(filename):
                        return file
            if hasattr(scan_dir, 'subdirs'):
                for subdir in scan_dir.subdirs:
                    result = find_file_recursive(subdir, filename)
                    if result:
                        return result
            return None
        
        main_file = find_file_recursive(repo_info, "main.py")
        self.assertIsNotNone(main_file, "Should find main.py in analysis results")
        
        # Check churn KPI
        churn_kpi = main_file.kpis.get('churn')
        self.assertIsNotNone(churn_kpi, "File should have churn KPI")
        
        # Expected: 9 commits / 3 months = 3.0 commits/month
        # Current implementation will return 9 (total commits)
        expected_churn_per_month = 3.0
        self.assertEqual(churn_kpi.value, expected_churn_per_month,
                        f"Churn should be {expected_churn_per_month} commits/month, not total commits")
        
        # Check unit
        self.assertEqual(churn_kpi.unit, "commits/month",
                        "Churn KPI should have unit 'commits/month'")
        
        # Check hotspot KPI  
        hotspot_kpi = main_file.kpis.get('hotspot')
        self.assertIsNotNone(hotspot_kpi, "File should have hotspot KPI")
        
        # Expected hotspot: 15 complexity * 3.0 churn/month = 45
        # Current implementation: 15 complexity * 9 total commits = 135 (too high!)
        expected_hotspot = 45.0
        self.assertEqual(hotspot_kpi.value, expected_hotspot,
                        f"Hotspot should be {expected_hotspot} (15 complexity * 3.0 churn/month), "
                        f"not {15 * 9} (complexity * total commits)")
        
        # Verify hotspot is in reasonable range for Crime Scene methodology
        self.assertLessEqual(hotspot_kpi.value, 75,
                           "Hotspot should be in reasonable range for analysis")

    @patch('src.kpis.codechurn.code_churn.Repository')
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root')
    @patch('os.path.isdir')
    def test_churn_kpi_calculation_values_should_include_time_period(self, mock_isdir, mock_find_git, mock_repository):
        """
        EXPECTED TO FAIL with current implementation.
        
        Tests that ChurnKPI.calculation_values includes time period information
        for transparency and debugging.
        """
        # Setup
        mock_find_git.return_value = "/fake/repo"
        mock_isdir.return_value = True
        
        mock_commits = []
        for i in range(6):
            mock_commit = MagicMock()
            mock_commit.hash = f"commit{i:03d}"
            mock_commit.author_date = datetime.now() - timedelta(days=i*10)
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/test.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = mock_commits
        mock_repository.return_value = mock_repo_instance
        
        # Test ChurnKPI calculation
        from src.kpis.codechurn.code_churn import CodeChurnAnalyzer
        from src.kpis.codechurn.kpi import ChurnKPI
        
        analyzer = CodeChurnAnalyzer(self.repo_scan_pairs, time_period_months=6)
        churn_data = analyzer.analyze()
        
        churn_kpi = ChurnKPI()
        churn_kpi.calculate("/fake/repo/src/test.py", churn_data, time_period_months=6)
        
        # Should include time period in calculation values
        self.assertIsNotNone(churn_kpi.calculation_values,
                           "ChurnKPI should have calculation_values")
        
        self.assertIn("time_period_months", churn_kpi.calculation_values,
                     "calculation_values should include time_period_months for transparency")
        
        self.assertEqual(churn_kpi.calculation_values["time_period_months"], 6,
                        "Should record the time period used for calculation")

    def test_different_time_periods_should_be_configurable(self):
        """
        EXPECTED TO FAIL with current implementation.
        
        Tests that different time periods can be configured and affect results.
        """
        # Test that Analyzer accepts churn_time_period_months parameter
        analyzer_3m = Analyzer(self.languages_config, churn_time_period_months=3)
        analyzer_6m = Analyzer(self.languages_config, churn_time_period_months=6)
        analyzer_12m = Analyzer(self.languages_config, churn_time_period_months=12)
        
        # This will FAIL if Analyzer doesn't accept the parameter
        self.assertEqual(analyzer_3m.churn_time_period_months, 3)
        self.assertEqual(analyzer_6m.churn_time_period_months, 6)
        self.assertEqual(analyzer_12m.churn_time_period_months, 12)

    @patch('src.kpis.codechurn.code_churn.Repository')
    @patch('src.kpis.codechurn.code_churn.find_git_repo_root')
    @patch('os.path.isdir')
    def test_empty_time_period_should_return_zero_churn(self, mock_isdir, mock_find_git, mock_repository):
        """
        Tests that files with no commits in the time period get zero churn.
        
        This test should PASS even with current implementation, but validates
        the expected behavior for edge cases.
        """
        # Setup
        mock_find_git.return_value = "/fake/repo"
        mock_isdir.return_value = True
        
        # Mock commits that are all older than the time period
        old_date = datetime.now() - timedelta(days=400)  # More than 1 year ago
        mock_commits = []
        
        for i in range(5):
            mock_commit = MagicMock()
            mock_commit.hash = f"old{i:03d}"
            mock_commit.author_date = old_date - timedelta(days=i*10)
            
            mock_modification = MagicMock()
            mock_modification.new_path = "src/legacy.py"
            mock_commit.modifications = [mock_modification]
            mock_commits.append(mock_commit)
        
        mock_repo_instance = MagicMock()
        mock_repo_instance.traverse_commits.return_value = mock_commits
        mock_repository.return_value = mock_repo_instance
        
        # Test with 6 month period (commits are older than this)
        from src.kpis.codechurn.code_churn import CodeChurnAnalyzer
        
        analyzer = CodeChurnAnalyzer(self.repo_scan_pairs, time_period_months=6)
        churn_data = analyzer.analyze()
        
        # File should have zero churn since no commits in time period
        expected_file_path = "/fake/repo/src/legacy.py"
        
        # This test should reveal if time filtering is working
        # Current implementation will still count the old commits
        # Fixed implementation will return 0.0
        if expected_file_path in churn_data:
            self.assertEqual(churn_data[expected_file_path], 0.0,
                           "Files with no commits in time period should have zero churn")
        else:
            # If file not in results, that's also acceptable (no activity = no entry)
            pass


if __name__ == '__main__':
    unittest.main()