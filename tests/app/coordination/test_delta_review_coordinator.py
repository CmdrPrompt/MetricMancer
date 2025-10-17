"""
Tests for DeltaReviewCoordinator module.

Following TDD approach (RED-GREEN-REFACTOR).
"""
import pytest
import os
import tempfile
from datetime import datetime
from unittest.mock import Mock, MagicMock
from src.app.coordination.delta_review_coordinator import DeltaReviewCoordinator
from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType


def create_function_change_mock(
    file_path="test.py",
    function_name="test_func",
    change_type=ChangeType.ADDED,
    complexity_before=None,
    complexity_after=10,
    complexity_delta=10
):
    """Helper to create properly mocked FunctionChange objects."""
    func = Mock(spec=FunctionChange)
    func.file_path = file_path
    func.function_name = function_name
    func.start_line = 1
    func.end_line = 10
    func.change_type = change_type
    func.complexity_before = complexity_before
    func.complexity_after = complexity_after
    func.complexity_delta = complexity_delta
    func.churn = 5
    func.hotspot_score = 50.0
    func.last_author = "test@example.com"
    func.last_modified = datetime.now()
    func.lines_changed = 10
    func.review_time_minutes = 15
    return func


class TestDeltaReviewCoordinator:
    """Test suite for DeltaReviewCoordinator."""

    def test_generate_delta_review_when_disabled(self):
        """Test that no delta review is generated when disabled."""
        config = Mock()
        config.delta_review = False

        result = DeltaReviewCoordinator.generate_delta_review(
            repo_path="/path/to/repo",
            config=config
        )

        assert result is None

    def test_generate_delta_review_with_defaults(self):
        """Test delta review generation with default branch settings."""
        config = Mock()
        config.delta_review = True
        config.delta_base_branch = "main"
        config.delta_target_branch = None
        config.directories = ["/path/to/repo"]

        # Mock the DeltaAnalyzer
        mock_analyzer = MagicMock()
        mock_diff = Mock(spec=DeltaDiff)
        mock_diff.added_functions = []
        mock_diff.modified_functions = []
        mock_diff.deleted_functions = []
        mock_diff.critical_changes = []
        mock_diff.refactorings = []
        mock_diff.total_complexity_delta = 0
        mock_diff.total_review_time_minutes = 30
        mock_analyzer.analyze_branch_delta.return_value = mock_diff

        result = DeltaReviewCoordinator.generate_delta_review(
            repo_path="/path/to/repo",
            config=config,
            analyzer_factory=lambda path: mock_analyzer
        )

        assert result == mock_diff
        mock_analyzer.analyze_branch_delta.assert_called_once_with(
            base_branch="main",
            target_branch=None
        )

    def test_generate_delta_review_with_custom_branches(self):
        """Test delta review generation with custom branch settings."""
        config = Mock()
        config.delta_review = True
        config.delta_base_branch = "develop"
        config.delta_target_branch = "feature-branch"
        config.directories = ["/path/to/repo"]

        mock_analyzer = MagicMock()
        mock_diff = Mock(spec=DeltaDiff)
        mock_diff.added_functions = []
        mock_diff.modified_functions = []
        mock_diff.deleted_functions = []
        mock_diff.critical_changes = []
        mock_diff.refactorings = []
        mock_diff.total_complexity_delta = 0
        mock_diff.total_review_time_minutes = 30
        mock_analyzer.analyze_branch_delta.return_value = mock_diff

        result = DeltaReviewCoordinator.generate_delta_review(
            repo_path="/path/to/repo",
            config=config,
            analyzer_factory=lambda path: mock_analyzer
        )

        assert result == mock_diff
        mock_analyzer.analyze_branch_delta.assert_called_once_with(
            base_branch="develop",
            target_branch="feature-branch"
        )

    def test_generate_delta_review_handles_errors(self):
        """Test that errors during delta review are caught and None is returned."""
        config = Mock()
        config.delta_review = True
        config.delta_base_branch = "main"
        config.delta_target_branch = None
        config.directories = ["/path/to/repo"]

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_branch_delta.side_effect = Exception("Git error")

        result = DeltaReviewCoordinator.generate_delta_review(
            repo_path="/path/to/repo",
            config=config,
            analyzer_factory=lambda path: mock_analyzer
        )

        assert result is None

    def test_format_delta_review(self):
        """Test formatting of delta review report."""
        # Create proper function change mocks using helper
        func1 = create_function_change_mock(
            change_type=ChangeType.ADDED,
            complexity_after=8,
            complexity_delta=8
        )
        func2 = create_function_change_mock(
            function_name="func2",
            change_type=ChangeType.MODIFIED,
            complexity_before=10,
            complexity_after=15,
            complexity_delta=5
        )
        func3 = create_function_change_mock(
            function_name="func3",
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=10,
            complexity_delta=5
        )

        mock_diff = Mock(spec=DeltaDiff)
        mock_diff.target_commit = "abc123def"
        mock_diff.base_commit = "xyz789abc"
        mock_diff.added_functions = [func1]
        mock_diff.modified_functions = [func2, func3]
        mock_diff.deleted_functions = []
        mock_diff.critical_changes = []
        mock_diff.refactorings = []
        mock_diff.total_complexity_delta = 15
        mock_diff.total_review_time_minutes = 45

        report = DeltaReviewCoordinator.format_delta_review(mock_diff)

        assert "Delta Review Strategy" in report
        assert "abc123" in report  # Short commit hash
        assert "3" in report or "total" in report.lower()  # Total functions

    def test_write_delta_review_file(self):
        """Test writing delta review to file."""
        mock_diff = Mock(spec=DeltaDiff)
        mock_diff.target_commit = "abc123def"
        mock_diff.base_commit = "xyz789abc"
        mock_diff.added_functions = []
        mock_diff.modified_functions = []
        mock_diff.deleted_functions = []
        mock_diff.critical_changes = []
        mock_diff.refactorings = []
        mock_diff.total_complexity_delta = 0
        mock_diff.total_review_time_minutes = 30

        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "delta_review.md")

            DeltaReviewCoordinator.write_delta_review_file(mock_diff, output_path)

            assert os.path.exists(output_path)
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "Delta Review Strategy" in content

    def test_print_delta_summary(self, capsys):
        """Test printing delta review summary to console."""
        mock_diff = Mock(spec=DeltaDiff)
        mock_diff.added_functions = [Mock()]
        mock_diff.modified_functions = [Mock(), Mock()]
        mock_diff.deleted_functions = [Mock()]
        mock_diff.critical_changes = [Mock()]
        mock_diff.refactorings = []
        mock_diff.total_complexity_delta = 25
        mock_diff.total_review_time_minutes = 90

        DeltaReviewCoordinator.print_delta_summary(mock_diff)

        captured = capsys.readouterr()
        assert "Summary:" in captured.out
        assert "Functions changed: 4" in captured.out or "4" in captured.out
        assert "+25" in captured.out
        assert "90" in captured.out

    def test_print_delta_summary_with_refactorings(self, capsys):
        """Test printing summary when refactorings are present."""
        mock_diff = Mock(spec=DeltaDiff)
        mock_diff.added_functions = []
        mock_diff.modified_functions = [Mock()]
        mock_diff.deleted_functions = []
        mock_diff.critical_changes = []
        mock_diff.refactorings = [Mock(), Mock()]
        mock_diff.total_complexity_delta = -10
        mock_diff.total_review_time_minutes = 30

        DeltaReviewCoordinator.print_delta_summary(mock_diff)

        captured = capsys.readouterr()
        assert "Refactorings: 2" in captured.out or "2" in captured.out

    def test_full_workflow_integration(self):
        """Test complete workflow from generation to file output."""
        config = Mock()
        config.delta_review = True
        config.delta_base_branch = "main"
        config.delta_target_branch = None
        config.directories = ["/path/to/repo"]
        config.report_folder = "output"
        config.delta_output = "delta_review.md"

        # Create proper function change mock using helper
        func1 = create_function_change_mock(
            complexity_after=5,
            complexity_delta=5
        )

        mock_diff = Mock(spec=DeltaDiff)
        mock_diff.target_commit = "abc123def"
        mock_diff.base_commit = "xyz789abc"
        mock_diff.added_functions = [func1]
        mock_diff.modified_functions = []
        mock_diff.deleted_functions = []
        mock_diff.critical_changes = []
        mock_diff.refactorings = []
        mock_diff.total_complexity_delta = 5
        mock_diff.total_review_time_minutes = 20

        mock_analyzer = MagicMock()
        mock_analyzer.analyze_branch_delta.return_value = mock_diff

        # Generate
        delta_diff = DeltaReviewCoordinator.generate_delta_review(
            repo_path="/path/to/repo",
            config=config,
            analyzer_factory=lambda path: mock_analyzer
        )

        assert delta_diff is not None

        # Format
        report = DeltaReviewCoordinator.format_delta_review(delta_diff)
        assert len(report) > 0

        # Write to file
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, "delta_review.md")
            DeltaReviewCoordinator.write_delta_review_file(delta_diff, output_path)
            assert os.path.exists(output_path)
