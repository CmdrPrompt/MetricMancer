"""
Test module for DeltaReviewStrategyFormat.

Following TDD (RED-GREEN-REFACTOR):
- Tests define the output format and content
- Format should be markdown with clear sections
"""

from datetime import datetime
from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType


def create_function_change(
    file_path="test.py",
    function_name="func",
    start_line=1,
    end_line=10,
    change_type=ChangeType.MODIFIED,
    complexity_before=5,
    complexity_after=8,
    complexity_delta=3,
    cognitive_complexity_before=None,  # Auto-calculate if None
    cognitive_complexity_after=None,  # Auto-calculate if None
    cognitive_complexity_delta=None,  # Auto-calculate if None
    churn=1,
    hotspot_score=8.0,
    last_author="dev@example.com",
    lines_changed=10,
    review_time_minutes=10
):
    """Helper to create FunctionChange with cognitive complexity fields.

    Auto-calculates cognitive complexity if not provided (uses cyclomatic - 2 or 0).
    """
    # Auto-calculate cognitive complexity if not provided
    if cognitive_complexity_before is None:
        cognitive_complexity_before = max(0, (complexity_before - 2)) if complexity_before is not None else None

    if cognitive_complexity_after is None:
        cognitive_complexity_after = max(0, (complexity_after - 2)) if complexity_after is not None else None

    if cognitive_complexity_delta is None:
        if cognitive_complexity_before is not None and cognitive_complexity_after is not None:
            cognitive_complexity_delta = cognitive_complexity_after - cognitive_complexity_before
        elif cognitive_complexity_after is not None:
            cognitive_complexity_delta = cognitive_complexity_after
        elif cognitive_complexity_before is not None:
            cognitive_complexity_delta = -cognitive_complexity_before
        else:
            cognitive_complexity_delta = 0

    return FunctionChange(
        file_path=file_path,
        function_name=function_name,
        start_line=start_line,
        end_line=end_line,
        change_type=change_type,
        complexity_before=complexity_before,
        complexity_after=complexity_after,
        complexity_delta=complexity_delta,
        cognitive_complexity_before=cognitive_complexity_before,
        cognitive_complexity_after=cognitive_complexity_after,
        cognitive_complexity_delta=cognitive_complexity_delta,
        churn=churn,
        hotspot_score=hotspot_score,
        last_author=last_author,
        last_modified=datetime.now(),
        lines_changed=lines_changed,
        review_time_minutes=review_time_minutes
    )


class TestDeltaReviewFormatBasics:
    """Test basic formatting functionality."""

    def test_format_initialization(self):
        """Test creating a DeltaReviewStrategyFormat instance."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()
        assert formatter is not None

    def test_format_empty_delta(self):
        """Test formatting an empty delta (no changes)."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[],
            deleted_functions=[],
            total_complexity_delta=0,
            total_review_time_minutes=0,
            critical_changes=[],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should produce valid markdown
        assert isinstance(output, str)
        assert len(output) > 0
        assert "# Delta Review Strategy" in output
        assert "No changes detected" in output or "0 function" in output.lower()


class TestOverviewSection:
    """Test the overview section of the report."""

    def test_overview_shows_commit_info(self):
        """Test that overview includes commit information."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[],
            deleted_functions=[],
            total_complexity_delta=0,
            total_review_time_minutes=0,
            critical_changes=[],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should show commits
        assert "abc123" in output
        assert "def456" in output

    def test_overview_shows_function_counts(self):
        """Test that overview shows function change counts."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        # Create sample changes
        added = create_function_change(
            file_path="test.py",
            function_name="new_func",
            start_line=1,
            end_line=5,
            change_type=ChangeType.ADDED,
            complexity_before=None,
            complexity_after=3,
            complexity_delta=3,
            churn=1,
            hotspot_score=3.0,
            last_author="dev@example.com",
            lines_changed=5,
            review_time_minutes=5,
        )

        modified = create_function_change(
            file_path="test.py",
            function_name="changed_func",
            start_line=10,
            end_line=20,
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=8,
            complexity_delta=3,
            churn=10,
            hotspot_score=80.0,
            last_author="dev@example.com",
            lines_changed=10,
            review_time_minutes=10,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[added],
            modified_functions=[modified],
            deleted_functions=[],
            total_complexity_delta=6,
            total_review_time_minutes=15,
            critical_changes=[modified],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should show counts
        assert "1" in output  # Added functions
        assert "1" in output  # Modified functions
        assert "15" in output or "15 min" in output.lower()  # Review time

    def test_overview_shows_complexity_delta(self):
        """Test that overview shows total complexity change."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        modified = create_function_change(
            file_path="test.py",
            function_name="func",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=15,
            complexity_delta=10,
            churn=5,
            hotspot_score=75.0,
            last_author="dev@example.com",
            lines_changed=10,
            review_time_minutes=15,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[modified],
            deleted_functions=[],
            total_complexity_delta=10,
            total_review_time_minutes=15,
            critical_changes=[modified],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should show complexity increase
        assert "+10" in output or "10" in output


class TestCriticalChangesSection:
    """Test the critical changes section."""

    def test_critical_changes_section_exists(self):
        """Test that critical changes section is present."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        critical = create_function_change(
            file_path="critical.py",
            function_name="hotspot_func",
            start_line=1,
            end_line=50,
            change_type=ChangeType.MODIFIED,
            complexity_before=10,
            complexity_after=25,
            complexity_delta=15,
            churn=20,
            hotspot_score=500.0,
            last_author="dev@example.com",
            lines_changed=30,
            review_time_minutes=30,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[critical],
            deleted_functions=[],
            total_complexity_delta=15,
            total_review_time_minutes=30,
            critical_changes=[critical],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should have critical changes section
        assert "Critical" in output or "Hotspot" in output
        assert "hotspot_func" in output
        assert "critical.py" in output

    def test_critical_changes_show_complexity_increase(self):
        """Test that critical changes highlight complexity increases."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        critical = create_function_change(
            file_path="test.py",
            function_name="complex_func",
            start_line=1,
            end_line=20,
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=20,
            complexity_delta=15,
            churn=10,
            hotspot_score=200.0,
            last_author="dev@example.com",
            lines_changed=15,
            review_time_minutes=25,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[critical],
            deleted_functions=[],
            total_complexity_delta=15,
            total_review_time_minutes=25,
            critical_changes=[critical],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should show complexity change
        assert "5" in output  # Before
        assert "20" in output  # After
        assert "15" in output or "+15" in output  # Delta

    def test_critical_changes_show_hotspot_score(self):
        """Test that hotspot scores are displayed."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        critical = create_function_change(
            file_path="test.py",
            function_name="func",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=10,
            complexity_after=15,
            complexity_delta=5,
            churn=20,
            hotspot_score=300.0,
            last_author="dev@example.com",
            lines_changed=10,
            review_time_minutes=20,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[critical],
            deleted_functions=[],
            total_complexity_delta=5,
            total_review_time_minutes=20,
            critical_changes=[critical],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should show hotspot score
        assert "300" in output or "Hotspot" in output


class TestRefactoringsSection:
    """Test the refactorings section (complexity improvements)."""

    def test_refactorings_section_exists(self):
        """Test that refactorings are highlighted."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        refactoring = create_function_change(
            file_path="improved.py",
            function_name="simplified_func",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=20,
            complexity_after=10,
            complexity_delta=-10,
            churn=5,
            hotspot_score=50.0,
            last_author="dev@example.com",
            lines_changed=15,
            review_time_minutes=10,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[refactoring],
            deleted_functions=[],
            total_complexity_delta=-10,
            total_review_time_minutes=10,
            critical_changes=[],
            refactorings=[refactoring]
        )

        output = formatter.format(delta)

        # Should have refactorings section
        assert "Refactor" in output or "Improve" in output or "simplified" in output.lower()
        assert "simplified_func" in output
        assert "-10" in output or "decreased" in output.lower()


class TestAddedFunctionsSection:
    """Test section for newly added functions."""

    def test_added_functions_section(self):
        """Test that added functions are shown."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        added = create_function_change(
            file_path="new.py",
            function_name="brand_new_func",
            start_line=1,
            end_line=20,
            change_type=ChangeType.ADDED,
            complexity_before=None,
            complexity_after=15,
            complexity_delta=15,
            churn=1,
            hotspot_score=15.0,
            last_author="dev@example.com",
            lines_changed=20,
            review_time_minutes=15,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[added],
            modified_functions=[],
            deleted_functions=[],
            total_complexity_delta=15,
            total_review_time_minutes=15,
            critical_changes=[],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should show added function
        assert "brand_new_func" in output
        assert "new.py" in output
        assert "Added" in output or "New" in output


class TestMarkdownFormatting:
    """Test that output is valid markdown."""

    def test_output_has_headers(self):
        """Test that output has proper markdown headers."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[],
            deleted_functions=[],
            total_complexity_delta=0,
            total_review_time_minutes=0,
            critical_changes=[],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should have markdown headers
        assert output.count("# ") >= 1  # At least one H1
        assert output.count("## ") >= 1  # At least one H2

    def test_output_has_lists(self):
        """Test that output uses markdown lists for items."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        func = create_function_change(
            file_path="test.py",
            function_name="func",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=8,
            complexity_delta=3,
            churn=5,
            hotspot_score=40.0,
            last_author="dev@example.com",
            lines_changed=5,
            review_time_minutes=8,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[func],
            deleted_functions=[],
            total_complexity_delta=3,
            total_review_time_minutes=8,
            critical_changes=[func],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should use markdown lists
        assert "- " in output or "* " in output or "1. " in output

    def test_output_uses_code_blocks(self):
        """Test that function names are formatted as code."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        func = create_function_change(
            file_path="test.py",
            function_name="my_function",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=8,
            complexity_delta=3,
            churn=5,
            hotspot_score=40.0,
            last_author="dev@example.com",
            lines_changed=5,
            review_time_minutes=8,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[func],
            deleted_functions=[],
            total_complexity_delta=3,
            total_review_time_minutes=8,
            critical_changes=[func],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should use inline code for function names
        assert "`my_function" in output or "my_function()" in output


class TestReviewGuidance:
    """Test that format provides actionable review guidance."""

    def test_high_complexity_gets_review_checklist(self):
        """Test that high complexity changes get review checklists."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        high_complexity = create_function_change(
            file_path="complex.py",
            function_name="very_complex_func",
            start_line=1,
            end_line=100,
            change_type=ChangeType.MODIFIED,
            complexity_before=10,
            complexity_after=30,
            complexity_delta=20,
            churn=10,
            hotspot_score=300.0,
            last_author="dev@example.com",
            lines_changed=50,
            review_time_minutes=40,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[high_complexity],
            deleted_functions=[],
            total_complexity_delta=20,
            total_review_time_minutes=40,
            critical_changes=[high_complexity],
            refactorings=[]
        )

        output = formatter.format(delta)

        # Should provide review guidance
        assert "Focus" in output or "Review" in output or "Check" in output
        # Should have checkboxes or action items
        assert "[ ]" in output or "- [ ]" in output or "test" in output.lower()

    def test_refactoring_gets_validation_guidance(self):
        """Test that refactorings get validation checklists."""
        from src.analysis.delta.delta_review_format import DeltaReviewStrategyFormat

        formatter = DeltaReviewStrategyFormat()

        refactoring = create_function_change(
            file_path="improved.py",
            function_name="refactored_func",
            start_line=1,
            end_line=20,
            change_type=ChangeType.MODIFIED,
            complexity_before=25,
            complexity_after=10,
            complexity_delta=-15,
            churn=5,
            hotspot_score=50.0,
            last_author="dev@example.com",
            lines_changed=20,
            review_time_minutes=15,
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[refactoring],
            deleted_functions=[],
            total_complexity_delta=-15,
            total_review_time_minutes=15,
            critical_changes=[],
            refactorings=[refactoring]
        )

        output = formatter.format(delta)

        # Should suggest validation steps
        assert "behav" in output.lower() or "test" in output.lower() or "verify" in output.lower()
