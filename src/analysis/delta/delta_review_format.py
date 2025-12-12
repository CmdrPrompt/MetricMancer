"""
Delta review strategy formatter.

Generates markdown reports for function-level code review guidance,
following Adam Tornhill's "Your Code as a Crime Scene" methodology.
"""

from typing import List, Dict, Optional
from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType

# Complexity thresholds
COMPLEXITY_WARNING_THRESHOLD = 20
COMPLEXITY_GOOD_THRESHOLD = -20
COGNITIVE_WARNING_THRESHOLD = 15
COGNITIVE_GOOD_THRESHOLD = -15
HIGH_COMPLEXITY_THRESHOLD = 10
MODERATE_COMPLEXITY_DELTA = 5

# Icons for different change types and severity
ICONS = {
    'added': '➕',
    'deleted': '🗑️ ',
    'increase_high': '🔴',
    'increase_moderate': '🟡',
    'decrease': '🟢',
}


class DeltaReviewStrategyFormat:
    """
    Format delta analysis results into actionable review strategies.

    Generates markdown reports with:
    - Overview of changes
    - Critical changes (high hotspot scores)
    - Refactorings (complexity improvements)
    - Review guidance and checklists
    """

    def format(self, delta: DeltaDiff) -> str:
        """
        Format a DeltaDiff into a markdown review strategy report.

        Args:
            delta: DeltaDiff object with function-level changes

        Returns:
            Markdown-formatted review strategy report
        """
        sections = []

        # Header
        sections.append(self._format_header(delta))

        # Overview
        sections.append(self._format_overview(delta))

        # Critical Changes
        if delta.critical_changes:
            sections.append(self._format_critical_changes(delta))

        # Refactorings
        if delta.refactorings:
            sections.append(self._format_refactorings(delta))

        # Added Functions
        if delta.added_functions:
            sections.append(self._format_added_functions(delta))

        # Modified Functions Summary
        if delta.modified_functions:
            sections.append(self._format_modified_summary(delta))

        # Deleted Functions
        if delta.deleted_functions:
            sections.append(self._format_deleted_functions(delta))

        # No changes message
        if not (delta.added_functions or delta.modified_functions or delta.deleted_functions):
            sections.append("\n**No changes detected** - branches are identical.\n")

        return "\n\n".join(sections)

    def _format_header(self, delta: DeltaDiff) -> str:
        """Format report header."""
        return f"# Delta Review Strategy - {delta.target_commit[:7]}"

    def _format_overview(self, delta: DeltaDiff) -> str:
        """Format overview section."""
        total_functions = self._count_total_functions(delta)
        total_cognitive_delta = self._calculate_cognitive_delta(delta)

        lines = self._build_overview_header(delta, total_functions, total_cognitive_delta)
        lines.extend(self._build_complexity_warnings(delta.total_complexity_delta, total_cognitive_delta))

        return "\n".join(lines)

    def _count_total_functions(self, delta: DeltaDiff) -> int:
        """Count total functions changed."""
        return len(delta.added_functions) + len(delta.modified_functions) + len(delta.deleted_functions)

    def _calculate_cognitive_delta(self, delta: DeltaDiff) -> int:
        """Calculate total cognitive complexity delta."""
        all_changes = delta.added_functions + delta.modified_functions + delta.deleted_functions
        return sum(f.cognitive_complexity_delta for f in all_changes)

    def _build_overview_header(self, delta: DeltaDiff, total_functions: int, total_cognitive_delta: int) -> List[str]:
        """Build overview header lines."""
        return [
            "## Overview",
            "",
            f"**Commits:** `{delta.base_commit[:7]}` → `{delta.target_commit[:7]}`",
            "",
            "### Changes Summary",
            "",
            f"- **Functions Changed:** {total_functions}",
            f"  - Added: {len(delta.added_functions)}",
            f"  - Modified: {len(delta.modified_functions)}",
            f"  - Deleted: {len(delta.deleted_functions)}",
            "",
            f"- **Cyclomatic Complexity Delta:** {delta.total_complexity_delta:+d}",
            f"- **Cognitive Complexity Delta:** {total_cognitive_delta:+d}",
            f"- **Estimated Review Time:** {self._format_time(delta.total_review_time_minutes)}",
            "",
        ]

    def _build_complexity_warnings(self, cc_delta: int, cog_delta: int) -> List[str]:
        """Build complexity warning messages."""
        lines = []
        lines.extend(self._get_cyclomatic_warning(cc_delta))
        lines.extend(self._get_cognitive_warning(cog_delta))
        return lines

    def _get_cyclomatic_warning(self, delta: int) -> List[str]:
        """Get cyclomatic complexity warning message."""
        if delta > COMPLEXITY_WARNING_THRESHOLD:
            return ["⚠️  **Warning:** Significant cyclomatic complexity increase detected!", ""]
        if delta < COMPLEXITY_GOOD_THRESHOLD:
            return ["✅ **Good:** Significant cyclomatic complexity reduction!", ""]
        return []

    def _get_cognitive_warning(self, delta: int) -> List[str]:
        """Get cognitive complexity warning message."""
        if delta > COGNITIVE_WARNING_THRESHOLD:
            return [
                "⚠️  **Warning:** Significant cognitive complexity increase detected!",
                "         Code is becoming harder to understand.",
                ""
            ]
        if delta < COGNITIVE_GOOD_THRESHOLD:
            return [
                "✅ **Good:** Significant cognitive complexity reduction!",
                "         Code is becoming easier to understand.",
                ""
            ]
        return []

    def _format_critical_changes(self, delta: DeltaDiff) -> str:
        """Format critical changes section (high hotspot scores)."""
        lines = [
            "## 🔥 Critical Changes (Complexity Hotspots)",
            "",
            "These functions have the highest risk due to complexity × churn.",
            "Focus your review effort here.",
            "",
        ]

        for change in delta.critical_changes[:10]:  # Top 10
            lines.extend(self._format_function_change(change, include_guidance=True))

        return "\n".join(lines)

    def _format_refactorings(self, delta: DeltaDiff) -> str:
        """Format refactorings section (complexity improvements)."""
        lines = [
            "## ✨ Refactorings (Complexity Improvements)",
            "",
            "These functions became simpler. Verify behavior is preserved.",
            "",
        ]

        for change in delta.refactorings:
            lines.extend(self._format_function_change(change, include_guidance=True))

        return "\n".join(lines)

    def _format_added_functions(self, delta: DeltaDiff) -> str:
        """Format added functions section."""
        lines = ["## ➕ New Functions", ""]

        high_complexity, normal = self._split_by_complexity(delta.added_functions)

        if high_complexity:
            lines.extend(self._format_high_complexity_section(high_complexity))
        if normal:
            lines.extend(self._format_normal_complexity_section(normal, bool(high_complexity)))

        return "\n".join(lines)

    def _split_by_complexity(self, functions: List[FunctionChange]) -> tuple:
        """Split functions into high and normal complexity groups."""
        high = [f for f in functions if f.complexity_after and f.complexity_after > HIGH_COMPLEXITY_THRESHOLD]
        normal = [f for f in functions if f.complexity_after and f.complexity_after <= HIGH_COMPLEXITY_THRESHOLD]
        return high, normal

    def _format_high_complexity_section(self, functions: List[FunctionChange]) -> List[str]:
        """Format high complexity functions section."""
        lines = ["### High Complexity (>10)", ""]
        for change in functions:
            lines.extend(self._format_function_change(change))
        return lines

    def _format_normal_complexity_section(self, functions: List[FunctionChange], has_high: bool) -> List[str]:
        """Format normal complexity functions section."""
        lines = []
        if has_high:
            lines.append("")
        lines.extend(["### Standard Complexity", ""])
        for change in functions:
            lines.extend(self._format_function_change(change, brief=True))
        return lines

    def _format_modified_summary(self, delta: DeltaDiff) -> str:
        """Format modified functions summary."""
        # Only show non-critical modified functions
        non_critical = [f for f in delta.modified_functions if f not in delta.critical_changes]

        if not non_critical:
            return ""

        lines = [
            "## 📝 Other Modified Functions",
            "",
        ]

        for change in non_critical:
            lines.extend(self._format_function_change(change, brief=True))

        return "\n".join(lines)

    def _format_deleted_functions(self, delta: DeltaDiff) -> str:
        """Format deleted functions section."""
        lines = [
            "## 🗑️  Deleted Functions",
            "",
        ]

        for change in delta.deleted_functions:
            lines.append(f"- `{change.function_name}()` in {change.file_path}")
            if change.complexity_before and change.complexity_before > 10:
                lines.append(f"  - Complexity: {change.complexity_before} (was complex)")

        lines.append("")
        return "\n".join(lines)

    def _format_function_change(
        self,
        change: FunctionChange,
        include_guidance: bool = False,
        brief: bool = False
    ) -> List[str]:
        """
        Format a single function change.

        Args:
            change: FunctionChange to format
            include_guidance: Include review guidance checklist
            brief: Use brief format (one line)

        Returns:
            List of formatted lines
        """
        icon = self._get_change_icon(change)

        if brief:
            return self._format_brief_change(change, icon)
        return self._format_detailed_change(change, icon, include_guidance)

    def _get_change_icon(self, change: FunctionChange) -> str:
        """Get icon based on change type and complexity delta."""
        if change.change_type == ChangeType.ADDED:
            return ICONS['added']
        if change.change_type == ChangeType.DELETED:
            return ICONS['deleted']
        if change.complexity_delta > HIGH_COMPLEXITY_THRESHOLD:
            return ICONS['increase_high']
        if change.complexity_delta > 0:
            return ICONS['increase_moderate']
        return ICONS['decrease']

    def _format_brief_change(self, change: FunctionChange, icon: str) -> List[str]:
        """Format a brief one-line change description."""
        complexity_info = self._get_brief_complexity_info(change)
        return [f"- {icon} `{change.function_name}()` in {change.file_path}{complexity_info}"]

    def _get_brief_complexity_info(self, change: FunctionChange) -> str:
        """Get brief complexity info string."""
        if change.complexity_before is not None and change.complexity_after is not None:
            return f" ({change.complexity_before} → {change.complexity_after})"
        if change.complexity_after is not None:
            return f" (complexity: {change.complexity_after})"
        return ""

    def _format_detailed_change(self, change: FunctionChange, icon: str, include_guidance: bool) -> List[str]:
        """Format a detailed change description."""
        lines = [
            f"### {icon} `{change.function_name}()`",
            "",
            f"**File:** {change.file_path} (lines {change.start_line}-{change.end_line})",
            ""
        ]
        lines.append(self._format_cyclomatic_complexity(change, icon))
        lines.append(self._format_cognitive_complexity(change))
        lines.append(f"- **Hotspot Score:** {change.hotspot_score:.0f}")
        lines.append(f"- **Review Time:** ~{change.review_time_minutes} minutes")
        lines.append("")

        if include_guidance:
            lines.extend(self._format_review_guidance(change))

        return lines

    def _format_cyclomatic_complexity(self, change: FunctionChange, icon: str) -> str:
        """Format cyclomatic complexity line."""
        if change.complexity_before is not None and change.complexity_after is not None:
            delta_str = f"{change.complexity_delta:+d}"
            return (f"- **Cyclomatic Complexity:** {change.complexity_before} → {change.complexity_after} "
                    f"({delta_str}) {icon}")
        if change.complexity_after is not None:
            return f"- **Cyclomatic Complexity:** {change.complexity_after}"
        if change.complexity_before is not None:
            return f"- **Cyclomatic Complexity:** {change.complexity_before} (deleted)"
        return "- **Cyclomatic Complexity:** N/A"

    def _format_cognitive_complexity(self, change: FunctionChange) -> str:
        """Format cognitive complexity line."""
        if change.cognitive_complexity_before is not None and change.cognitive_complexity_after is not None:
            cog_delta_str = f"{change.cognitive_complexity_delta:+d}"
            cog_icon = self._get_cognitive_icon(change.cognitive_complexity_delta)
            return (f"- **Cognitive Complexity:** {change.cognitive_complexity_before} → "
                    f"{change.cognitive_complexity_after} ({cog_delta_str}) {cog_icon}")
        if change.cognitive_complexity_after is not None:
            return f"- **Cognitive Complexity:** {change.cognitive_complexity_after}"
        if change.cognitive_complexity_before is not None:
            return f"- **Cognitive Complexity:** {change.cognitive_complexity_before} (deleted)"
        return "- **Cognitive Complexity:** N/A"

    def _get_cognitive_icon(self, delta: int) -> str:
        """Get icon for cognitive complexity delta."""
        if delta <= 0:
            return ICONS['decrease']
        if delta <= MODERATE_COMPLEXITY_DELTA:
            return ICONS['increase_moderate']
        return ICONS['increase_high']

    def _format_review_guidance(self, change: FunctionChange) -> List[str]:
        """Generate review guidance checklist for a function change."""
        lines = ["**Review Focus:**", ""]
        lines.extend(self._get_review_checklist(change))
        lines.append("")
        return lines

    def _get_review_checklist(self, change: FunctionChange) -> List[str]:
        """Get appropriate review checklist based on change characteristics."""
        if change.complexity_delta > HIGH_COMPLEXITY_THRESHOLD:
            return self._high_complexity_checklist()
        if change.complexity_delta > MODERATE_COMPLEXITY_DELTA:
            return self._moderate_complexity_checklist()
        if change.complexity_delta < 0:
            return self._refactoring_checklist()
        if change.change_type == ChangeType.ADDED:
            return self._new_function_checklist(change)
        return self._general_checklist()

    def _high_complexity_checklist(self) -> List[str]:
        """Checklist for high complexity increase."""
        return [
            "- [ ] Review all new branches and conditional logic",
            "- [ ] Verify error handling for edge cases",
            "- [ ] Consider if function should be decomposed",
            "- [ ] Validate test coverage for new complexity",
            "- [ ] Check for potential simplification opportunities"
        ]

    def _moderate_complexity_checklist(self) -> List[str]:
        """Checklist for moderate complexity increase."""
        return [
            "- [ ] Review new branches added",
            "- [ ] Verify error handling",
            "- [ ] Check test coverage"
        ]

    def _refactoring_checklist(self) -> List[str]:
        """Checklist for refactoring (complexity decrease)."""
        return [
            "- [ ] Verify refactoring maintains behavior",
            "- [ ] Check test coverage is still adequate",
            "- [ ] Validate performance hasn't degraded"
        ]

    def _new_function_checklist(self, change: FunctionChange) -> List[str]:
        """Checklist for new functions."""
        checklist = [
            "- [ ] Verify function has clear purpose",
            "- [ ] Check error handling",
            "- [ ] Validate test coverage"
        ]
        if change.complexity_after and change.complexity_after > 15:
            checklist.append("- [ ] Consider simplification for high complexity")
        return checklist

    def _general_checklist(self) -> List[str]:
        """General review checklist."""
        return [
            "- [ ] Review changes for correctness",
            "- [ ] Verify test coverage"
        ]

    def _format_time(self, minutes: int) -> str:
        """Format review time in human-readable format."""
        if minutes < 60:
            return f"{minutes} minutes"
        else:
            hours = minutes // 60
            mins = minutes % 60
            if mins == 0:
                return f"{hours} hour{'s' if hours > 1 else ''}"
            else:
                return f"{hours}h {mins}m"
