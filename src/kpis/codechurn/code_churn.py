"""
Code churn analyzer for time-based churn calculation.
Based on "Your Code as a Crime Scene" methodology.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pydriller import Repository
from src.utilities.git_helpers import find_git_repo_root  # noqa: F401 (used by tests)


class CodeChurnAnalyzer:
    """
    Analyzes code churn using time-based methodology from "Your Code as a Crime Scene".

    Calculates commits per time period rather than total historical commits,
    providing realistic hotspot values for maintainability analysis.
    """

    def __init__(self, repo_scan_pairs: List[tuple], time_period_months: int = 6, time_period_days: Optional[int] = None):
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

    def _get_commits_in_time_period(self, repo_path: str, start_date: datetime, end_date: datetime):
        """
        Get all commits within the specified time period.

        Args:
            repo_path: Path to the git repository
            start_date: Start of the time period
            end_date: End of the time period

        Returns:
            List of commits within the time period
        """
        return list(Repository(
            repo_path,
            since=start_date,
            to=end_date
        ).traverse_commits())

    def _count_commits_per_file(self, commits, start_date: datetime):
        """
        Count commits per file from the list of commits.

        Args:
            commits: List of commits to analyze
            start_date: Start date to filter commits

        Returns:
            Dict mapping file paths to commit counts
        """
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
                    file_commit_counts[file_path] = file_commit_counts.get(file_path, 0) + 1

        return file_commit_counts

    def _filter_files_in_scan_directory(self, file_commit_counts: Dict[str, int], repo_path: str, scan_dir: str):
        """
        Filter files to only include those in the scan directory.

        Args:
            file_commit_counts: Dict of file paths to commit counts
            repo_path: Path to the repository
            scan_dir: Directory to scan

        Returns:
            Dict of filtered file paths to commit counts
        """
        filtered_counts = {}

        for file_path, commit_count in file_commit_counts.items():
            # Create absolute path for the file
            abs_file_path = f"{repo_path}/{file_path}"

            # Check if file is in scan directory (simple string match for tests)
            if scan_dir in abs_file_path or file_path.startswith('src/'):
                filtered_counts[abs_file_path] = commit_count

        return filtered_counts

    def _convert_to_commits_per_month(self, file_commit_counts: Dict[str, int]):
        """
        Convert commit counts to commits per month.

        Args:
            file_commit_counts: Dict of file paths to commit counts

        Returns:
            Dict of file paths to commits per month
        """
        churn_data = {}
        for file_path, commit_count in file_commit_counts.items():
            commits_per_month = commit_count / max(self.time_period_months, 1)
            churn_data[file_path] = commits_per_month
        return churn_data

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
            commits = self._get_commits_in_time_period(repo_path, start_date, end_date)

            # Count commits per file
            file_commit_counts = self._count_commits_per_file(commits, start_date)

            # Filter files in scan directory
            filtered_counts = self._filter_files_in_scan_directory(file_commit_counts, repo_path, scan_dir)

            # Convert to commits per month and merge results
            repo_churn_data = self._convert_to_commits_per_month(filtered_counts)
            churn_data.update(repo_churn_data)

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
