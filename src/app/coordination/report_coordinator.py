"""
Report Coordinator Module

Handles coordination of report generation across multiple formats and repositories.
Separates report generation logic from main application flow.
"""
from typing import List, Dict

from src.kpis.model import RepoInfo
from src.utilities.debug import debug_print
from src.utilities.path_helpers import normalize_output_path
from src.app.coordination.format_mapper import FormatMapper
from src.app.coordination.filename_generator import FileNameGenerator


class ReportCoordinator:
    """
    Coordinates report generation for multiple formats and repositories.

    Responsibilities:
    - Manage report file naming and extensions
    - Coordinate multi-format report generation
    - Handle cross-repository report linking
    """

    def __init__(self, app_config, report_generator_cls=None):
        """
        Initialize ReportCoordinator.

        Args:
            app_config: Application configuration object
            report_generator_cls: Optional custom report generator class
        """
        self.app_config = app_config
        self.report_generator_cls = report_generator_cls
        self.threshold_low = app_config.threshold_low
        self.threshold_high = app_config.threshold_high
        self.problem_file_threshold = app_config.problem_file_threshold
        self.output_file = app_config.output_file
        self.level = app_config.level
        self.hierarchical = app_config.hierarchical
        self.report_folder = app_config.report_folder
        
        # Initialize filename generator
        self.filename_generator = FileNameGenerator(
            self.output_file,
            app_config.using_output_formats_flag
        )



    def get_generator_from_factory(self, output_format: str):
        """
        Get report generator from factory.

        Args:
            output_format: Output format name

        Returns:
            Report generator class
        """
        from src.report.report_generator_factory import ReportGeneratorFactory
        generator_cls = ReportGeneratorFactory.create(output_format)
        if generator_cls is None:
            from src.report.report_generator import ReportGenerator
            generator_cls = ReportGenerator
        return generator_cls

    def create_report_generator(self, output_format: str):
        """
        Create appropriate report generator class for the given format.

        Args:
            output_format: Output format name

        Returns:
            Report generator class
        """
        if self.report_generator_cls is None:
            return self.get_generator_from_factory(output_format)
        return self.report_generator_cls

    def generate_single_report(self, repo_info: RepoInfo, output_format: str,
                               output_file: str, links_for_this: List[Dict],
                               is_multi_format: bool):
        """
        Generate a single report for a repo in the specified format.

        Args:
            repo_info: Repository information object
            output_format: Output format name
            output_file: Output filename
            links_for_this: Cross-repository links
            is_multi_format: Whether multiple formats are being generated
        """
        output_path = normalize_output_path(self.report_folder, output_file)
        generator_cls = self.create_report_generator(output_format)

        report = generator_cls(
            repo_info, self.threshold_low, self.threshold_high,
            self.problem_file_threshold
        )

        save_cli_to_file = (
            (is_multi_format or self.app_config.using_output_formats_flag) and
            FormatMapper.is_cli_format(output_format)
        )

        report.generate(
            output_file=output_path,
            level=self.level,
            hierarchical=self.hierarchical,
            output_format=output_format,
            report_links=links_for_this,
            save_cli_to_file=save_cli_to_file,
            report_folder=self.report_folder,
            # Pass review tab settings for HTML reports
            include_review_tab=self.app_config.include_review_tab,
            review_branch_only=self.app_config.review_branch_only,
            review_base_branch=self.app_config.review_base_branch,
            # Pass extreme complexity threshold for summary report
            extreme_complexity_threshold=self.app_config.extreme_complexity_threshold
        )

    def generate_reports_for_format(self, output_format: str, repo_infos: List[RepoInfo],
                                    report_links: List[Dict], is_multi_format: bool,
                                    review_strategy_callback=None):
        """
        Generate reports for all repos in the specified output format.

        Args:
            output_format: Output format name
            repo_infos: List of repository information objects
            report_links: Cross-repository links
            is_multi_format: Whether multiple formats are being generated
            review_strategy_callback: Callback for review strategy formats
        """
        # Handle review-strategy formats (aggregate report, not per-repo)
        if FormatMapper.is_review_strategy_format(output_format):
            self._handle_review_strategy_format(
                output_format, repo_infos, review_strategy_callback
            )
            return

        # Generate one report per repo_info for this format
        for idx, repo_info in enumerate(repo_infos):
            base, ext = self.filename_generator.get_base_and_extension(
                output_format, is_multi_format
            )
            output_file, links_for_this = self.filename_generator.generate_with_links(
                base, ext, idx, len(repo_infos), report_links
            )

            self.generate_single_report(
                repo_info, output_format, output_file, links_for_this, is_multi_format
            )
    
    def _handle_review_strategy_format(self, output_format: str, repo_infos: List[RepoInfo],
                                      review_strategy_callback):
        """
        Handle review strategy format generation.
        
        Args:
            output_format: Output format name
            repo_infos: List of repository information objects
            review_strategy_callback: Callback function for review strategy
        """
        if not review_strategy_callback:
            return
        
        review_branch_only = (output_format == 'review-strategy-branch')
        output_filename = ('review_strategy_branch.md' if review_branch_only
                          else 'review_strategy.md')
        review_strategy_callback(repo_infos, review_branch_only, output_filename)

    def generate_all_reports(self, repo_infos: List[RepoInfo], report_links: List[Dict],
                             review_strategy_callback=None):
        """
        Generate reports for all configured output formats.

        Args:
            repo_infos: List of repository information objects
            report_links: Cross-repository links
            review_strategy_callback: Optional callback for review strategy
        """
        is_multi_format = len(self.app_config.output_formats) > 1

        for output_format in self.app_config.output_formats:
            debug_print(f"[DEBUG] Generating reports for format: {output_format}")
            self.generate_reports_for_format(
                output_format, repo_infos, report_links, is_multi_format,
                review_strategy_callback
            )

    @staticmethod
    def prepare_report_links(repo_infos: List[RepoInfo], output_file: str) -> List[Dict]:
        """
        Prepare cross-links for multi-repo reports.

        Args:
            repo_infos: List of repository information objects
            output_file: Base output filename

        Returns:
            List of report link dictionaries
        """
        return FileNameGenerator.prepare_report_links(repo_infos, output_file)
