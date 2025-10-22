"""Tests for CLIQuickWinsFormat class."""
import io
import sys
import unittest
from unittest.mock import MagicMock, patch

from src.kpis.base_kpi import BaseKPI
from src.kpis.model import File, Function, ScanDir, RepoInfo
from src.report.cli.cli_quick_wins_format import CLIQuickWinsFormat


class TestCollectAllFiles(unittest.TestCase):
    """Test _collect_all_files method."""

    def test_collect_all_files_with_ownership(self):
        """Test collecting files with ownership data."""
        # Create mock files
        file1 = File(name="file1.py", file_path="src/file1.py")
        file1.functions = [Function(name="func1"), Function(name="func2")]

        # Add complexity KPI (required for quick wins)
        complexity_kpi = MagicMock(spec=BaseKPI)
        complexity_kpi.value = 10
        file1.kpis['complexity'] = complexity_kpi

        # Add ownership KPI to indicate tracked file
        ownership_kpi = MagicMock(spec=BaseKPI)
        ownership_kpi.value = {"Alice": 60, "Bob": 40}
        file1.kpis['Code Ownership'] = ownership_kpi

        file2 = File(name="file2.py", file_path="src/file2.py")
        file2.functions = [Function(name="func3")]

        # Add complexity KPI
        complexity_kpi2 = MagicMock(spec=BaseKPI)
        complexity_kpi2.value = 15
        file2.kpis['complexity'] = complexity_kpi2

        ownership_kpi2 = MagicMock(spec=BaseKPI)
        ownership_kpi2.value = {"Charlie": 100}
        file2.kpis['Code Ownership'] = ownership_kpi2

        # Create scan directory
        repo_info = RepoInfo(
            dir_name="test_repo",
            scan_dir_path=".",
            repo_root_path="/test",
            repo_name="test_repo"
        )
        repo_info.files = {"file1.py": file1, "file2.py": file2}

        # Test
        formatter = CLIQuickWinsFormat()
        all_files = formatter._collect_all_files(repo_info)

        self.assertEqual(len(all_files), 2)
        self.assertIn(file1, all_files)
        self.assertIn(file2, all_files)

    def test_collect_all_files_empty_repo(self):
        """Test collecting files from empty repository."""
        repo_info = RepoInfo(
            dir_name="empty_repo",
            scan_dir_path=".",
            repo_root_path="/test",
            repo_name="empty_repo"
        )

        formatter = CLIQuickWinsFormat()
        all_files = formatter._collect_all_files(repo_info)

        self.assertEqual(len(all_files), 0)

    def test_collect_all_files_multiple_subdirs(self):
        """Test collecting files from nested subdirectories."""
        file1 = File(name="file1.py", file_path="src/file1.py")

        # Add complexity KPI
        complexity_kpi1 = MagicMock(spec=BaseKPI)
        complexity_kpi1.value = 12
        file1.kpis['complexity'] = complexity_kpi1

        ownership_kpi1 = MagicMock(spec=BaseKPI)
        ownership_kpi1.value = {"Alice": 100}
        file1.kpis['Code Ownership'] = ownership_kpi1

        file2 = File(name="file2.py", file_path="tests/file2.py")

        # Add complexity KPI
        complexity_kpi2 = MagicMock(spec=BaseKPI)
        complexity_kpi2.value = 8
        file2.kpis['complexity'] = complexity_kpi2

        ownership_kpi2 = MagicMock(spec=BaseKPI)
        ownership_kpi2.value = {"Bob": 100}
        file2.kpis['Code Ownership'] = ownership_kpi2

        subdir = ScanDir(
            dir_name="tests",
            scan_dir_path="tests",
            repo_root_path="/test",
            repo_name="test_repo"
        )
        subdir.files = {"file2.py": file2}

        repo_info = RepoInfo(
            dir_name="test_repo",
            scan_dir_path=".",
            repo_root_path="/test",
            repo_name="test_repo"
        )
        repo_info.files = {"file1.py": file1}
        repo_info.scan_dirs = {"tests": subdir}

        formatter = CLIQuickWinsFormat()
        all_files = formatter._collect_all_files(repo_info)

        self.assertEqual(len(all_files), 2)


class TestCalculateImpact(unittest.TestCase):
    """Test _calculate_impact method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CLIQuickWinsFormat()

    def test_impact_high_hotspot(self):
        """Test impact with high hotspot score."""
        impact = self.formatter._calculate_impact(
            complexity=5,
            churn=2,
            hotspot=600
        )
        # hotspot=600 -> 5 points, complexity=5 -> 0 points, churn=2 -> 0 points
        self.assertEqual(impact, 5)

    def test_impact_high_complexity(self):
        """Test impact with high complexity."""
        impact = self.formatter._calculate_impact(
            complexity=60,
            churn=2,
            hotspot=10
        )
        # hotspot=10 -> 1 point, complexity=60 -> 2 points, churn=2 -> 0 points = 3
        self.assertEqual(impact, 3)

    def test_impact_high_churn(self):
        """Test impact with high churn."""
        impact = self.formatter._calculate_impact(
            complexity=5,
            churn=20,
            hotspot=10
        )
        # hotspot=10 -> 1 point, complexity=5 -> 0 points, churn=20 -> 2 points = 3
        self.assertEqual(impact, 3)

    def test_impact_combined_scores(self):
        """Test impact with combined high scores."""
        impact = self.formatter._calculate_impact(
            complexity=60,
            churn=20,
            hotspot=600
        )
        # hotspot=600 -> 5, complexity=60 -> 2, churn=20 -> 2 = 9
        self.assertEqual(impact, 9)

    def test_impact_low_scores(self):
        """Test impact with all low scores."""
        impact = self.formatter._calculate_impact(
            complexity=3,
            churn=2,
            hotspot=10
        )
        # hotspot=10 -> 1 point (>0), others contribute 0
        self.assertEqual(impact, 1)

    def test_impact_medium_hotspot(self):
        """Test impact with medium hotspot scores."""
        # Test boundaries: complexity=50 adds 2 points
        self.assertEqual(
            self.formatter._calculate_impact(50, 0, 51),
            3  # hotspot 51 -> 2 points, complexity 50 -> 1 point
        )
        self.assertEqual(
            self.formatter._calculate_impact(50, 0, 151),
            4  # hotspot 151 -> 3 points, complexity 50 -> 1 point
        )
        self.assertEqual(
            self.formatter._calculate_impact(50, 0, 301),
            5  # hotspot 301 -> 4 points, complexity 50 -> 1 point
        )

    def test_impact_medium_complexity(self):
        """Test impact with medium complexity scores."""
        self.assertEqual(
            self.formatter._calculate_impact(11, 0, 0),
            0  # complexity 11-20 -> 0 points
        )
        self.assertEqual(
            self.formatter._calculate_impact(25, 0, 0),
            1  # complexity 21-50 -> 1 point
        )


class TestCalculateEffort(unittest.TestCase):
    """Test _calculate_effort method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CLIQuickWinsFormat()

    def test_effort_high_complexity(self):
        """Test effort with high complexity."""
        file_obj = File(name="test.py", file_path="test.py")
        file_obj.functions = [Function(name=f"func{i}") for i in range(3)]

        effort = self.formatter._calculate_effort(complexity=150, file_obj=file_obj)
        # complexity=150 -> 5, functions=3 -> 0, owners=1 -> 0 = 5
        self.assertEqual(effort, 5)

    def test_effort_many_functions(self):
        """Test effort with many functions."""
        file_obj = File(name="test.py", file_path="test.py")
        file_obj.functions = [Function(name=f"func{i}") for i in range(25)]

        effort = self.formatter._calculate_effort(complexity=5, file_obj=file_obj)
        # complexity=5 -> 0, functions=25 -> 3, owners=1 -> 0 = 3
        self.assertEqual(effort, 3)

    def test_effort_fragmented_ownership(self):
        """Test effort with fragmented ownership."""
        file_obj = File(name="test.py", file_path="test.py")
        file_obj.functions = [Function(name="func1")]

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 6}
        file_obj.kpis['Shared Code Ownership'] = shared_kpi

        effort = self.formatter._calculate_effort(complexity=5, file_obj=file_obj)
        # complexity=5 -> 0, functions=1 -> 0, owners=6 -> 2 = 2
        self.assertEqual(effort, 2)

    def test_effort_combined_scores(self):
        """Test effort with combined high scores."""
        file_obj = File(name="test.py", file_path="test.py")
        file_obj.functions = [Function(name=f"func{i}") for i in range(25)]

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 6}
        file_obj.kpis['Shared Code Ownership'] = shared_kpi

        effort = self.formatter._calculate_effort(complexity=150, file_obj=file_obj)
        # complexity=150 -> 5, functions=25 -> 3, owners=6 -> 2 = 10
        self.assertEqual(effort, 10)

    def test_effort_low_scores(self):
        """Test effort with all low scores."""
        file_obj = File(name="test.py", file_path="test.py")
        file_obj.functions = [Function(name="func1")]

        effort = self.formatter._calculate_effort(complexity=3, file_obj=file_obj)
        self.assertEqual(effort, 0)

    def test_effort_medium_complexity(self):
        """Test effort with medium complexity scores."""
        file_obj = File(name="test.py", file_path="test.py")

        self.assertEqual(self.formatter._calculate_effort(6, file_obj), 1)
        self.assertEqual(self.formatter._calculate_effort(20, file_obj), 2)
        self.assertEqual(self.formatter._calculate_effort(40, file_obj), 3)


class TestCalculateQuickWins(unittest.TestCase):
    """Test _calculate_quick_wins method."""

    def test_calculate_quick_wins_sorting(self):
        """Test that quick wins are sorted by ROI."""
        # High ROI file: high impact, low effort
        file1 = File(name="high_roi.py", file_path="high_roi.py")
        file1.functions = [Function(name="func1")]

        complexity_kpi1 = MagicMock(spec=BaseKPI)
        complexity_kpi1.value = 5
        file1.kpis['complexity'] = complexity_kpi1

        churn_kpi1 = MagicMock(spec=BaseKPI)
        churn_kpi1.value = 15
        file1.kpis['churn'] = churn_kpi1

        hotspot_kpi1 = MagicMock(spec=BaseKPI)
        hotspot_kpi1.value = 200
        file1.kpis['hotspot'] = hotspot_kpi1

        ownership_kpi1 = MagicMock(spec=BaseKPI)
        ownership_kpi1.value = {"Alice": 100}
        file1.kpis['Code Ownership'] = ownership_kpi1

        # Low ROI file: high impact, high effort
        file2 = File(name="low_roi.py", file_path="low_roi.py")
        file2.functions = [Function(name=f"func{i}") for i in range(25)]

        complexity_kpi2 = MagicMock(spec=BaseKPI)
        complexity_kpi2.value = 150
        file2.kpis['complexity'] = complexity_kpi2

        churn_kpi2 = MagicMock(spec=BaseKPI)
        churn_kpi2.value = 15
        file2.kpis['churn'] = churn_kpi2

        hotspot_kpi2 = MagicMock(spec=BaseKPI)
        hotspot_kpi2.value = 200
        file2.kpis['hotspot'] = hotspot_kpi2

        ownership_kpi2 = MagicMock(spec=BaseKPI)
        ownership_kpi2.value = {"Bob": 100}
        file2.kpis['Code Ownership'] = ownership_kpi2

        formatter = CLIQuickWinsFormat()
        quick_wins = formatter._calculate_quick_wins([file2, file1])  # Intentionally wrong order

        # High ROI should be first
        self.assertEqual(len(quick_wins), 2)
        self.assertEqual(quick_wins[0]['file'], file1)
        self.assertEqual(quick_wins[1]['file'], file2)
        self.assertGreater(quick_wins[0]['roi'], quick_wins[1]['roi'])

    def test_calculate_quick_wins_filters_low_impact(self):
        """Test that files with low impact are filtered out."""
        file1 = File(name="low_impact.py", file_path="low_impact.py")
        file1.functions = [Function(name="func1")]

        complexity_kpi = MagicMock(spec=BaseKPI)
        complexity_kpi.value = 2
        file1.kpis['complexity'] = complexity_kpi

        churn_kpi = MagicMock(spec=BaseKPI)
        churn_kpi.value = 1
        file1.kpis['churn'] = churn_kpi

        hotspot_kpi = MagicMock(spec=BaseKPI)
        hotspot_kpi.value = 5
        file1.kpis['hotspot'] = hotspot_kpi

        ownership_kpi = MagicMock(spec=BaseKPI)
        ownership_kpi.value = {"Alice": 100}
        file1.kpis['Code Ownership'] = ownership_kpi

        formatter = CLIQuickWinsFormat()
        quick_wins = formatter._calculate_quick_wins([file1])

        # Impact=0, should be filtered
        self.assertEqual(len(quick_wins), 0)

    def test_calculate_quick_wins_empty_repo(self):
        """Test quick wins calculation with empty repository."""
        formatter = CLIQuickWinsFormat()
        quick_wins = formatter._calculate_quick_wins([])

        self.assertEqual(len(quick_wins), 0)


class TestDetermineAction(unittest.TestCase):
    """Test _determine_action method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CLIQuickWinsFormat()

    def test_determine_action_document(self):
        """Test action determination for documentation."""
        file_obj = File(name="test.py", file_path="test.py")

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 1}

        action, desc, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=35,
            churn=5,
            hotspot=100,
            ownership_kpi=MagicMock(),
            shared_kpi=shared_kpi
        )
        self.assertEqual(action, "Document")
        self.assertIn("single owner", reason.lower())

    def test_determine_action_refactor_critical(self):
        """Test action determination for critical refactoring."""
        file_obj = File(name="test.py", file_path="test.py")

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 2}

        action, desc, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=20,
            churn=15,
            hotspot=200,
            ownership_kpi=MagicMock(),
            shared_kpi=shared_kpi
        )
        self.assertEqual(action, "Refactor")
        self.assertIn("critical hotspot", reason.lower())

    def test_determine_action_refactor_high_complexity(self):
        """Test action determination for high complexity refactoring."""
        file_obj = File(name="test.py", file_path="test.py")

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 2}

        action, desc, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=25,
            churn=5,
            hotspot=50,
            ownership_kpi=MagicMock(),
            shared_kpi=shared_kpi
        )
        self.assertEqual(action, "Refactor")
        self.assertIn("high complexity", reason.lower())

    def test_determine_action_add_tests(self):
        """Test action determination for adding tests."""
        file_obj = File(name="test.py", file_path="test.py")

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 2}

        action, desc, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=10,
            churn=15,
            hotspot=50,
            ownership_kpi=MagicMock(),
            shared_kpi=shared_kpi
        )
        self.assertEqual(action, "Add Tests")
        self.assertIn("high churn", reason.lower())

    def test_determine_action_review_ownership(self):
        """Test action determination for ownership review."""
        file_obj = File(name="test.py", file_path="test.py")

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 5}

        action, desc, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=10,
            churn=5,
            hotspot=50,
            ownership_kpi=MagicMock(),
            shared_kpi=shared_kpi
        )
        self.assertEqual(action, "Review Ownership")
        self.assertIn("fragmented", reason.lower())

    def test_determine_action_improve(self):
        """Test action determination for general improvement."""
        file_obj = File(name="test.py", file_path="test.py")

        shared_kpi = MagicMock(spec=BaseKPI)
        shared_kpi.value = {'num_significant_authors': 2}

        action, desc, reason = self.formatter._determine_action(
            file_obj=file_obj,
            complexity=10,
            churn=5,
            hotspot=50,
            ownership_kpi=MagicMock(),
            shared_kpi=shared_kpi
        )
        self.assertEqual(action, "Improve")
        self.assertIn("moderate", reason.lower())


class TestEstimateTime(unittest.TestCase):
    """Test _estimate_time method."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CLIQuickWinsFormat()

    def test_estimate_time_very_low_effort(self):
        """Test time estimation for very low effort."""
        time = self.formatter._estimate_time(effort=1, complexity=5)
        self.assertEqual(time, "30-60 min")

    def test_estimate_time_low_effort(self):
        """Test time estimation for low effort."""
        time = self.formatter._estimate_time(effort=3, complexity=15)
        self.assertEqual(time, "1-2 hours")

    def test_estimate_time_medium_effort(self):
        """Test time estimation for medium effort."""
        time = self.formatter._estimate_time(effort=5, complexity=25)
        self.assertEqual(time, "2-4 hours")

    def test_estimate_time_high_effort(self):
        """Test time estimation for high effort."""
        time = self.formatter._estimate_time(effort=7, complexity=50)
        self.assertEqual(time, "4-8 hours")

    def test_estimate_time_very_high_effort(self):
        """Test time estimation for very high effort."""
        time = self.formatter._estimate_time(effort=9, complexity=100)
        self.assertEqual(time, "1-2 days")


class TestPrintMethods(unittest.TestCase):
    """Test output formatting methods."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = CLIQuickWinsFormat()

    def test_create_bar_full(self):
        """Test creating a full progress bar."""
        bar = self.formatter._create_bar(10, 10)
        self.assertEqual(bar, "██████████")

    def test_create_bar_half(self):
        """Test creating a half-filled progress bar."""
        bar = self.formatter._create_bar(5, 10)
        self.assertEqual(bar, "█████░░░░░")

    def test_create_bar_empty(self):
        """Test creating an empty progress bar."""
        bar = self.formatter._create_bar(0, 10)
        self.assertEqual(bar, "░░░░░░░░░░")

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_header(self, mock_stdout):
        """Test printing the header."""
        self.formatter._print_header()
        output = mock_stdout.getvalue()
        self.assertIn("QUICK WIN SUGGESTIONS", output)
        self.assertIn("╔", output)
        self.assertIn("╗", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_quick_win(self, mock_stdout):
        """Test printing a single quick win."""
        file_obj = File(name="test.py", file_path="test.py")
        win = {
            'file': file_obj,
            'file_path': "test.py",
            'impact': 7,
            'effort': 3,
            'action_type': "Refactor",
            'action_desc': "Break down function",
            'reason': "High complexity",
            'time_estimate': "2-4 hours",
            'complexity': 25,
            'cognitive_complexity': 15,
            'churn': 10,
            'hotspot': 250
        }
        self.formatter._print_quick_win(1, win)
        output = mock_stdout.getvalue()
        self.assertIn("Refactor", output)
        self.assertIn("test.py", output)
        self.assertIn("Impact", output)
        self.assertIn("Effort", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_summary(self, mock_stdout):
        """Test printing the summary."""
        file1 = File(name="file1.py", file_path="file1.py")
        file2 = File(name="file2.py", file_path="file2.py")

        quick_wins = [
            {
                'file': file1,
                'file_path': "file1.py",
                'action_type': "Refactor",
                'impact': 8,
                'effort': 2,
                'roi': 4.0
            },
            {
                'file': file2,
                'file_path': "file2.py",
                'action_type': "Add Tests",
                'impact': 6,
                'effort': 3,
                'roi': 2.0
            }
        ]
        self.formatter._print_summary(quick_wins)
        output = mock_stdout.getvalue()
        self.assertIn("SUMMARY", output)
        self.assertIn("Total Opportunities", output)
        self.assertIn("Best ROI", output)
        self.assertIn("file1.py", output)


class TestPrintReportIntegration(unittest.TestCase):
    """Integration tests for print_report method."""

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_report_with_quick_wins(self, mock_stdout):
        """Test full report generation with quick wins."""
        file1 = File(name="test.py", file_path="test.py")
        file1.functions = [Function(name=f"func{i}") for i in range(5)]

        complexity_kpi = MagicMock(spec=BaseKPI)
        complexity_kpi.value = 25
        file1.kpis['complexity'] = complexity_kpi

        churn_kpi = MagicMock(spec=BaseKPI)
        churn_kpi.value = 12
        file1.kpis['churn'] = churn_kpi

        hotspot_kpi = MagicMock(spec=BaseKPI)
        hotspot_kpi.value = 300
        file1.kpis['hotspot'] = hotspot_kpi

        ownership_kpi = MagicMock(spec=BaseKPI)
        ownership_kpi.value = {"Alice": 100}
        file1.kpis['Code Ownership'] = ownership_kpi

        repo_info = RepoInfo(
            dir_name="test_repo",
            scan_dir_path=".",
            repo_root_path="/test",
            repo_name="test_repo"
        )
        repo_info.files = {"test.py": file1}

        formatter = CLIQuickWinsFormat()
        formatter.print_report(repo_info, debug_print=lambda x: None)

        output = mock_stdout.getvalue()
        self.assertIn("QUICK WIN SUGGESTIONS", output)
        self.assertIn("test.py", output)
        self.assertIn("SUMMARY", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_print_report_empty_repo(self, mock_stdout):
        """Test report generation with no quick wins."""
        repo_info = RepoInfo(
            dir_name="empty_repo",
            scan_dir_path=".",
            repo_root_path="/test",
            repo_name="empty_repo"
        )

        formatter = CLIQuickWinsFormat()
        formatter.print_report(repo_info, debug_print=lambda x: None)

        output = mock_stdout.getvalue()
        self.assertIn("No significant improvement opportunities found", output)


if __name__ == '__main__':
    unittest.main()
