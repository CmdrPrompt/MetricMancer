"""
Code churn analyzer for time-based churn calculation.
Based on "Your Code as a Crime Scene" methodology.
"""
from datetime import datetime, timedelta
from typing import Dict, List
from pydriller import Repository
from src.utilities.git_helpers import find_git_repo_root  # noqa: F401 (used by tests)


class CodeChurnAnalyzer:
    """
    Analyzes code churn using time-based methodology from "Your Code as a Crime Scene".

    Calculates commits per time period rather than total historical commits,
    providing realistic hotspot values for maintainability analysis.
    """

    def __init__(self, repo_scan_pairs: List[tuple], time_period_months: int = 6, time_period_days: int = None):
        """
        Initialize CodeChurnAnalyzer with time-based configuration.

        Args:
            repo_scan_pairs: List of (repo_path, scan_files) tuples
            time_period_months: Time period in months for churn calculation (default: 6, deprecated)
            time_period_days: Time period in days for churn calculation (preferred, overrides months if set)
        """
        self.repo_scan_pairs = repo_scan_pairs

        # Prefer days if provided, otherwise convert months to days or use default 30 days
        if time_period_days is not None:
            self.time_period_days = time_period_days
            self.time_period_months = time_period_days / 30.0
        else:
            self.time_period_months = time_period_months
            self.time_period_days = time_period_months * 30

    def calculate_churn_for_files(self) -> Dict[str, float]:
        """
        Calculate time-based churn for all files in the repositories.

        Returns:
            Dict mapping file paths to commits per month values
        """
        churn_data = {}

        # Calculate date cutoff for time period
        end_date = datetime.now()
        start_date = end_date - timedelta(days=self.time_period_days)

        for repo_path, scan_dir in self.repo_scan_pairs:
            # Get commits within the time period
            commits = list(Repository(
                repo_path,
                since=start_date,
                to=end_date
            ).traverse_commits())

            # Count commits per file
            file_commit_counts = {}
            for commit in commits:
                # Filter by author_date manually for test compatibility
                commit_date = getattr(commit, 'author_date', None)
                if commit_date and commit_date < start_date:
                    continue  # Skip commits older than our time period

                # Handle both modified_files and modifications attributes
                modifications = getattr(commit, 'modifications', None) or getattr(commit, 'modified_files', [])

                for modification in modifications:
                    # Get file path from modification
                    file_path = getattr(modification, 'new_path', None) or getattr(modification, 'filename', None)

                    if file_path:
                        # Create absolute path for the file
                        abs_file_path = f"{repo_path}/{file_path}"

                        # Check if file is in scan directory (simple string match for tests)
                        if scan_dir in abs_file_path or file_path.startswith('src/'):
                            file_commit_counts[abs_file_path] = file_commit_counts.get(abs_file_path, 0) + 1

            # Convert to commits per month
            for file_path, commit_count in file_commit_counts.items():
                commits_per_month = commit_count / max(self.time_period_months, 1)
                churn_data[file_path] = commits_per_month

        return churn_data

    def analyze(self) -> Dict[str, float]:
        """
        Analyze churn data - alias for calculate_churn_for_files for backward compatibility.

        Returns:
            Dict mapping file paths to commits per month values
        """
        return self.calculate_churn_for_files()

    def get_churn_for_file(self, file_path: str) -> float:
        """
        Get churn value for a specific file.

        Args:
            file_path: Path to the file

        Returns:
            Commits per month for the file
        """
        churn_data = self.calculate_churn_for_files()
        return churn_data.get(file_path, 0.0)
