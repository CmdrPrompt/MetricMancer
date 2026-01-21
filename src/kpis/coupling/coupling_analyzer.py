"""
Coupling Analyzer - Temporal coupling detection based on commit history.

This module implements temporal coupling analysis to identify files that
frequently change together, revealing hidden architectural dependencies.

Based on Adam Tornhill's methodology from "Your Code as a Crime Scene".
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set
from collections import defaultdict
from itertools import combinations

from src.utilities.git_helpers import get_commit_history


@dataclass
class CouplingData:
    """
    Represents coupling relationship between two files.

    Attributes:
        file_a: First file path
        file_b: Second file path
        coupling_score: Coupling strength (0.0 - 1.0)
        commits_together: Number of commits where both files changed
        total_commits_a: Total commits affecting file_a
        total_commits_b: Total commits affecting file_b
        commits: List of commit hashes where both files changed together
    """
    file_a: str
    file_b: str
    coupling_score: float
    commits_together: int
    total_commits_a: int
    total_commits_b: int
    commits: List[str] = field(default_factory=list)

    @property
    def strength(self) -> str:
        """
        Return coupling strength category based on score.

        Returns:
            VERY_HIGH (>=0.7), HIGH (>=0.5), MEDIUM (>=0.3), or LOW (<0.3)
        """
        if self.coupling_score >= 0.7:
            return "VERY_HIGH"
        elif self.coupling_score >= 0.5:
            return "HIGH"
        elif self.coupling_score >= 0.3:
            return "MEDIUM"
        else:
            return "LOW"


class CouplingAnalyzer:
    """
    Analyzes temporal coupling between files based on commit history.

    Algorithm:
        1. Extract commit history for time period
        2. For each commit, identify all file pairs
        3. Count co-changes for each pair
        4. Calculate coupling score = co_changes / min(changes_a, changes_b)

    Usage:
        >>> analyzer = CouplingAnalyzer(time_period_days=90)
        >>> matrix = analyzer.calculate_coupling_matrix("/path/to/repo")
        >>> coupled_files = analyzer.get_coupled_files("/path/to/repo", "src/file.py")
    """

    def __init__(
        self,
        time_period_days: int = 90,
        min_coupling_threshold: float = 0.3,
        min_commits: int = 3
    ):
        """
        Initialize coupling analyzer.

        Args:
            time_period_days: Number of days of commit history to analyze
            min_coupling_threshold: Minimum coupling score to include in results (0.0-1.0)
            min_commits: Minimum number of co-changes required to report coupling
        """
        self.time_period_days = time_period_days
        self.min_coupling_threshold = min_coupling_threshold
        self.min_commits = min_commits

        # Cache for calculated coupling matrices
        self._coupling_matrix_cache: Dict[str, Dict[Tuple[str, str], CouplingData]] = {}

    def calculate_coupling_matrix(
        self,
        repo_root: str,
        force_recalculate: bool = False
    ) -> Dict[Tuple[str, str], CouplingData]:
        """
        Calculate coupling between all file pairs in repository.

        Args:
            repo_root: Root directory of git repository
            force_recalculate: If True, bypass cache and recalculate

        Returns:
            Dictionary mapping file pairs to coupling data.
            Key: (file_a, file_b) where file_a < file_b (sorted)
            Value: CouplingData instance

            Only includes pairs with:
            - coupling_score >= min_coupling_threshold
            - commits_together >= min_commits

        Example:
            >>> matrix = analyzer.calculate_coupling_matrix("/my/repo")
            >>> coupling = matrix[("src/a.py", "src/b.py")]
            >>> print(f"Score: {coupling.coupling_score:.2f}")
            Score: 0.85
        """
        repo_root = os.path.abspath(repo_root)

        # Check cache
        if not force_recalculate and repo_root in self._coupling_matrix_cache:
            return self._coupling_matrix_cache[repo_root]

        # Get commit history
        since_date = f"{self.time_period_days} days ago"
        commits = get_commit_history(repo_root, since_date=since_date)

        if not commits:
            return {}

        # Track file changes
        file_commits: Dict[str, Set[str]] = defaultdict(set)
        pair_commits: Dict[Tuple[str, str], Set[str]] = defaultdict(set)

        # Process each commit
        for commit in commits:
            commit_hash = commit['commit_hash']
            changed_files = commit['changed_files']

            # Track which commits each file appears in
            for file_path in changed_files:
                file_commits[file_path].add(commit_hash)

            # Track file pairs that change together
            if len(changed_files) >= 2:
                # Get all pairs of files in this commit
                for file_a, file_b in combinations(sorted(changed_files), 2):
                    pair_key = (file_a, file_b)
                    pair_commits[pair_key].add(commit_hash)

        # Calculate coupling scores
        coupling_matrix = {}

        for (file_a, file_b), commit_set in pair_commits.items():
            commits_together = len(commit_set)

            # Skip if below minimum commit threshold
            if commits_together < self.min_commits:
                continue

            total_commits_a = len(file_commits[file_a])
            total_commits_b = len(file_commits[file_b])

            # Calculate coupling score (normalized by minimum)
            # This gives a score indicating how often the less-changed file
            # changes together with the other file
            min_commits = min(total_commits_a, total_commits_b)
            coupling_score = commits_together / min_commits if min_commits > 0 else 0.0

            # Skip if below threshold
            if coupling_score < self.min_coupling_threshold:
                continue

            coupling_data = CouplingData(
                file_a=file_a,
                file_b=file_b,
                coupling_score=coupling_score,
                commits_together=commits_together,
                total_commits_a=total_commits_a,
                total_commits_b=total_commits_b,
                commits=sorted(commit_set)
            )

            coupling_matrix[(file_a, file_b)] = coupling_data

        # Cache result
        self._coupling_matrix_cache[repo_root] = coupling_matrix

        return coupling_matrix

    def get_coupled_files(
        self,
        repo_root: str,
        target_file: str
    ) -> List[Tuple[str, float]]:
        """
        Get all files coupled to a specific target file.

        Args:
            repo_root: Root directory of git repository
            target_file: File path to find couplings for

        Returns:
            List of (coupled_file, coupling_score) tuples,
            sorted by coupling score descending.

        Example:
            >>> coupled = analyzer.get_coupled_files("/my/repo", "src/main.py")
            >>> for file, score in coupled[:5]:
            ...     print(f"{file}: {score:.2f}")
            src/config.py: 0.85
            src/utils.py: 0.72
            src/handlers.py: 0.65
        """
        coupling_matrix = self.calculate_coupling_matrix(repo_root)

        coupled_files = []

        for (file_a, file_b), coupling_data in coupling_matrix.items():
            if file_a == target_file:
                coupled_files.append((file_b, coupling_data.coupling_score))
            elif file_b == target_file:
                coupled_files.append((file_a, coupling_data.coupling_score))

        # Sort by coupling score descending
        coupled_files.sort(key=lambda x: x[1], reverse=True)

        return coupled_files

    def get_strongest_couplings(
        self,
        repo_root: str,
        top_n: int = 20
    ) -> List[Tuple[str, str, float]]:
        """
        Get the strongest coupling pairs in the repository.

        Args:
            repo_root: Root directory of git repository
            top_n: Maximum number of coupling pairs to return

        Returns:
            List of (file_a, file_b, coupling_score) tuples,
            sorted by coupling score descending.

        Example:
            >>> top_couplings = analyzer.get_strongest_couplings("/my/repo", top_n=10)
            >>> for file_a, file_b, score in top_couplings:
            ...     print(f"{file_a} ↔ {file_b}: {score:.2f}")
            src/a.py ↔ src/b.py: 0.92
            src/c.py ↔ src/d.py: 0.87
        """
        coupling_matrix = self.calculate_coupling_matrix(repo_root)

        # Convert to list of tuples
        couplings = [
            (data.file_a, data.file_b, data.coupling_score)
            for data in coupling_matrix.values()
        ]

        # Sort by score descending
        couplings.sort(key=lambda x: x[2], reverse=True)

        return couplings[:top_n]

    def clear_cache(self):
        """Clear the internal coupling matrix cache."""
        self._coupling_matrix_cache.clear()
