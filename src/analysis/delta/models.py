"""
Data models for delta analysis.

These models represent function-level changes detected between git commits,
following Adam Tornhill's "Your Code as a Crime Scene" methodology.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class ChangeType(Enum):
    """Type of change to a function."""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"


@dataclass
class FunctionChange:
    """
    Represents a single function change detected in delta analysis.

    This is the core data structure for function-level diff tracking.
    Each instance represents one function that was added, modified, or deleted.
    """

    file_path: str
    function_name: str
    start_line: int
    end_line: int
    change_type: ChangeType

    # Cyclomatic complexity (branch coverage metric)
    complexity_before: Optional[int]  # None for ADDED functions
    complexity_after: Optional[int]   # None for DELETED functions
    complexity_delta: int             # Positive = increase, Negative = refactoring

    # Cognitive complexity (understandability metric - nesting-aware)
    cognitive_complexity_before: Optional[int]  # None for ADDED functions
    cognitive_complexity_after: Optional[int]   # None for DELETED functions
    cognitive_complexity_delta: int             # Positive = harder to understand

    churn: int                        # Number of times this function has changed
    hotspot_score: float              # complexity × churn (Tornhill's hotspot formula)
    last_author: str
    last_modified: datetime
    lines_changed: int
    review_time_minutes: int


@dataclass
class DeltaDiff:
    """
    Results of delta analysis between two git commits.

    Contains all function-level changes detected, categorized by type,
    plus aggregate metrics for review time estimation.
    """

    base_commit: str
    target_commit: str
    added_functions: List[FunctionChange]
    modified_functions: List[FunctionChange]
    deleted_functions: List[FunctionChange]
    total_complexity_delta: int
    total_review_time_minutes: int
    critical_changes: List[FunctionChange]  # Top 10 by hotspot score
    refactorings: List[FunctionChange]      # Functions with negative complexity delta
