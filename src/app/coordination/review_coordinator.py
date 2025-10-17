"""
Review Coordinator Module

Handles code review strategy coordination and file output.
Separates review-specific logic from main application flow.
"""
from typing import List, Tuple, Dict, Any, Optional


class ReviewCoordinator:
    """
    Coordinates code review strategy generation and output.

    Responsibilities:
    - Generate code review strategies
    - Handle git branch comparison
    - Write review strategies to files
    """

    @staticmethod
    def generate_review_strategy(
        analyzer,
        config,
        hotspots: List[Dict[str, Any]]
    ) -> Tuple[Optional[List[str]], Optional[str]]:
        """
        Generate code review strategy from analyzer.

        Args:
            analyzer: Analyzer instance with KPI results
            config: Application configuration
            hotspots: List of hotspot dictionaries

        Returns:
            Tuple of (review_list, error_message)
        """
        if not config.repo.generate_review_strategy:
            return None, None

        try:
            review_list = analyzer.get_code_review_strategy(
                diff_branch=config.repo.review_diff_branch
            )
            return review_list, None
        except Exception as e:
            error_msg = (
                f"Failed to generate code review strategy: {e}\n"
                f"Ensure git branch '{config.repo.review_diff_branch}' exists and "
                "diff can be generated."
            )
            return None, error_msg

    @staticmethod
    def format_review_strategy(review_list: List[str]) -> str:
        """
        Format review strategy as human-readable text.

        Args:
            review_list: List of file paths for review

        Returns:
            Formatted text representation
        """
        if not review_list:
            return "No files changed relative to comparison branch."

        lines = ["=== CODE REVIEW STRATEGY ==="]
        lines.append("Files changed (prioritized by hotspot/complexity):")
        for file_path in review_list:
            lines.append(f"  - {file_path}")
        return "\n".join(lines)

    @staticmethod
    def write_review_file(review_list: List[str], output_path: str):
        """
        Write code review strategy to text file.

        Args:
            review_list: List of file paths for review
            output_path: Path to output file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(ReviewCoordinator.format_review_strategy(review_list))
            print(f"\n✅ Code review strategy written to: {output_path}")
        except Exception as e:
            print(f"\n⚠️  Failed to write code review strategy file: {e}")

    @staticmethod
    def print_review_strategy(review_list: List[str]):
        """
        Print code review strategy to console.

        Args:
            review_list: List of file paths for review
        """
        print("\n" + ReviewCoordinator.format_review_strategy(review_list))

    @staticmethod
    def print_error(error_message: str):
        """
        Print error message for failed review generation.

        Args:
            error_message: Error message to display
        """
        print(f"\n⚠️  {error_message}")
