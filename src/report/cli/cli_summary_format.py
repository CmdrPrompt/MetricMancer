"""
Executive Summary Dashboard formatter for terminal output.
Provides actionable insights prioritized by importance instead of file tree.
"""

from src.report.report_format_strategy import ReportFormatStrategy
from src.report.cli.cli_format_base import CLIFormatBase
from src.kpis.model import RepoInfo, File
from typing import List, Tuple, Dict

# Categorization thresholds
HIGH_COMPLEXITY_THRESHOLD = 15
HIGH_CHURN_THRESHOLD = 10
MEDIUM_COMPLEXITY_MIN = 5

# Quality score thresholds: (max_avg_complexity, score, grade)
QUALITY_THRESHOLDS = [
    (10, 90, 'A'),
    (15, 75, 'B'),
    (20, 60, 'C'),
]
DEFAULT_QUALITY = (40, 'D')

# Tech debt thresholds: (max_avg_complexity, level)
TECH_DEBT_THRESHOLDS = [
    (10, 'Low'),
    (15, 'Medium'),
    (20, 'Medium-High'),
]
DEFAULT_TECH_DEBT = 'High'


class CLISummaryFormat(CLIFormatBase, ReportFormatStrategy):
    """Formats analysis results as an executive summary dashboard."""

    def print_report(self, repo_info: RepoInfo, debug_print, level="file", **kwargs):
        """
        Prints an executive summary dashboard to the console.
        Focuses on actionable insights and critical issues.
        """

        # Get extreme complexity threshold from kwargs (default: 100)
        extreme_threshold = kwargs.get('extreme_complexity_threshold', 100)

        # Collect all files and calculate statistics
        all_files = self._collect_tracked_files(repo_info)
        stats = self._calculate_statistics(all_files)

        # Categorize files by risk level
        critical_files, emerging_files, high_complexity_files, high_churn_files, extreme_files = self._categorize_files(
            all_files, extreme_threshold=extreme_threshold
        )

        # Print the dashboard
        self._print_header()
        self._print_overview(stats)
        self._print_critical_issues(critical_files, extreme_files, extreme_threshold)
        self._print_high_priority(emerging_files, high_complexity_files, high_churn_files)
        self._print_health_metrics(stats)
        self._print_recommendations(critical_files, emerging_files, high_complexity_files, all_files)
        self._print_detailed_reports(repo_info, **kwargs)

    def _calculate_statistics(self, files: List[File]) -> Dict:
        """Calculate overview statistics from all files."""
        if not files:
            return self._empty_stats()

        complexities = self._collect_kpi_values(files, 'complexity')
        cognitive = self._collect_kpi_values(files, 'cognitive_complexity')
        churns = self._collect_kpi_values(files, 'churn')

        return {
            'total_files': len(files),
            'avg_complexity': self._safe_avg(complexities),
            'max_complexity': max(complexities) if complexities else 0,
            'avg_cognitive_complexity': self._safe_avg(cognitive),
            'max_cognitive_complexity': max(cognitive) if cognitive else 0,
            'avg_churn': self._safe_avg(churns),
            'total_churn': sum(churns) if churns else 0
        }

    def _empty_stats(self) -> Dict:
        """Return empty statistics dictionary."""
        return {
            'total_files': 0, 'avg_complexity': 0.0, 'max_complexity': 0,
            'avg_cognitive_complexity': 0.0, 'max_cognitive_complexity': 0,
            'avg_churn': 0.0, 'total_churn': 0
        }

    def _collect_kpi_values(self, files: List[File], kpi_name: str) -> List:
        """Collect non-None KPI values from files."""
        return [self._get_kpi_value(f.kpis, kpi_name) for f in files
                if f.kpis.get(kpi_name) and f.kpis[kpi_name].value is not None]

    def _safe_avg(self, values: List) -> float:
        """Calculate average, returning 0.0 for empty list."""
        return sum(values) / len(values) if values else 0.0

    def _categorize_files(self, files: List[File], extreme_threshold: int = 100) -> Tuple[List, List, List, List, List]:
        """
        Categorize files by risk level based on hotspot analysis criteria.

        Returns:
            Tuple of (critical_hotspots, emerging_hotspots, high_complexity, high_churn, extreme_complexity)
        """
        critical, emerging, high_complexity, high_churn, extreme = [], [], [], [], []

        for file_obj in files:
            kpis = self._extract_file_kpis(file_obj)
            entry = (file_obj, kpis['complexity'], kpis['cognitive_complexity'], kpis['churn'], kpis['hotspot'])
            self._assign_to_category(entry, extreme_threshold, critical, emerging, high_complexity, high_churn, extreme)

        # Sort categories by appropriate metric
        extreme.sort(key=lambda x: x[1], reverse=True)  # By complexity
        critical.sort(key=lambda x: x[4], reverse=True)  # By hotspot
        emerging.sort(key=lambda x: x[4], reverse=True)  # By hotspot
        high_complexity.sort(key=lambda x: x[1], reverse=True)  # By complexity
        high_churn.sort(key=lambda x: x[3], reverse=True)  # By churn

        return critical, emerging, high_complexity, high_churn, extreme

    def _assign_to_category(self, entry: Tuple, extreme_threshold: int,
                            critical: List, emerging: List, high_complexity: List,
                            high_churn: List, extreme: List) -> None:
        """Assign a file entry to the appropriate risk category."""
        _, complexity, _, churn, _ = entry
        category = self._determine_category(complexity, churn, extreme_threshold)
        categories = {
            'extreme': extreme, 'critical': critical, 'emerging': emerging,
            'high_complexity': high_complexity, 'high_churn': high_churn
        }
        if category:
            categories[category].append(entry)

    def _determine_category(self, complexity: int, churn: int, extreme_threshold: int) -> str:
        """Determine risk category based on complexity and churn."""
        is_high_complexity = complexity > HIGH_COMPLEXITY_THRESHOLD
        is_high_churn = churn > HIGH_CHURN_THRESHOLD
        is_medium_complexity = MEDIUM_COMPLEXITY_MIN <= complexity <= HIGH_COMPLEXITY_THRESHOLD

        if complexity > extreme_threshold:
            return 'extreme'
        if is_high_complexity and is_high_churn:
            return 'critical'
        if is_medium_complexity and is_high_churn:
            return 'emerging'
        if is_high_complexity:
            return 'high_complexity'
        if is_high_churn:
            return 'high_churn'
        return None

    def _print_header(self):
        """Print the dashboard header."""
        print()
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           METRICMANCER ANALYSIS SUMMARY                      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print()

    def _print_overview(self, stats: Dict):
        """Print overview statistics."""
        print("📊 OVERVIEW")
        print(f"   Files Analyzed:        {stats['total_files']}")
        print(f"   Average Complexity:    {stats['avg_complexity']:.1f}")
        print(f"   Max Complexity:        {stats['max_complexity']}")
        print(f"   Average Cognitive:     {stats['avg_cognitive_complexity']:.1f}")
        print(f"   Max Cognitive:         {stats['max_cognitive_complexity']}")
        print()

    def _print_critical_issues(self, critical_files: List, extreme_files: List, extreme_threshold: int = 100):
        """Print critical issues section with both hotspots and extreme complexity."""
        print("🔥 CRITICAL ISSUES (Immediate Attention Required)")
        print(f"   Critical Hotspots:     {len(critical_files)} files (High complexity + Active changes)")
        print(f"   Extreme Complexity:    {len(extreme_files)} files (>{extreme_threshold}, regardless of churn)")

        all_critical = self._merge_critical_files(critical_files, extreme_files)
        self._print_top_critical(all_critical)
        print()

    def _merge_critical_files(self, critical_files: List, extreme_files: List) -> List:
        """Merge and sort critical and extreme files by complexity."""
        merged = [('HOTSPOT', *entry) for entry in critical_files]
        merged.extend(('EXTREME', *entry) for entry in extreme_files)
        merged.sort(key=lambda x: x[2], reverse=True)  # Sort by complexity
        return merged

    def _print_top_critical(self, all_critical: List, max_items: int = 5):
        """Print top critical files."""
        if not all_critical:
            print("   ✅ No critical issues detected")
            return

        print(f"   Top {min(max_items, len(all_critical))} Critical Files:")
        for i, (category, file_obj, cplx, cog_cplx, churn, hotspot) in enumerate(all_critical[:max_items], 1):
            file_path = self._get_file_path(file_obj)
            print(f"   {i}. {file_path:35s} (C:{cplx}, Cog:{cog_cplx}, Churn:{churn})")

    def _print_high_priority(self, emerging: List, high_complexity: List, high_churn: List):
        """Print high priority issues section."""
        print("⚠️  HIGH PRIORITY")
        print(f"   Emerging Hotspots:     {len(emerging)} files")
        print(f"   High Complexity (>15): {len(high_complexity)} files")
        print(f"   High Churn (>10):      {len(high_churn)} files")
        print()

    def _print_health_metrics(self, stats: Dict):
        """Print health metrics section."""
        avg_complexity = stats['avg_complexity']
        quality_score, quality_grade = self._calculate_quality_score(avg_complexity)
        tech_debt = self._calculate_tech_debt(avg_complexity)

        print("📈 HEALTH METRICS")
        print(f"   Code Quality:          {quality_grade} ({quality_score}/100)")
        print("   Test Coverage:         Unknown (run with --coverage)")
        print(f"   Tech Debt Score:       {tech_debt}")
        print()

    def _calculate_quality_score(self, avg_complexity: float) -> Tuple[int, str]:
        """Calculate quality score and grade based on average complexity."""
        for max_complexity, score, grade in QUALITY_THRESHOLDS:
            if avg_complexity <= max_complexity:
                return score, grade
        return DEFAULT_QUALITY

    def _calculate_tech_debt(self, avg_complexity: float) -> str:
        """Calculate tech debt level based on average complexity."""
        for max_complexity, level in TECH_DEBT_THRESHOLDS:
            if avg_complexity <= max_complexity:
                return level
        return DEFAULT_TECH_DEBT

    def _print_recommendations(self, critical: List, emerging: List, high_complexity: List, all_files: List):
        """Print actionable recommendations."""
        print("💡 RECOMMENDATIONS")
        recommendations = self._build_recommendations(critical, emerging, all_files)

        if recommendations:
            for i, rec in enumerate(recommendations[:4], 1):
                print(f"   {i}. {rec}")
        else:
            print("   ✅ No critical issues detected - code is in good shape!")
        print()

    def _build_recommendations(self, critical: List, emerging: List, all_files: List) -> List[str]:
        """Build list of recommendations based on analysis results."""
        recommendations = []

        if critical:
            file_path = self._get_file_path(critical[0][0])
            recommendations.append(f"Refactor {file_path} (critical complexity)")
            recommendations.append(f"Add tests for {len(critical)} critical files")

        if emerging:
            suffix = 's' if len(emerging) > 1 else ''
            recommendations.append(f"Investigate high churn in {len(emerging)} emerging hotspot{suffix}")

        fragmented_count = self._count_fragmented_files(all_files)
        if fragmented_count > 0:
            recommendations.append(f"Review code ownership for {fragmented_count} fragmented files")

        return recommendations

    def _count_fragmented_files(self, files: List[File]) -> int:
        """Count files with fragmented ownership (>3 significant authors)."""
        return sum(1 for f in files if self._is_fragmented(f))

    def _is_fragmented(self, file_obj: File) -> bool:
        """Check if a file has fragmented ownership (>3 significant authors)."""
        ownership = file_obj.kpis.get('Shared Code Ownership')
        if not ownership or not ownership.value:
            return False
        return ownership.value.get('num_significant_authors', 0) > 3

    def _print_detailed_reports(self, repo_info: RepoInfo, **kwargs):
        """Print links to detailed reports."""
        print("📁 DETAILED REPORTS")
        self._print_html_report_link(kwargs)
        print("   Hotspot Report: Run with --list-hotspots")
        print("   Review Strategy: Run with --review-strategy")
        print("   File Tree:      Run with --output-format human-tree")
        print()

    def _print_html_report_link(self, kwargs: Dict):
        """Print HTML report link if generating HTML output."""
        if kwargs.get('output_format') != 'html':
            return
        html_output_file = kwargs.get('output_file', 'output/complexity_report.html')
        if html_output_file and not html_output_file.startswith('output/'):
            report_folder = kwargs.get('report_folder', 'output')
            html_output_file = f"{report_folder}/{html_output_file}"
        print(f"   HTML Report:    {html_output_file}")

    def _print_footer(self, elapsed: float):
        """Print footer with timing info."""
        # Note: Analysis timing is now shown in the global TIME SUMMARY
        # This footer is kept for potential future use but doesn't show timing
        pass

    def _get_file_path(self, file_obj: File) -> str:
        """Get the relative file path for display."""
        # Use the file_path attribute which contains the full path
        if hasattr(file_obj, 'file_path') and file_obj.file_path:
            return file_obj.file_path
        # Fallback to just the name
        return file_obj.name
