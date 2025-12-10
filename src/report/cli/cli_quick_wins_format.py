"""
Quick Win Suggestions formatter for terminal output.
Prioritizes improvements by impact vs. effort for maximum ROI.
"""

from src.report.report_format_strategy import ReportFormatStrategy
from src.report.cli.cli_format_base import CLIFormatBase
from src.kpis.model import RepoInfo, File
from typing import List, Tuple, Dict


class CLIQuickWinsFormat(CLIFormatBase, ReportFormatStrategy):
    """Formats analysis results as prioritized quick win suggestions."""

    def print_report(self, repo_info: RepoInfo, debug_print, level="file", **kwargs):
        """
        Prints quick win suggestions prioritized by impact vs. effort.
        Helps teams focus on high-value, low-effort improvements.
        """
        # Collect files with metrics and calculate quick wins
        all_files = self._collect_files_with_metrics(repo_info)
        quick_wins = self._calculate_quick_wins(all_files)

        # Print the report
        self._print_header()
        self._print_quick_wins(quick_wins)
        self._print_summary(quick_wins)

    def _calculate_quick_wins(self, files: List[File]) -> List[Dict]:
        """
        Calculate quick wins with impact and effort scores.

        Returns list of dicts sorted by ROI (impact/effort ratio).
        """
        quick_wins = []

        for file_obj in files:
            # Extract KPIs using base class helper
            kpis = self._extract_file_kpis(file_obj)
            complexity = kpis['complexity']
            churn = kpis['churn']
            hotspot = kpis['hotspot']
            cognitive_complexity = kpis['cognitive_complexity']
            ownership_kpi = file_obj.kpis.get('Code Ownership')
            shared_kpi = file_obj.kpis.get('Shared Code Ownership')

            # Calculate impact score (0-10)
            impact = self._calculate_impact(complexity, churn, hotspot, cognitive_complexity)

            # Calculate effort score (0-10, higher = more effort)
            effort = self._calculate_effort(complexity, file_obj)

            # Calculate ROI (impact/effort ratio)
            roi = impact / max(effort, 1)  # Avoid division by zero

            # Determine action type and description
            action_type, action_desc, reason = self._determine_action(
                file_obj, complexity, churn, hotspot, ownership_kpi, shared_kpi, cognitive_complexity
            )

            # Estimate time required
            time_estimate = self._estimate_time(effort, complexity)

            # Only include files with some improvement potential (impact > 3)
            if impact > 3:
                quick_wins.append({
                    'file': file_obj,
                    'file_path': self._get_file_path(file_obj),
                    'impact': impact,
                    'effort': effort,
                    'roi': roi,
                    'action_type': action_type,
                    'action_desc': action_desc,
                    'reason': reason,
                    'time_estimate': time_estimate,
                    'complexity': complexity,
                    'cognitive_complexity': cognitive_complexity,
                    'churn': churn,
                    'hotspot': hotspot
                })

        # Sort by ROI (highest first)
        quick_wins.sort(key=lambda x: x['roi'], reverse=True)

        return quick_wins

    def _calculate_impact(self, complexity: int, churn: float, hotspot: float,
                          cognitive_complexity: int = 0) -> int:
        """
        Calculate impact score (0-10) based on KPIs.
        Higher score = more impact if improved.

        Cognitive complexity is weighted higher than cyclomatic complexity because
        it better reflects actual understandability and maintenance difficulty.

        Args:
            complexity: Cyclomatic complexity
            churn: Code churn (commits)
            hotspot: Hotspot score (complexity × churn)
            cognitive_complexity: Cognitive complexity (understanding difficulty)
        """
        score = 0

        # Hotspot score contributes most (0-5 points)
        if hotspot > 500:
            score += 5
        elif hotspot > 300:
            score += 4
        elif hotspot > 150:
            score += 3
        elif hotspot > 50:
            score += 2
        elif hotspot > 0:
            score += 1

        # Cognitive complexity contributes more (0-4 points) - PRIORITIZED
        # High cognitive = hard to understand, more bugs, higher maintenance burden
        if cognitive_complexity > 25:
            score += 4
        elif cognitive_complexity > 15:
            score += 3
        elif cognitive_complexity > 10:
            score += 2
        elif cognitive_complexity > 5:
            score += 1

        # Cyclomatic complexity contributes (0-2 points)
        # Lower weight than cognitive since it doesn't account for nesting
        if complexity > 50:
            score += 2
        elif complexity > 20:
            score += 1

        # Churn contributes (0-2 points)
        if churn > 15:
            score += 2
        elif churn > 10:
            score += 1

        return min(score, 10)  # Cap at 10

    def _calculate_effort(self, complexity: int, file_obj: File) -> int:
        """
        Calculate effort score (0-10) based on file characteristics.
        Higher score = more effort required.
        """
        score = 0

        # Complexity-based effort (0-5 points)
        if complexity > 100:
            score += 5
        elif complexity > 50:
            score += 4
        elif complexity > 30:
            score += 3
        elif complexity > 15:
            score += 2
        elif complexity > 5:
            score += 1

        # File size estimate (0-3 points) - based on functions count
        num_functions = len(file_obj.functions) if hasattr(file_obj, 'functions') else 0
        if num_functions > 20:
            score += 3
        elif num_functions > 10:
            score += 2
        elif num_functions > 5:
            score += 1

        # Ownership fragmentation adds effort (0-2 points)
        shared_kpi = file_obj.kpis.get('Shared Code Ownership')
        if shared_kpi and shared_kpi.value:
            num_authors = shared_kpi.value.get('num_significant_authors', 0)
            if num_authors > 4:
                score += 2
            elif num_authors > 2:
                score += 1

        return min(score, 10)  # Cap at 10

    def _determine_action(self, file_obj: File, complexity: int, churn: float,
                          hotspot: float, ownership_kpi, shared_kpi,
                          cognitive_complexity: int = 0) -> Tuple[str, str, str]:
        """
        Determine the recommended action type based on file characteristics.

        Args:
            cognitive_complexity: Cognitive complexity (understanding difficulty)

        Returns:
            (action_type, action_description, reason)
        """
        # Very high cognitive complexity = reduce nesting (PRIORITY)
        if cognitive_complexity > 25:
            return (
                'Reduce Nesting',
                'Reduce nesting depth and extract helper methods',
                f'Very high cognitive complexity (Cog:{cognitive_complexity}) - hard to understand'
            )

        # Check for single owner + high complexity = documentation opportunity
        if shared_kpi and shared_kpi.value:
            num_authors = shared_kpi.value.get('num_significant_authors', 0)
            if num_authors == 1 and complexity > 30:
                return (
                    'Document',
                    'Add comprehensive documentation and comments',
                    f'Single owner (100%), high complexity (C:{complexity})'
                )

        # Critical hotspot = refactor
        if complexity > 15 and churn > 10:
            return (
                'Refactor',
                'Break down into smaller functions (<10 complexity each)',
                f'Critical hotspot (C:{complexity}, Churn:{churn})'
            )

        # High complexity alone = refactor
        if complexity > 20:
            return (
                'Refactor',
                'Extract functions to reduce complexity',
                f'High complexity (C:{complexity})'
            )

        # Moderate cognitive complexity = simplify
        if cognitive_complexity > 15:
            return (
                'Simplify',
                'Reduce nesting and simplify boolean conditions',
                f'Moderate cognitive complexity (Cog:{cognitive_complexity})'
            )

        # High churn = add tests
        if churn > 10:
            return (
                'Add Tests',
                'Start with happy path tests, then edge cases',
                f'High churn (Churn:{churn}) - likely lacks test coverage'
            )

        # Fragmented ownership = establish ownership
        if shared_kpi and shared_kpi.value:
            num_authors = shared_kpi.value.get('num_significant_authors', 0)
            if num_authors > 3:
                return (
                    'Review Ownership',
                    'Establish clear ownership and responsibility',
                    f'Fragmented ownership ({num_authors} significant authors)'
                )

        # Default = general improvement
        return (
            'Improve',
            'General code quality improvements',
            f'Moderate metrics (C:{complexity}, Churn:{churn})'
        )

    def _estimate_time(self, effort: int, complexity: int) -> str:
        """Estimate time required based on effort score."""
        if effort >= 8:
            return '1-2 days'
        elif effort >= 6:
            return '4-8 hours'
        elif effort >= 4:
            return '2-4 hours'
        elif effort >= 2:
            return '1-2 hours'
        else:
            return '30-60 min'

    def _print_header(self):
        """Print the header."""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║              QUICK WIN SUGGESTIONS                           ║")
        print("║          Highest Impact, Lowest Effort                       ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

    def _print_quick_wins(self, quick_wins: List[Dict]):
        """Print the quick wins list."""
        if not quick_wins:
            print("✅ No significant improvement opportunities found!")
            print("   Your codebase is in good shape.")
            return

        # Show top 10 by default
        display_count = min(10, len(quick_wins))

        for i, win in enumerate(quick_wins[:display_count], 1):
            self._print_quick_win(i, win)

        if len(quick_wins) > display_count:
            print(f"\n💡 {len(quick_wins) - display_count} more opportunities available")
            print("   Run with --output-format json for full list")

    def _print_quick_win(self, index: int, win: Dict):
        """Print a single quick win suggestion."""
        # Header
        print(f"{index}. {win['action_type']}: {win['file_path']}")

        # Impact bar
        impact_bar = self._create_bar(win['impact'], 10, '█')
        impact_label = 'High' if win['impact'] >= 7 else 'Medium' if win['impact'] >= 5 else 'Low'
        print(f"   Impact:  {impact_bar} {impact_label} ({win['impact']}/10)")

        # Effort bar
        effort_bar = self._create_bar(win['effort'], 10, '█')
        effort_label = 'High' if win['effort'] >= 7 else 'Medium' if win['effort'] >= 4 else 'Low'
        print(f"   Effort:  {effort_bar} {effort_label} ({win['effort']}/10)")

        # Time estimate
        print(f"   Time:    {win['time_estimate']}")

        # Metrics - show both complexity metrics if available
        metrics_parts = []
        if win['complexity'] > 0:
            metrics_parts.append(f"Complexity: {win['complexity']}")
        if win['cognitive_complexity'] > 0:
            metrics_parts.append(f"Cognitive: {win['cognitive_complexity']}")
        if win['churn'] > 0:
            metrics_parts.append(f"Churn: {win['churn']}")
        if metrics_parts:
            print(f"   Metrics: {', '.join(metrics_parts)}")

        # Reason
        print(f"   Reason:  {win['reason']}")

        # Action
        print(f"   Action:  {win['action_desc']}")
        print()

    def _create_bar(self, value: int, max_value: int, char: str = '█') -> str:
        """Create a visual bar for impact/effort display."""
        filled = int((value / max_value) * 10)
        empty = 10 - filled
        return char * filled + '░' * empty

    def _print_summary(self, quick_wins: List[Dict]):
        """Print summary statistics."""
        if not quick_wins:
            return

        print("📊 SUMMARY")

        # Count by action type
        action_counts = {}
        for win in quick_wins:
            action = win['action_type']
            action_counts[action] = action_counts.get(action, 0) + 1

        print(f"   Total Opportunities:  {len(quick_wins)}")
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   {action:20s}: {count}")

        # ROI insights
        if quick_wins:
            print(f"\n   Best ROI:  {quick_wins[0]['file_path']}")
            print(f"              (Impact: {quick_wins[0]['impact']}/10, Effort: {quick_wins[0]['effort']}/10)")

        print()
        print("💡 TIP: Start with items 1-3 for maximum return on investment")
        print()

    def _print_footer(self, elapsed: float):
        """Print footer with timing info."""
        # Note: Analysis timing is now shown in the global TIME SUMMARY
        # This footer is kept for potential future use but doesn't show timing
        pass

    def _get_file_path(self, file_obj: File) -> str:
        """Get the relative file path for display."""
        if hasattr(file_obj, 'file_path') and file_obj.file_path:
            return file_obj.file_path
        return file_obj.name
