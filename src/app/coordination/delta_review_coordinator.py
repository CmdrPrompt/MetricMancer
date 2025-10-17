"""
Delta Review Coordinator Module

Handles delta-based code review coordination and file output.
Separates delta review logic from main application flow following Open/Closed Principle.
"""
import os
from typing import Optional, Callable

from src.analysis.delta import DeltaAnalyzer, DeltaReviewStrategyFormat, DeltaDiff


class DeltaReviewCoordinator:
    """
    Coordinates delta-based code review generation and output.

    Responsibilities:
    - Generate function-level delta analysis between branches
    - Format delta review reports
    - Write delta review strategies to files
    - Display delta review summaries

    Follows the same pattern as ReviewCoordinator to maintain architectural consistency.
    """

    @staticmethod
    def generate_delta_review(
        repo_path: str,
        config,
        analyzer_factory: Optional[Callable[[str], DeltaAnalyzer]] = None
    ) -> Optional[DeltaDiff]:
        """
        Generate delta review analysis from repository.

        Args:
            repo_path: Path to git repository
            config: Application configuration with delta review settings
            analyzer_factory: Optional factory function for creating DeltaAnalyzer
                            (used for dependency injection in tests)

        Returns:
            DeltaDiff object with function-level changes, or None if disabled or error
        """
        if not config.delta_review:
            return None

        try:
            # Create analyzer (allow injection for testing)
            if analyzer_factory is None:
                analyzer = DeltaAnalyzer(repo_path=repo_path)
            else:
                analyzer = analyzer_factory(repo_path)

            # Analyze branch delta
            delta_diff = analyzer.analyze_branch_delta(
                base_branch=config.delta_base_branch,
                target_branch=config.delta_target_branch
            )

            return delta_diff

        except Exception:
            # Silently return None on error - caller can check for None
            return None

    @staticmethod
    def format_delta_review(delta_diff: DeltaDiff) -> str:
        """
        Format delta review as markdown report.

        Args:
            delta_diff: DeltaDiff object with function-level changes

        Returns:
            Markdown-formatted review strategy report
        """
        formatter = DeltaReviewStrategyFormat()
        return formatter.format(delta_diff)

    @staticmethod
    def write_delta_review_file(delta_diff: DeltaDiff, output_path: str):
        """
        Write delta review report to file.

        Args:
            delta_diff: DeltaDiff object with function-level changes
            output_path: Path to output file
        """
        try:
            report = DeltaReviewCoordinator.format_delta_review(delta_diff)

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)

            print(f"\n✅ Delta review report generated: {output_path}")

        except Exception as e:
            print(f"\n⚠️  Failed to write delta review file: {e}")

    @staticmethod
    def print_delta_summary(delta_diff: DeltaDiff):
        """
        Print delta review summary to console.

        Args:
            delta_diff: DeltaDiff object with function-level changes
        """
        total_functions = (
            len(delta_diff.added_functions) +
            len(delta_diff.modified_functions) +
            len(delta_diff.deleted_functions)
        )

        print(f"\n📊 Summary:")
        print(f"  - Functions changed: {total_functions}")
        print(f"  - Complexity delta: {delta_diff.total_complexity_delta:+d}")
        print(f"  - Estimated review time: {delta_diff.total_review_time_minutes} minutes")

        if delta_diff.critical_changes:
            print(f"  - Critical changes: {len(delta_diff.critical_changes)}")

        if delta_diff.refactorings:
            print(f"  - Refactorings: {len(delta_diff.refactorings)}")
