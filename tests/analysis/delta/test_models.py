"""
Test module for delta analysis data models.

Following TDD (RED-GREEN-REFACTOR):
- RED: Write failing tests first
- GREEN: Implement minimal code to pass
- REFACTOR: Clean up implementation
"""

import pytest
from datetime import datetime
from typing import Optional


class TestChangeType:
    """Test ChangeType enum."""

    def test_change_type_has_added(self):
        """Test that ChangeType has ADDED value."""
        from src.analysis.delta.models import ChangeType
        assert hasattr(ChangeType, 'ADDED')

    def test_change_type_has_modified(self):
        """Test that ChangeType has MODIFIED value."""
        from src.analysis.delta.models import ChangeType
        assert hasattr(ChangeType, 'MODIFIED')

    def test_change_type_has_deleted(self):
        """Test that ChangeType has DELETED value."""
        from src.analysis.delta.models import ChangeType
        assert hasattr(ChangeType, 'DELETED')


class TestFunctionChange:
    """Test FunctionChange data model."""

    def test_function_change_creation_with_all_fields(self):
        """Test creating FunctionChange with all required fields."""
        from src.analysis.delta.models import FunctionChange, ChangeType

        change = FunctionChange(
            file_path="src/test.py",
            function_name="test_function",
            start_line=10,
            end_line=20,
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=8,
            complexity_delta=3,
            churn=10,
            hotspot_score=80.0,
            last_author="test@example.com",
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=15,
            review_time_minutes=12
        )

        assert change.file_path == "src/test.py"
        assert change.function_name == "test_function"
        assert change.start_line == 10
        assert change.end_line == 20
        assert change.change_type == ChangeType.MODIFIED
        assert change.complexity_before == 5
        assert change.complexity_after == 8
        assert change.complexity_delta == 3
        assert change.churn == 10
        assert change.hotspot_score == 80.0
        assert change.last_author == "test@example.com"
        assert change.lines_changed == 15
        assert change.review_time_minutes == 12

    def test_function_change_with_added_function(self):
        """Test FunctionChange for newly added function (no before complexity)."""
        from src.analysis.delta.models import FunctionChange, ChangeType

        change = FunctionChange(
            file_path="src/new.py",
            function_name="new_function",
            start_line=1,
            end_line=10,
            change_type=ChangeType.ADDED,
            complexity_before=None,  # No previous version
            complexity_after=5,
            complexity_delta=5,
            churn=1,
            hotspot_score=5.0,
            last_author="dev@example.com",
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=10,
            review_time_minutes=8
        )

        assert change.change_type == ChangeType.ADDED
        assert change.complexity_before is None
        assert change.complexity_after == 5
        assert change.complexity_delta == 5

    def test_function_change_with_deleted_function(self):
        """Test FunctionChange for deleted function (no after complexity)."""
        from src.analysis.delta.models import FunctionChange, ChangeType

        change = FunctionChange(
            file_path="src/old.py",
            function_name="old_function",
            start_line=1,
            end_line=10,
            change_type=ChangeType.DELETED,
            complexity_before=10,
            complexity_after=None,  # Deleted
            complexity_delta=-10,
            churn=50,
            hotspot_score=500.0,
            last_author="old@example.com",
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=10,
            review_time_minutes=0  # No review needed for deletion
        )

        assert change.change_type == ChangeType.DELETED
        assert change.complexity_before == 10
        assert change.complexity_after is None
        assert change.complexity_delta == -10
        assert change.review_time_minutes == 0

    def test_function_change_calculates_negative_delta(self):
        """Test that complexity_delta can be negative (refactoring)."""
        from src.analysis.delta.models import FunctionChange, ChangeType

        change = FunctionChange(
            file_path="src/refactored.py",
            function_name="refactored_func",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=15,
            complexity_after=8,
            complexity_delta=-7,  # Improved!
            churn=5,
            hotspot_score=40.0,
            last_author="refactor@example.com",
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=20,
            review_time_minutes=10
        )

        assert change.complexity_delta == -7
        assert change.complexity_after < change.complexity_before


class TestDeltaDiff:
    """Test DeltaDiff data model."""

    def test_delta_diff_creation_empty(self):
        """Test creating empty DeltaDiff."""
        from src.analysis.delta.models import DeltaDiff

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

        assert delta.base_commit == "abc123"
        assert delta.target_commit == "def456"
        assert len(delta.added_functions) == 0
        assert len(delta.modified_functions) == 0
        assert len(delta.deleted_functions) == 0
        assert delta.total_complexity_delta == 0
        assert delta.total_review_time_minutes == 0

    def test_delta_diff_with_changes(self):
        """Test DeltaDiff with actual function changes."""
        from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType

        added = FunctionChange(
            file_path="src/new.py",
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
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=5,
            review_time_minutes=5
        )

        modified = FunctionChange(
            file_path="src/changed.py",
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
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=10,
            review_time_minutes=10
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[added],
            modified_functions=[modified],
            deleted_functions=[],
            total_complexity_delta=6,  # 3 + 3
            total_review_time_minutes=15,  # 5 + 10
            critical_changes=[modified],  # Highest hotspot
            refactorings=[]
        )

        assert len(delta.added_functions) == 1
        assert len(delta.modified_functions) == 1
        assert delta.total_complexity_delta == 6
        assert delta.total_review_time_minutes == 15
        assert len(delta.critical_changes) == 1
        assert delta.critical_changes[0].hotspot_score == 80.0

    def test_delta_diff_identifies_refactorings(self):
        """Test that DeltaDiff can identify refactorings (negative delta)."""
        from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType

        refactoring = FunctionChange(
            file_path="src/improved.py",
            function_name="improved_func",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=20,
            complexity_after=10,
            complexity_delta=-10,  # Improved!
            churn=5,
            hotspot_score=50.0,
            last_author="refactor@example.com",
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=15,
            review_time_minutes=8
        )

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[],
            modified_functions=[refactoring],
            deleted_functions=[],
            total_complexity_delta=-10,
            total_review_time_minutes=8,
            critical_changes=[],
            refactorings=[refactoring]
        )

        assert delta.total_complexity_delta == -10
        assert len(delta.refactorings) == 1
        assert delta.refactorings[0].complexity_delta < 0

    def test_delta_diff_total_function_count(self):
        """Test calculating total number of changed functions."""
        from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType

        # Create some changes
        changes = []
        for i in range(3):
            changes.append(FunctionChange(
                file_path=f"src/file{i}.py",
                function_name=f"func{i}",
                start_line=1,
                end_line=10,
                change_type=ChangeType.MODIFIED,
                complexity_before=5,
                complexity_after=6,
                complexity_delta=1,
                churn=1,
                hotspot_score=6.0,
                last_author="dev@example.com",
                last_modified=datetime(2025, 10, 17, 10, 0, 0),
                lines_changed=5,
                review_time_minutes=5
            ))

        delta = DeltaDiff(
            base_commit="abc123",
            target_commit="def456",
            added_functions=[changes[0]],
            modified_functions=[changes[1]],
            deleted_functions=[changes[2]],
            total_complexity_delta=1,
            total_review_time_minutes=15,
            critical_changes=[],
            refactorings=[]
        )

        total_changes = (len(delta.added_functions) +
                        len(delta.modified_functions) +
                        len(delta.deleted_functions))
        assert total_changes == 3


class TestDataModelValidation:
    """Test validation and edge cases for data models."""

    def test_function_change_requires_valid_line_numbers(self):
        """Test that start_line must be <= end_line."""
        from src.analysis.delta.models import FunctionChange, ChangeType

        # This should work
        change = FunctionChange(
            file_path="src/test.py",
            function_name="test",
            start_line=10,
            end_line=20,
            change_type=ChangeType.MODIFIED,
            complexity_before=5,
            complexity_after=5,
            complexity_delta=0,
            churn=1,
            hotspot_score=5.0,
            last_author="dev@example.com",
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=0,
            review_time_minutes=0
        )
        assert change.start_line <= change.end_line

    def test_hotspot_score_is_complexity_times_churn(self):
        """Test that hotspot_score formula is correct (complexity × churn)."""
        from src.analysis.delta.models import FunctionChange, ChangeType

        complexity_after = 10
        churn = 8
        expected_hotspot = complexity_after * churn  # 80

        change = FunctionChange(
            file_path="src/test.py",
            function_name="test",
            start_line=1,
            end_line=10,
            change_type=ChangeType.MODIFIED,
            complexity_before=8,
            complexity_after=complexity_after,
            complexity_delta=2,
            churn=churn,
            hotspot_score=expected_hotspot,
            last_author="dev@example.com",
            last_modified=datetime(2025, 10, 17, 10, 0, 0),
            lines_changed=5,
            review_time_minutes=10
        )

        assert change.hotspot_score == expected_hotspot
        assert change.hotspot_score == change.complexity_after * change.churn
