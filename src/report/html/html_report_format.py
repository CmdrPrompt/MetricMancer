from src.report.report_format_strategy import ReportFormatStrategy
from src.report.report_renderer import ReportRenderer
from src.report.report_writer import ReportWriter
from src.kpis.model import RepoInfo
from src.analysis.code_review_advisor import CodeReviewAdvisor


class HTMLReportFormat(ReportFormatStrategy):
    def __init__(self, template_dir='src/report/templates', template_file='report.html'):
        self.template_dir = template_dir
        self.template_file = template_file

    def print_report(self, repo_info: RepoInfo, debug_print, output_file='complexity_report.html',
                     threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, report_links=None, **kwargs):
        """
        Generates an HTML report directly from a RepoInfo object.

        Args:
            include_review_tab: Include Code Review tab with recommendations
            review_branch_only: Only show changed files in review tab
            review_base_branch: Base branch to compare against
        """
        # Generate review data if requested
        review_data = None
        if kwargs.get('include_review_tab', False):
            review_data = self._generate_review_data(
                repo_info,
                review_branch_only=kwargs.get('review_branch_only', False),
                review_base_branch=kwargs.get('review_base_branch', 'main')
            )

        renderer = ReportRenderer(
            template_dir=self.template_dir,
            template_file=self.template_file,
            threshold_low=threshold_low,
            threshold_high=threshold_high
        )

        html = renderer.render(
            repo_info=repo_info,
            problem_file_threshold=problem_file_threshold,
            report_links=report_links,
            review_data=review_data
        )

        ReportWriter.write_html(html, output_file)
        print(f"[OK] Report generated: {output_file}")

    def _generate_review_data(self, repo_info: RepoInfo, review_branch_only=False, review_base_branch='main'):
        """
        Generate code review recommendations for all files in the repository.

        Args:
            repo_info: Repository information
            review_branch_only: If True, only analyze changed files
            review_base_branch: Base branch to compare against

        Returns:
            Dict with review recommendations and metadata
        """
        from src.report.report_renderer import collect_all_files
        from src.utilities.git_helpers import get_changed_files_in_branch
        import os

        advisor = CodeReviewAdvisor()
        all_files = collect_all_files(repo_info)

        # Filter to changed files if requested
        if review_branch_only:
            changed_paths = get_changed_files_in_branch(repo_info.repo_root_path, review_base_branch)
            # Convert to relative paths for comparison
            changed_rel_paths = {os.path.relpath(p, repo_info.repo_root_path) for p in changed_paths}
            all_files = [f for f in all_files if f.file_path in changed_rel_paths]

        # Generate recommendations for each file
        recommendations = []
        for file_obj in all_files:
            complexity = file_obj.kpis.get('complexity', type('', (), {'value': 0})).value
            churn = file_obj.kpis.get('churn', type('', (), {'value': 0})).value
            hotspot = file_obj.kpis.get('hotspot', type('', (), {'value': 0})).value

            # Get ownership data
            ownership_kpi = file_obj.kpis.get('Code Ownership')
            ownership_data = ownership_kpi.value if ownership_kpi and hasattr(ownership_kpi, 'value') else None

            shared_ownership_kpi = file_obj.kpis.get('Shared Code Ownership')
            shared_ownership_data = shared_ownership_kpi.value if shared_ownership_kpi and hasattr(shared_ownership_kpi, 'value') else None

            rec = advisor.analyze_file(
                file_obj.file_path,
                complexity,
                churn,
                hotspot,
                ownership_data,
                shared_ownership_data
            )
            recommendations.append(rec)

        # Sort by priority
        recommendations.sort(key=lambda r: r.priority)

        # Calculate summary statistics
        total_time = sum(r.estimated_time_minutes for r in recommendations)
        risk_counts = {
            'critical': sum(1 for r in recommendations if r.risk_level == 'critical'),
            'high': sum(1 for r in recommendations if r.risk_level == 'high'),
            'medium': sum(1 for r in recommendations if r.risk_level == 'medium'),
            'low': sum(1 for r in recommendations if r.risk_level == 'low')
        }

        return {
            'recommendations': recommendations,
            'total_files': len(all_files),
            'total_time_minutes': total_time,
            'risk_counts': risk_counts,
            'branch_filter': review_branch_only,
            'base_branch': review_base_branch if review_branch_only else None
        }
