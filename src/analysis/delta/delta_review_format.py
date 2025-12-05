"""
Delta review strategy formatter.

Generates markdown reports for function-level code review guidance,
following Adam Tornhill's "Your Code as a Crime Scene" methodology.
"""

from typing import List
from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType


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
        total_functions = (
            len(delta.added_functions) +
            len(delta.modified_functions) +
            len(delta.deleted_functions)
        )

        # Calculate cognitive complexity delta
        total_cognitive_delta = sum(
            f.cognitive_complexity_delta for f in (delta.added_functions + delta.modified_functions + delta.deleted_functions)
        )

        lines = [
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

        # Highlight if complexity increased significantly
        if delta.total_complexity_delta > 20:
            lines.append("⚠️  **Warning:** Significant cyclomatic complexity increase detected!")
            lines.append("")
        elif delta.total_complexity_delta < -20:
            lines.append("✅ **Good:** Significant cyclomatic complexity reduction!")
            lines.append("")

        if total_cognitive_delta > 15:
            lines.append("⚠️  **Warning:** Significant cognitive complexity increase detected!")
            lines.append("         Code is becoming harder to understand.")
            lines.append("")
        elif total_cognitive_delta < -15:
            lines.append("✅ **Good:** Significant cognitive complexity reduction!")
            lines.append("         Code is becoming easier to understand.")
            lines.append("")

        return "\n".join(lines)

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
        lines = [
            "## ➕ New Functions",
            "",
        ]

        # Show high-complexity new functions first
        high_complexity = [f for f in delta.added_functions if f.complexity_after and f.complexity_after > 10]
        normal = [f for f in delta.added_functions if f.complexity_after and f.complexity_after <= 10]

        if high_complexity:
            lines.append("### High Complexity (>10)")
            lines.append("")
            for change in high_complexity:
                lines.extend(self._format_function_change(change))

        if normal:
            if high_complexity:
                lines.append("")
            lines.append("### Standard Complexity")
            lines.append("")
            for change in normal:
                lines.extend(self._format_function_change(change, brief=True))

        return "\n".join(lines)

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
        lines = []

        # Icon based on change type and complexity
        if change.change_type == ChangeType.ADDED:
            icon = "➕"
        elif change.change_type == ChangeType.DELETED:
            icon = "🗑️ "
        elif change.complexity_delta > 0:
            icon = "🔴" if change.complexity_delta > 10 else "🟡"
        else:
            icon = "🟢"

        if brief:
            # Brief format - one line
            complexity_info = ""
            if change.complexity_before is not None and change.complexity_after is not None:
                complexity_info = f" ({change.complexity_before} → {change.complexity_after})"
            elif change.complexity_after is not None:
                complexity_info = f" (complexity: {change.complexity_after})"

            lines.append(
                f"- {icon} `{change.function_name}()` in {change.file_path}{complexity_info}"
            )
        else:
            # Detailed format
            lines.append(f"### {icon} `{change.function_name}()`")
            lines.append("")
            lines.append(f"**File:** {change.file_path} (lines {change.start_line}-{change.end_line})")
            lines.append("")

            # Cyclomatic Complexity info
            if change.complexity_before is not None and change.complexity_after is not None:
                delta_str = f"{change.complexity_delta:+d}"
                lines.append(
                    f"- **Cyclomatic Complexity:** {change.complexity_before} → {change.complexity_after} "
                    f"({delta_str}) {icon}"
                )
            elif change.complexity_after is not None:
                lines.append(f"- **Cyclomatic Complexity:** {change.complexity_after}")
            elif change.complexity_before is not None:
                lines.append(f"- **Cyclomatic Complexity:** {change.complexity_before} (deleted)")

            # Cognitive Complexity info
            if change.cognitive_complexity_before is not None and change.cognitive_complexity_after is not None:
                cog_delta_str = f"{change.cognitive_complexity_delta:+d}"
                cog_icon = "🟢" if change.cognitive_complexity_delta <= 0 else ("🟡" if change.cognitive_complexity_delta <= 5 else "🔴")
                lines.append(
                    f"- **Cognitive Complexity:** {change.cognitive_complexity_before} → {change.cognitive_complexity_after} "
                    f"({cog_delta_str}) {cog_icon}"
                )
            elif change.cognitive_complexity_after is not None:
                lines.append(f"- **Cognitive Complexity:** {change.cognitive_complexity_after}")
            elif change.cognitive_complexity_before is not None:
                lines.append(f"- **Cognitive Complexity:** {change.cognitive_complexity_before} (deleted)")

            # Additional metrics
            lines.append(f"- **Hotspot Score:** {change.hotspot_score:.0f}")
            lines.append(f"- **Review Time:** ~{change.review_time_minutes} minutes")
            lines.append("")

            # Review guidance
            if include_guidance:
                lines.extend(self._format_review_guidance(change))

        return lines

    def _format_review_guidance(self, change: FunctionChange) -> List[str]:
        """Generate review guidance checklist for a function change."""
        lines = ["**Review Focus:**", ""]

        if change.complexity_delta > 10:
            # High complexity increase
            lines.append("- [ ] Review all new branches and conditional logic")
            lines.append("- [ ] Verify error handling for edge cases")
            lines.append("- [ ] Consider if function should be decomposed")
            lines.append("- [ ] Validate test coverage for new complexity")
            lines.append("- [ ] Check for potential simplification opportunities")

        elif change.complexity_delta > 5:
            # Moderate complexity increase
            lines.append("- [ ] Review new branches added")
            lines.append("- [ ] Verify error handling")
            lines.append("- [ ] Check test coverage")

        elif change.complexity_delta < 0:
            # Refactoring
            lines.append("- [ ] Verify refactoring maintains behavior")
            lines.append("- [ ] Check test coverage is still adequate")
            lines.append("- [ ] Validate performance hasn't degraded")

        elif change.change_type == ChangeType.ADDED:
            # New function
            lines.append("- [ ] Verify function has clear purpose")
            lines.append("- [ ] Check error handling")
            lines.append("- [ ] Validate test coverage")
            if change.complexity_after and change.complexity_after > 15:
                lines.append("- [ ] Consider simplification for high complexity")

        else:
            # General review
            lines.append("- [ ] Review changes for correctness")
            lines.append("- [ ] Verify test coverage")

        lines.append("")
        return lines

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
