"""
Delta analyzer for function-level code change analysis.

Integrates git diff parsing, AST function extraction, and complexity calculation
to provide precise function-level delta analysis between commits/branches.
"""

import os
import subprocess
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.analysis.delta.models import DeltaDiff, FunctionChange, ChangeType
from src.analysis.delta.function_diff_parser import FunctionDiffParser
from src.kpis.complexity.analyzer import ComplexityAnalyzer
from src.kpis.cognitive_complexity.calculator_factory import CognitiveComplexityCalculatorFactory
from src.languages.config import LANGUAGES
from src.utilities.git_helpers import find_git_repo_root


class DeltaAnalyzer:
    """
    Analyze code changes at function-level granularity.

    Combines git diff parsing with complexity analysis to track which specific
    functions changed and how their complexity evolved.
    """

    def __init__(self, repo_path: str):
        """
        Initialize DeltaAnalyzer for a git repository.

        Args:
            repo_path: Path to the git repository root
        """
        self.repo_path = os.path.abspath(repo_path)
        self.repo_root = find_git_repo_root(repo_path)
        self.diff_parser = FunctionDiffParser()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.cognitive_complexity_factory = CognitiveComplexityCalculatorFactory()

    def analyze_branch_delta(
        self,
        base_branch: str = "main",
        target_branch: Optional[str] = None
    ) -> DeltaDiff:
        """
        Analyze function-level changes between two branches.

        Args:
            base_branch: Base branch to compare against
            target_branch: Target branch (None = current branch)

        Returns:
            DeltaDiff object with all function-level changes
        """
        # Get current branch if target not specified
        if target_branch is None:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=True
            )
            target_branch = result.stdout.strip()

        # Get commit hashes
        base_commit = self._get_commit_hash(base_branch)
        target_commit = self._get_commit_hash(target_branch)

        # Get diff between branches
        diff_text = self._get_git_diff(base_branch, target_branch)

        # Parse and analyze
        return self._analyze_diff(diff_text, base_commit, target_commit, base_branch, target_branch)

    def analyze_commit_range(
        self,
        from_commit: str,
        to_commit: str = "HEAD"
    ) -> DeltaDiff:
        """
        Analyze function-level changes between two commits.

        Args:
            from_commit: Starting commit hash
            to_commit: Ending commit hash (default: HEAD)

        Returns:
            DeltaDiff object with all function-level changes
        """
        # Get diff between commits
        diff_text = self._get_git_diff(from_commit, to_commit)

        # Get full commit hashes
        from_commit_full = self._get_commit_hash(from_commit)
        to_commit_full = self._get_commit_hash(to_commit)

        # Parse and analyze
        return self._analyze_diff(diff_text, from_commit_full, to_commit_full, from_commit, to_commit)

    def analyze_working_tree(self) -> DeltaDiff:
        """
        Analyze uncommitted changes in the working tree.

        Returns:
            DeltaDiff object with function-level changes in working directory
        """
        # Get HEAD commit
        head_commit = self._get_commit_hash('HEAD')

        # Get diff for working tree (staged + unstaged)
        staged_diff = self._run_git_command(['git', 'diff', '--cached', 'HEAD'])
        unstaged_diff = self._run_git_command(['git', 'diff', 'HEAD'])

        # Combine diffs
        diff_text = staged_diff + "\n" + unstaged_diff

        # Parse and analyze
        return self._analyze_diff(diff_text, head_commit, 'working-tree', 'HEAD', 'working-tree')

    def _get_commit_hash(self, ref: str) -> str:
        """Get full commit hash for a git reference."""
        result = subprocess.run(
            ['git', 'rev-parse', ref],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()

    def _get_git_diff(self, from_ref: str, to_ref: str) -> str:
        """Get git diff between two references."""
        return self._run_git_command(['git', 'diff', f'{from_ref}...{to_ref}'])

    def _run_git_command(self, command: List[str]) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            command,
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def _analyze_diff(
        self,
        diff_text: str,
        base_commit: str,
        target_commit: str,
        base_ref: str,
        target_ref: str
    ) -> DeltaDiff:
        """
        Analyze a git diff and extract function-level changes.

        Args:
            diff_text: Git unified diff text
            base_commit: Base commit hash
            target_commit: Target commit hash
            base_ref: Base reference (for file retrieval)
            target_ref: Target reference (for file retrieval)

        Returns:
            DeltaDiff object with all function changes
        """
        # Parse diff to get changed files and lines
        file_changes = self.diff_parser.parse_git_diff(diff_text)

        added_functions = []
        modified_functions = []
        deleted_functions = []

        for file_change in file_changes:
            file_path = file_change['file_path']

            # Skip non-source files
            if not self._is_source_file(file_path):
                continue

            # Get language
            language_config = self._get_language_config(file_path)
            if not language_config:
                continue

            language = language_config.get('name', 'unknown').lower()

            # Get file content from both versions
            base_content = self._get_file_content(file_path, base_ref) if not file_change['is_added'] else ""
            target_content = self._get_file_content(file_path, target_ref) if not file_change['is_deleted'] else ""

            # Extract functions from both versions
            base_functions = self.diff_parser.extract_functions_from_source(
                base_content, language) if base_content else []
            target_functions = self.diff_parser.extract_functions_from_source(
                target_content, language) if target_content else []

            # Map changed lines to functions
            affected_target_functions = self.diff_parser.map_lines_to_functions(
                target_functions,
                file_change['changed_lines']
            ) if target_functions else []

            # Analyze each affected function
            for target_func in affected_target_functions:
                func_name = target_func['name']

                # Find matching function in base version
                base_func = self._find_function_by_name(base_functions, func_name)

                if base_func:
                    # Modified function - calculate complexity change
                    base_complexity = self._calculate_function_complexity(
                        base_content,
                        base_func,
                        language_config
                    )
                    target_complexity = self._calculate_function_complexity(
                        target_content,
                        target_func,
                        language_config
                    )

                    # Calculate cognitive complexity
                    base_cognitive = self._calculate_function_cognitive_complexity(
                        base_content,
                        base_func,
                        file_path
                    )
                    target_cognitive = self._calculate_function_cognitive_complexity(
                        target_content,
                        target_func,
                        file_path
                    )

                    function_change = FunctionChange(
                        file_path=file_path,
                        function_name=func_name,
                        start_line=target_func['start_line'],
                        end_line=target_func['end_line'],
                        change_type=ChangeType.MODIFIED,
                        complexity_before=base_complexity,
                        complexity_after=target_complexity,
                        complexity_delta=target_complexity - base_complexity,
                        cognitive_complexity_before=base_cognitive,
                        cognitive_complexity_after=target_cognitive,
                        cognitive_complexity_delta=target_cognitive - base_cognitive,
                        churn=1,  # Will be calculated in Phase 3
                        hotspot_score=float(target_complexity * 1),  # complexity × churn
                        last_author="unknown",  # Will be calculated in Phase 3
                        last_modified=datetime.now(),
                        lines_changed=len(file_change['changed_lines']),
                        review_time_minutes=self._estimate_review_time(target_complexity)
                    )

                    modified_functions.append(function_change)
                else:
                    # Added function
                    target_complexity = self._calculate_function_complexity(
                        target_content,
                        target_func,
                        language_config
                    )

                    target_cognitive = self._calculate_function_cognitive_complexity(
                        target_content,
                        target_func,
                        file_path
                    )

                    function_change = FunctionChange(
                        file_path=file_path,
                        function_name=func_name,
                        start_line=target_func['start_line'],
                        end_line=target_func['end_line'],
                        change_type=ChangeType.ADDED,
                        complexity_before=None,
                        complexity_after=target_complexity,
                        complexity_delta=target_complexity,
                        cognitive_complexity_before=None,
                        cognitive_complexity_after=target_cognitive,
                        cognitive_complexity_delta=target_cognitive,
                        churn=1,
                        hotspot_score=float(target_complexity * 1),
                        last_author="unknown",
                        last_modified=datetime.now(),
                        lines_changed=len(file_change['changed_lines']),
                        review_time_minutes=self._estimate_review_time(target_complexity)
                    )

                    added_functions.append(function_change)

            # Check for deleted functions
            if file_change['is_deleted']:
                for base_func in base_functions:
                    base_complexity = self._calculate_function_complexity(
                        base_content,
                        base_func,
                        language_config
                    )

                    base_cognitive = self._calculate_function_cognitive_complexity(
                        base_content,
                        base_func,
                        file_path
                    )

                    function_change = FunctionChange(
                        file_path=file_path,
                        function_name=base_func['name'],
                        start_line=base_func['start_line'],
                        end_line=base_func['end_line'],
                        change_type=ChangeType.DELETED,
                        complexity_before=base_complexity,
                        complexity_after=None,
                        complexity_delta=-base_complexity,
                        cognitive_complexity_before=base_cognitive,
                        cognitive_complexity_after=None,
                        cognitive_complexity_delta=-base_cognitive,
                        churn=1,
                        hotspot_score=0.0,
                        last_author="unknown",
                        last_modified=datetime.now(),
                        lines_changed=0,
                        review_time_minutes=0
                    )

                    deleted_functions.append(function_change)

        # Calculate totals
        total_complexity_delta = sum(
            f.complexity_delta for f in (added_functions + modified_functions + deleted_functions)
        )
        total_review_time = sum(
            f.review_time_minutes for f in (added_functions + modified_functions + deleted_functions)
        )

        # Identify critical changes (top 10 by hotspot score)
        all_changes = added_functions + modified_functions
        critical_changes = sorted(all_changes, key=lambda f: f.hotspot_score, reverse=True)[:10]

        # Identify refactorings (complexity decreased)
        refactorings = [f for f in modified_functions if f.complexity_delta < 0]

        return DeltaDiff(
            base_commit=base_commit,
            target_commit=target_commit,
            added_functions=added_functions,
            modified_functions=modified_functions,
            deleted_functions=deleted_functions,
            total_complexity_delta=total_complexity_delta,
            total_review_time_minutes=total_review_time,
            critical_changes=critical_changes,
            refactorings=refactorings
        )

    def _get_language_config(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get language configuration for a file based on extension."""
        for ext, config in LANGUAGES.items():
            if file_path.endswith(ext):
                return config
        return None

    def _is_source_file(self, file_path: str) -> bool:
        """Check if file is a source code file."""
        return self._get_language_config(file_path) is not None

    def _get_file_content(self, file_path: str, ref: str) -> str:
        """Get file content from a specific git reference."""
        if ref == 'working-tree':
            # Read from working directory
            full_path = os.path.join(self.repo_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            return ""

        try:
            result = subprocess.run(
                ['git', 'show', f'{ref}:{file_path}'],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False
            )
            return result.stdout if result.returncode == 0 else ""
        except Exception:
            return ""

    def _find_function_by_name(self, functions: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
        """Find a function by name in a list of functions."""
        for func in functions:
            if func['name'] == name:
                return func
        return None

    def _calculate_function_complexity(
        self,
        file_content: str,
        function: Dict[str, Any],
        language_config: Dict[str, Any]
    ) -> int:
        """
        Calculate cyclomatic complexity for a specific function.

        Args:
            file_content: Full file source code
            function: Function dict with start_line and end_line
            language_config: Language configuration

        Returns:
            Cyclomatic complexity of the function
        """
        # Extract just the function's code
        lines = file_content.split('\n')
        start = function['start_line'] - 1  # Convert to 0-indexed
        end = function['end_line']
        function_code = '\n'.join(lines[start:end])

        # Use existing complexity analyzer
        complexity, _ = self.complexity_analyzer.calculate_for_file(function_code, language_config)

        return complexity if complexity > 0 else 1  # Minimum complexity is 1

    def _calculate_function_cognitive_complexity(
        self,
        file_content: str,
        function: Dict[str, Any],
        file_path: str
    ) -> int:
        """
        Calculate cognitive complexity for a specific function.

        Args:
            file_content: Full file source code
            function: Function dict with start_line and end_line
            file_path: File path (used to determine language from extension)

        Returns:
            Cognitive complexity of the function (0 if not supported)
        """
        # Create cognitive complexity calculator based on file extension
        calculator = self.cognitive_complexity_factory.create(file_path)
        if calculator is None:
            # Language not supported for cognitive complexity
            return 0

        # Calculate cognitive complexity
        try:
            # Extract just the function's code
            lines = file_content.split('\n')
            start = function['start_line'] - 1  # Convert to 0-indexed
            end = function['end_line']
            function_code = '\n'.join(lines[start:end])

            # Calculate for file returns dict {function_name: complexity}
            complexity_map = calculator.calculate_for_file(function_code)

            # Get the function name
            func_name = function['name']

            # Return cognitive complexity for this function
            # If multiple functions, get the first one (should be the only one)
            if func_name in complexity_map:
                return complexity_map[func_name]
            elif complexity_map:
                # Return the first (and likely only) function's complexity
                return list(complexity_map.values())[0]
            else:
                return 0
        except Exception as e:
            # Silently return 0 if calculation fails
            return 0

    def _estimate_review_time(self, complexity: int) -> int:
        """
        Estimate review time in minutes based on complexity.

        Based on "Your Code as a Crime Scene" heuristics:
        - Simple function (complexity 1-5): 5 minutes
        - Moderate function (complexity 6-10): 10 minutes
        - Complex function (complexity 11-20): 20 minutes
        - Very complex function (complexity 21+): 30+ minutes
        """
        if complexity <= 5:
            return 5
        elif complexity <= 10:
            return 10
        elif complexity <= 20:
            return 20
        else:
            return 30 + (complexity - 20) * 2  # +2 min per point above 20
