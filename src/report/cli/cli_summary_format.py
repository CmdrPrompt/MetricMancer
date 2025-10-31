"""
Executive Summary Dashboard formatter for terminal output.
Provides actionable insights prioritized by importance instead of file tree.
"""

from src.report.report_format_strategy import ReportFormatStrategy
from src.kpis.model import RepoInfo, ScanDir, File
from typing import List, Tuple, Dict


class CLISummaryFormat(ReportFormatStrategy):
    """Formats analysis results as an executive summary dashboard."""

    def print_report(self, repo_info: RepoInfo, debug_print, level="file", **kwargs):
        """
        Prints an executive summary dashboard to the console.
        Focuses on actionable insights and critical issues.
        """

        # Collect all files and calculate statistics
        all_files = self._collect_all_files(repo_info)
        stats = self._calculate_statistics(all_files)

        # Categorize files by risk level
        critical_files, emerging_files, high_complexity_files, high_churn_files = self._categorize_files(all_files)

        # Print the dashboard
        self._print_header()
        self._print_overview(stats)
        self._print_critical_issues(critical_files)
        self._print_high_priority(emerging_files, high_complexity_files, high_churn_files)
        self._print_health_metrics(stats)
        self._print_recommendations(critical_files, emerging_files, high_complexity_files, all_files)
        self._print_detailed_reports(repo_info, **kwargs)

    def _collect_all_files(self, scan_dir: ScanDir) -> List[File]:
        """Recursively collects all git-tracked File objects from a ScanDir tree."""

        def is_tracked_file(file_obj: File):
            co = file_obj.kpis.get('Code Ownership')
            if not co or not hasattr(co, 'value'):
                return False

            # Handle new cache structure: value is either None/empty dict for untracked files,
            # or dict with author percentages for tracked files
            if co.value is None or not isinstance(co.value, dict) or len(co.value) == 0:
                return False

            # Check if it's the old 'N/A' format or actual ownership data
            if co.value.get('ownership') == 'N/A':
                return False

            return True

        files = [f for f in scan_dir.files.values() if is_tracked_file(f)]
        for sub_dir in scan_dir.scan_dirs.values():
            files.extend(self._collect_all_files(sub_dir))
        return files

    def _calculate_statistics(self, files: List[File]) -> Dict:
        """Calculate overview statistics from all files."""
        if not files:
            return {
                'total_files': 0,
                'total_complexity': 0,
                'avg_complexity': 0.0,
                'min_complexity': 0,
                'max_complexity': 0,
                'avg_churn': 0.0,
                'total_churn': 0
            }

        complexities = []
        churns = []

        for file_obj in files:
            # Get complexity
            complexity_kpi = file_obj.kpis.get('complexity')
            if complexity_kpi and complexity_kpi.value is not None:
                complexities.append(complexity_kpi.value)

            # Get churn
            churn_kpi = file_obj.kpis.get('churn')
            if churn_kpi and churn_kpi.value is not None:
                churns.append(churn_kpi.value)

        total_complexity = sum(complexities) if complexities else 0
        total_churn = sum(churns) if churns else 0

        return {
            'total_files': len(files),
            'total_complexity': total_complexity,
            'avg_complexity': total_complexity / len(complexities) if complexities else 0.0,
            'min_complexity': min(complexities) if complexities else 0,
            'max_complexity': max(complexities) if complexities else 0,
            'avg_churn': total_churn / len(churns) if churns else 0.0,
            'total_churn': total_churn
        }

    def _categorize_files(self, files: List[File]) -> Tuple[List, List, List, List]:
        """
        Categorize files by risk level based on hotspot analysis criteria.

        Returns:
            Tuple of (critical_hotspots, emerging_hotspots, high_complexity, high_churn)
        """
        critical = []
        emerging = []
        high_complexity = []
        high_churn = []

        for file_obj in files:
            complexity_kpi = file_obj.kpis.get('complexity')
            churn_kpi = file_obj.kpis.get('churn')
            hotspot_kpi = file_obj.kpis.get('hotspot')

            complexity = complexity_kpi.value if complexity_kpi and complexity_kpi.value is not None else 0
            churn = churn_kpi.value if churn_kpi and churn_kpi.value is not None else 0
            hotspot = hotspot_kpi.value if hotspot_kpi and hotspot_kpi.value is not None else 0

            # Critical: High complexity AND high churn (from hotspot_analyzer criteria)
            if complexity > 15 and churn > 10:
                critical.append((file_obj, complexity, churn, hotspot))
            # Emerging: Medium complexity AND high churn
            elif 5 <= complexity <= 15 and churn > 10:
                emerging.append((file_obj, complexity, churn, hotspot))
            # High complexity alone
            elif complexity > 15:
                high_complexity.append((file_obj, complexity, churn, hotspot))
            # High churn alone
            elif churn > 10:
                high_churn.append((file_obj, complexity, churn, hotspot))

        # Sort by hotspot score (highest first)
        critical.sort(key=lambda x: x[3], reverse=True)
        emerging.sort(key=lambda x: x[3], reverse=True)
        high_complexity.sort(key=lambda x: x[1], reverse=True)
        high_churn.sort(key=lambda x: x[2], reverse=True)

        return critical, emerging, high_complexity, high_churn

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
        print(f"   Total Complexity:      {stats['total_complexity']:,}")
        print(f"   Average Complexity:    {stats['avg_complexity']:.1f}")
        print()

    def _print_critical_issues(self, critical_files: List):
        """Print critical issues section."""
        print("🔥 CRITICAL ISSUES (Immediate Attention Required)")
        print(f"   Critical Hotspots:     {len(critical_files)} files")

        if critical_files:
            print("   Top 3 Risk Files:")
            for i, (file_obj, complexity, churn, hotspot) in enumerate(critical_files[:3], 1):
                file_path = self._get_file_path(file_obj)
                print(f"   {i}. {file_path:40s} (Hotspot: {hotspot}, C:{complexity}, Churn:{churn})")
        else:
            print("   ✅ No critical hotspots detected")
        print()

    def _print_high_priority(self, emerging: List, high_complexity: List, high_churn: List):
        """Print high priority issues section."""
        print("⚠️  HIGH PRIORITY")
        print(f"   Emerging Hotspots:     {len(emerging)} files")
        print(f"   High Complexity (>15): {len(high_complexity)} files")
        print(f"   High Churn (>10):      {len(high_churn)} files")
        print()

    def _print_health_metrics(self, stats: Dict):
        """Print health metrics section."""
        # Calculate code quality score (simple heuristic)
        avg_complexity = stats['avg_complexity']
        if avg_complexity <= 10:
            quality_score = 90
            quality_grade = "A"
        elif avg_complexity <= 15:
            quality_score = 75
            quality_grade = "B"
        elif avg_complexity <= 20:
            quality_score = 60
            quality_grade = "C"
        else:
            quality_score = 40
            quality_grade = "D"

        # Determine tech debt level
        if avg_complexity <= 10:
            tech_debt = "Low"
        elif avg_complexity <= 15:
            tech_debt = "Medium"
        elif avg_complexity <= 20:
            tech_debt = "Medium-High"
        else:
            tech_debt = "High"

        print("📈 HEALTH METRICS")
        print(f"   Code Quality:          {quality_grade} ({quality_score}/100)")
        print("   Test Coverage:         Unknown (run with --coverage)")
        print(f"   Tech Debt Score:       {tech_debt}")
        print()

    def _print_recommendations(self, critical: List, emerging: List, high_complexity: List, all_files: List):
        """Print actionable recommendations."""
        print("💡 RECOMMENDATIONS")

        recommendations = []

        # Recommendation 1: Critical files
        if critical:
            top_critical = critical[0][0]
            file_path = self._get_file_path(top_critical)
            recommendations.append(f"Refactor {file_path} (critical complexity)")

        # Recommendation 2: Emerging hotspots
        if emerging:
            recommendations.append(
                f"Investigate high churn in {len(emerging)} emerging hotspot{'s' if len(emerging) > 1 else ''}"
            )

        # Recommendation 3: Testing
        if critical:
            recommendations.append(f"Add tests for {len(critical)} critical files")

        # Recommendation 4: Code ownership
        fragmented_files = []
        for file_obj in all_files:
            ownership = file_obj.kpis.get('Shared Code Ownership')
            if ownership and ownership.value:
                num_authors = ownership.value.get('num_significant_authors', 0)
                if num_authors > 3:
                    fragmented_files.append(file_obj)

        if fragmented_files:
            recommendations.append(f"Review code ownership for {len(fragmented_files)} fragmented files")

        # Print recommendations
        if recommendations:
            for i, rec in enumerate(recommendations[:4], 1):
                print(f"   {i}. {rec}")
        else:
            print("   ✅ No critical issues detected - code is in good shape!")
        print()

    def _print_detailed_reports(self, repo_info: RepoInfo, **kwargs):
        """Print links to detailed reports."""
        print("📁 DETAILED REPORTS")

        # Only show HTML report if we're actually generating an HTML file
        output_format = kwargs.get('output_format')
        if output_format == 'html':
            html_output_file = kwargs.get('output_file', 'output/complexity_report.html')
            if html_output_file and not html_output_file.startswith('output/'):
                # If it's a custom filename, assume it's in the report folder
                report_folder = kwargs.get('report_folder', 'output')
                html_output_file = f"{report_folder}/{html_output_file}"
            print(f"   HTML Report:    {html_output_file}")

        print("   Hotspot Report: Run with --list-hotspots")
        print("   Review Strategy: Run with --review-strategy")
        print("   File Tree:      Run with --output-format human-tree")
        print()

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
