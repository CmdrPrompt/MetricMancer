"""
Tests for CLISummaryFormat - Executive Summary Dashboard formatter.
"""

import unittest
from unittest.mock import MagicMock
from io import StringIO
import sys

from src.report.cli.cli_summary_format import CLISummaryFormat
from src.kpis.model import RepoInfo, ScanDir, File
from src.kpis.base_kpi import BaseKPI


class TestCLISummaryFormat(unittest.TestCase):
    """Test suite for CLISummaryFormat class."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CLISummaryFormat()
        self.mock_debug_print = MagicMock()

    def _create_mock_file(self, name: str, file_path: str, complexity: int = 5,
                          churn: float = 3.0, hotspot: float = 15.0,
                          has_ownership: bool = True) -> File:
        """Helper to create a mock File object with KPIs."""
        file_obj = File(name=name, file_path=file_path)

        # Create mock KPIs using MagicMock (BaseKPI is abstract)
        complexity_kpi = MagicMock(spec=BaseKPI)
        complexity_kpi.value = complexity
        file_obj.kpis['complexity'] = complexity_kpi

        churn_kpi = MagicMock(spec=BaseKPI)
        churn_kpi.value = churn
        file_obj.kpis['churn'] = churn_kpi

        hotspot_kpi = MagicMock(spec=BaseKPI)
        hotspot_kpi.value = hotspot
        file_obj.kpis['hotspot'] = hotspot_kpi

        ownership_kpi = MagicMock(spec=BaseKPI)
        if has_ownership:
            ownership_kpi.value = {'author1': 80.0, 'author2': 20.0}
        else:
            ownership_kpi.value = None
        file_obj.kpis['Code Ownership'] = ownership_kpi

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 2, 'authors': ['author1', 'author2']}
        file_obj.kpis['Shared Code Ownership'] = shared_kpi

        return file_obj

    def _create_mock_repo(self, files: list) -> RepoInfo:
        """Helper to create a mock RepoInfo with files."""
        repo_info = RepoInfo(
            dir_name='test_repo',
            scan_dir_path='.',
            repo_root_path='.',
            repo_name='test_repo'
        )

        # Add files to repo
        for file_obj in files:
            repo_info.files[file_obj.name] = file_obj

        return repo_info


class TestCollectAllFiles(TestCLISummaryFormat):
    """Tests for _collect_all_files method."""

    def test_collect_files_with_ownership(self):
        """Test collecting files that have code ownership."""
        file1 = self._create_mock_file('file1.py', 'src/file1.py', has_ownership=True)
        file2 = self._create_mock_file('file2.py', 'src/file2.py', has_ownership=True)

        repo_info = self._create_mock_repo([file1, file2])

        files = self.formatter._collect_all_files(repo_info)

        self.assertEqual(len(files), 2)
        self.assertIn(file1, files)
        self.assertIn(file2, files)

    def test_collect_files_filters_untracked(self):
        """Test that untracked files (no ownership) are filtered out."""
        tracked = self._create_mock_file('tracked.py', 'src/tracked.py', has_ownership=True)
        untracked = self._create_mock_file('untracked.py', 'src/untracked.py', has_ownership=False)

        repo_info = self._create_mock_repo([tracked, untracked])

        files = self.formatter._collect_all_files(repo_info)

        self.assertEqual(len(files), 1)
        self.assertIn(tracked, files)
        self.assertNotIn(untracked, files)

    def test_collect_files_recursive(self):
        """Test collecting files from nested directories."""
        file1 = self._create_mock_file('file1.py', 'src/file1.py', has_ownership=True)

        # Create nested structure
        repo_info = RepoInfo(
            dir_name='test_repo',
            scan_dir_path='.',
            repo_root_path='.',
            repo_name='test_repo'
        )
        repo_info.files['file1.py'] = file1

        # Add subdirectory
        subdir = ScanDir(dir_name='subdir', scan_dir_path='src/subdir', repo_root_path='.', repo_name='test_repo')
        file2 = self._create_mock_file('file2.py', 'src/subdir/file2.py', has_ownership=True)
        subdir.files['file2.py'] = file2
        repo_info.scan_dirs['subdir'] = subdir

        files = self.formatter._collect_all_files(repo_info)

        self.assertEqual(len(files), 2)
        self.assertIn(file1, files)
        self.assertIn(file2, files)

    def test_collect_files_empty_repo(self):
        """Test collecting files from empty repository."""
        repo_info = self._create_mock_repo([])

        files = self.formatter._collect_all_files(repo_info)

        self.assertEqual(len(files), 0)


class TestCalculateStatistics(TestCLISummaryFormat):
    """Tests for _calculate_statistics method."""

    def test_calculate_stats_basic(self):
        """Test basic statistics calculation."""
        files = [
            self._create_mock_file('f1.py', 'src/f1.py', complexity=10, churn=5.0),
            self._create_mock_file('f2.py', 'src/f2.py', complexity=20, churn=10.0),
            self._create_mock_file('f3.py', 'src/f3.py', complexity=15, churn=7.5),
        ]

        stats = self.formatter._calculate_statistics(files)

        self.assertEqual(stats['total_files'], 3)
        self.assertEqual(stats['total_complexity'], 45)
        self.assertAlmostEqual(stats['avg_complexity'], 15.0)
        self.assertEqual(stats['min_complexity'], 10)
        self.assertEqual(stats['max_complexity'], 20)
        self.assertAlmostEqual(stats['avg_churn'], 7.5)
        self.assertAlmostEqual(stats['total_churn'], 22.5)

    def test_calculate_stats_empty(self):
        """Test statistics calculation with no files."""
        stats = self.formatter._calculate_statistics([])

        self.assertEqual(stats['total_files'], 0)
        self.assertEqual(stats['total_complexity'], 0)
        self.assertEqual(stats['avg_complexity'], 0.0)
        self.assertEqual(stats['min_complexity'], 0)
        self.assertEqual(stats['max_complexity'], 0)

    def test_calculate_stats_with_missing_kpis(self):
        """Test statistics calculation when some files lack KPIs."""
        file1 = self._create_mock_file('f1.py', 'src/f1.py', complexity=10, churn=5.0)

        # File with no complexity
        file2 = File(name='f2.py', file_path='src/f2.py')
        complexity_kpi = MagicMock(spec=BaseKPI)
        complexity_kpi.value = None
        file2.kpis['complexity'] = complexity_kpi

        churn_kpi = MagicMock(spec=BaseKPI)
        churn_kpi.value = 10.0
        file2.kpis['churn'] = churn_kpi

        ownership_kpi = MagicMock(spec=BaseKPI)
        ownership_kpi.value = {'author': 100.0}
        file2.kpis['Code Ownership'] = ownership_kpi

        stats = self.formatter._calculate_statistics([file1, file2])

        self.assertEqual(stats['total_files'], 2)
        self.assertEqual(stats['total_complexity'], 10)  # Only file1
        self.assertAlmostEqual(stats['avg_complexity'], 10.0)  # Only file1
        self.assertAlmostEqual(stats['total_churn'], 15.0)  # Both files


class TestCategorizeFiles(TestCLISummaryFormat):
    """Tests for _categorize_files method."""

    def test_categorize_critical_hotspot(self):
        """Test categorization of critical hotspots (C>15, Churn>10)."""
        critical = self._create_mock_file(
            'critical.py', 'src/critical.py',
            complexity=20, churn=15.0, hotspot=300.0
        )

        crit, emerg, high_c, high_ch = self.formatter._categorize_files([critical])

        self.assertEqual(len(crit), 1)
        self.assertEqual(crit[0][0], critical)
        self.assertEqual(len(emerg), 0)
        self.assertEqual(len(high_c), 0)
        self.assertEqual(len(high_ch), 0)

    def test_categorize_emerging_hotspot(self):
        """Test categorization of emerging hotspots (5<C<=15, Churn>10)."""
        emerging = self._create_mock_file(
            'emerging.py', 'src/emerging.py',
            complexity=10, churn=12.0, hotspot=120.0
        )

        crit, emerg, high_c, high_ch = self.formatter._categorize_files([emerging])

        self.assertEqual(len(crit), 0)
        self.assertEqual(len(emerg), 1)
        self.assertEqual(emerg[0][0], emerging)

    def test_categorize_high_complexity_only(self):
        """Test categorization of high complexity files (C>15, Churn<=10)."""
        high_complexity = self._create_mock_file(
            'complex.py', 'src/complex.py',
            complexity=20, churn=5.0, hotspot=100.0
        )

        crit, emerg, high_c, high_ch = self.formatter._categorize_files([high_complexity])

        self.assertEqual(len(crit), 0)
        self.assertEqual(len(emerg), 0)
        self.assertEqual(len(high_c), 1)
        self.assertEqual(high_c[0][0], high_complexity)

    def test_categorize_high_churn_only(self):
        """Test categorization of high churn files (C<5, Churn>10)."""
        high_churn = self._create_mock_file(
            'churny.py', 'src/churny.py',
            complexity=3, churn=15.0, hotspot=45.0
        )

        crit, emerg, high_c, high_ch = self.formatter._categorize_files([high_churn])

        self.assertEqual(len(crit), 0)
        self.assertEqual(len(emerg), 0)
        self.assertEqual(len(high_c), 0)
        self.assertEqual(len(high_ch), 1)
        self.assertEqual(high_ch[0][0], high_churn)

    def test_categorize_sorted_by_hotspot(self):
        """Test that files are sorted by hotspot score (descending)."""
        file1 = self._create_mock_file('f1.py', 'src/f1.py',
                                       complexity=20, churn=15.0, hotspot=100.0)
        file2 = self._create_mock_file('f2.py', 'src/f2.py',
                                       complexity=20, churn=15.0, hotspot=300.0)
        file3 = self._create_mock_file('f3.py', 'src/f3.py',
                                       complexity=20, churn=15.0, hotspot=200.0)

        crit, _, _, _ = self.formatter._categorize_files([file1, file2, file3])

        self.assertEqual(len(crit), 3)
        self.assertEqual(crit[0][0], file2)  # Highest hotspot first
        self.assertEqual(crit[1][0], file3)
        self.assertEqual(crit[2][0], file1)

    def test_categorize_mixed_files(self):
        """Test categorization with multiple file types."""
        critical = self._create_mock_file('c.py', 'c.py', 20, 15.0, 300.0)
        emerging = self._create_mock_file('e.py', 'e.py', 10, 12.0, 120.0)
        high_c = self._create_mock_file('hc.py', 'hc.py', 20, 5.0, 100.0)
        high_ch = self._create_mock_file('hch.py', 'hch.py', 3, 15.0, 45.0)  # Changed from 5 to 3
        normal = self._create_mock_file('n.py', 'n.py', 3, 5.0, 15.0)  # Changed from 5 to 3

        crit, emerg, h_c, h_ch = self.formatter._categorize_files(
            [critical, emerging, high_c, high_ch, normal]
        )

        self.assertEqual(len(crit), 1)
        self.assertEqual(len(emerg), 1)
        self.assertEqual(len(h_c), 1)
        self.assertEqual(len(h_ch), 1)


class TestPrintMethods(TestCLISummaryFormat):
    """Tests for print methods (output formatting)."""

    def _capture_print_output(self, method, *args):
        """Helper to capture print output from a method."""
        captured = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured
        try:
            method(*args)
        finally:
            sys.stdout = sys_stdout
        return captured.getvalue()

    def test_print_header(self):
        """Test header printing."""
        output = self._capture_print_output(self.formatter._print_header)

        self.assertIn('METRICMANCER ANALYSIS SUMMARY', output)
        self.assertIn('╔', output)
        self.assertIn('╚', output)

    def test_print_overview(self):
        """Test overview printing."""
        stats = {
            'total_files': 65,
            'total_complexity': 1085,
            'avg_complexity': 16.7
        }

        output = self._capture_print_output(self.formatter._print_overview, stats)

        self.assertIn('📊 OVERVIEW', output)
        self.assertIn('Files Analyzed:', output)
        self.assertIn('65', output)
        self.assertIn('1,085', output)
        self.assertIn('16.7', output)

    def test_print_critical_issues_with_files(self):
        """Test critical issues section with files."""
        file1 = self._create_mock_file('f1.py', 'src/app/analyzer.py', 90, 20.0, 1800.0)
        file2 = self._create_mock_file('f2.py', 'src/app/scanner.py', 70, 15.0, 1050.0)
        critical = [(file1, 90, 20.0, 1800.0), (file2, 70, 15.0, 1050.0)]

        output = self._capture_print_output(
            self.formatter._print_critical_issues, critical
        )

        self.assertIn('🔥 CRITICAL ISSUES', output)
        self.assertIn('2 files', output)
        self.assertIn('analyzer.py', output)
        self.assertIn('Hotspot: 1800', output)
        self.assertIn('C:90', output)
        self.assertIn('Churn:20', output)

    def test_print_critical_issues_no_files(self):
        """Test critical issues section with no critical files."""
        output = self._capture_print_output(
            self.formatter._print_critical_issues, []
        )

        self.assertIn('🔥 CRITICAL ISSUES', output)
        self.assertIn('0 files', output)
        self.assertIn('✅ No critical hotspots detected', output)

    def test_print_high_priority(self):
        """Test high priority section."""
        output = self._capture_print_output(
            self.formatter._print_high_priority, [1, 2], [3, 4, 5], [6]
        )

        self.assertIn('⚠️  HIGH PRIORITY', output)
        self.assertIn('Emerging Hotspots:     2 files', output)
        self.assertIn('High Complexity (>15): 3 files', output)
        self.assertIn('High Churn (>10):      1 files', output)

    def test_print_health_metrics_good(self):
        """Test health metrics with good quality code."""
        stats = {'avg_complexity': 8.5}

        output = self._capture_print_output(
            self.formatter._print_health_metrics, stats
        )

        self.assertIn('📈 HEALTH METRICS', output)
        self.assertIn('Code Quality:', output)
        self.assertIn('A', output)
        self.assertIn('90', output)
        self.assertIn('Tech Debt Score:', output)
        self.assertIn('Low', output)

    def test_print_health_metrics_poor(self):
        """Test health metrics with poor quality code."""
        stats = {'avg_complexity': 25.0}

        output = self._capture_print_output(
            self.formatter._print_health_metrics, stats
        )

        self.assertIn('D', output)
        self.assertIn('40', output)
        self.assertIn('High', output)

    def test_print_recommendations_with_issues(self):
        """Test recommendations when there are issues."""
        critical = [(self._create_mock_file('f1.py', 'src/f1.py', 90, 20, 1800), 90, 20, 1800)]
        emerging = [(self._create_mock_file('f2.py', 'src/f2.py', 10, 15, 150), 10, 15, 150)]

        # Create files with fragmented ownership
        fragmented = self._create_mock_file('f3.py', 'src/f3.py', 5, 5, 25)
        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 5, 'authors': ['a', 'b', 'c', 'd', 'e']}
        fragmented.kpis['Shared Code Ownership'] = shared_kpi
        all_files = [critical[0][0], emerging[0][0], fragmented]

        output = self._capture_print_output(
            self.formatter._print_recommendations,
            critical, emerging, [], all_files
        )

        self.assertIn('💡 RECOMMENDATIONS', output)
        self.assertIn('Refactor', output)
        self.assertIn('f1.py', output)
        self.assertIn('Investigate high churn', output)
        self.assertIn('Add tests', output)
        self.assertIn('code ownership', output)

    def test_print_recommendations_no_issues(self):
        """Test recommendations when code is in good shape."""
        output = self._capture_print_output(
            self.formatter._print_recommendations, [], [], [], []
        )

        self.assertIn('💡 RECOMMENDATIONS', output)
        self.assertIn('✅ No critical issues detected', output)
        self.assertIn('good shape', output)

    def test_print_detailed_reports(self):
        """Test detailed reports section."""
        repo_info = self._create_mock_repo([])

        output = self._capture_print_output(
            self.formatter._print_detailed_reports, repo_info
        )

        self.assertIn('📁 DETAILED REPORTS', output)
        self.assertIn('--list-hotspots', output)
        self.assertIn('--review-strategy', output)
        self.assertIn('--output-format human-tree', output)

    def test_print_footer(self):
        """Test footer printing - now empty as timing is shown in global TIME SUMMARY."""
        output = self._capture_print_output(self.formatter._print_footer, 1.234)

        # Footer is now empty - timing shown in global TIME SUMMARY instead
        self.assertEqual(output.strip(), "")


class TestGetFilePath(TestCLISummaryFormat):
    """Tests for _get_file_path method."""

    def test_get_file_path_with_path_attribute(self):
        """Test getting file path when file_path attribute exists."""
        file_obj = self._create_mock_file('test.py', 'src/app/test.py')

        path = self.formatter._get_file_path(file_obj)

        self.assertEqual(path, 'src/app/test.py')

    def test_get_file_path_fallback_to_name(self):
        """Test fallback to name when file_path is missing."""
        file_obj = File(name='test.py', file_path='')

        path = self.formatter._get_file_path(file_obj)

        self.assertEqual(path, 'test.py')


class TestPrintReportIntegration(TestCLISummaryFormat):
    """Integration tests for full print_report method."""

    def test_print_report_full_workflow(self):
        """Test complete report generation workflow."""
        # Create test files
        critical = self._create_mock_file('critical.py', 'src/critical.py', 90, 20, 1800)
        normal = self._create_mock_file('normal.py', 'src/normal.py', 5, 3, 15)

        repo_info = self._create_mock_repo([critical, normal])

        # Capture output
        captured = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured
        try:
            self.formatter.print_report(repo_info, self.mock_debug_print, level='file')
        finally:
            sys.stdout = sys_stdout

        output = captured.getvalue()

        # Verify all sections are present
        self.assertIn('METRICMANCER ANALYSIS SUMMARY', output)
        self.assertIn('📊 OVERVIEW', output)
        self.assertIn('🔥 CRITICAL ISSUES', output)
        self.assertIn('⚠️  HIGH PRIORITY', output)
        self.assertIn('📈 HEALTH METRICS', output)
        self.assertIn('💡 RECOMMENDATIONS', output)
        self.assertIn('📁 DETAILED REPORTS', output)
        # Note: Timing info is now shown in global TIME SUMMARY, not in report footer

    def test_print_report_empty_repo(self):
        """Test report generation with empty repository."""
        repo_info = self._create_mock_repo([])

        captured = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured
        try:
            self.formatter.print_report(repo_info, self.mock_debug_print, level='file')
        finally:
            sys.stdout = sys_stdout

        output = captured.getvalue()

        # Should still print all sections
        self.assertIn('METRICMANCER ANALYSIS SUMMARY', output)
        self.assertIn('Files Analyzed:        0', output)
        self.assertIn('✅ No critical issues detected', output)


if __name__ == '__main__':
    unittest.main()
