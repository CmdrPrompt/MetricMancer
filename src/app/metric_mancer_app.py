import os

from src.app.core.analyzer import Analyzer
from src.app.scanning.scanner import Scanner
from src.app.hierarchy.data_converter import DataConverter
from src.app.coordination.report_coordinator import ReportCoordinator
from src.app.coordination.delta_review_coordinator import DeltaReviewCoordinator
from src.app.coordination.filename_generator import FileNameGenerator
from src.app.infrastructure.timing_reporter import TimingReporter
from src.app.infrastructure.exception_handler import ExceptionHandler
from src.app.services.hotspot_service import HotspotService
from src.app.services.file_change_detector import FileChangeDetector
from src.utilities.path_helpers import normalize_output_path
from src.languages.config import Config
from src.config.app_config import AppConfig
from src.report.report_generator import ReportGenerator  # noqa: F401 - used in tests for mocking
from src.utilities.debug import debug_print


class MetricMancerApp:
    def __init__(self, config: AppConfig,
                 report_generator_cls=None,
                 scanner=None, analyzer=None):
        """
        Initialize MetricMancerApp.

        Usage (Configuration Object Pattern):
            config = AppConfig(directories=['/path/to/code'], threshold_low=5.0)
            app = MetricMancerApp(config=config)

        Dependency Injection (for testing):
            mock_scanner = Mock()
            mock_analyzer = Mock()
            app = MetricMancerApp(config=config, scanner=mock_scanner, analyzer=mock_analyzer)

        Args:
            config: AppConfig object with all settings (REQUIRED)
            report_generator_cls: Optional report generator class (for testing/custom generators)
            scanner: Optional Scanner instance (for testing/DI, default: creates new Scanner)
            analyzer: Optional Analyzer instance (for testing/DI, default: creates new Analyzer)

        Raises:
            TypeError: If config is not provided
            ValueError: If config validation fails
        """
        # Validate config is provided
        if config is None:
            raise TypeError("MetricMancerApp() missing required argument: 'config'")

        # Store and validate config
        config.validate()
        self.app_config = config

        # Ensure output_file is set for file-based formats (moved from main.py)
        self._ensure_output_file_for_file_formats()

        # Initialize dependencies (Dependency Injection Pattern)
        self.lang_config = Config()
        self.scanner = scanner or Scanner(self.lang_config.languages)
        self.analyzer = analyzer or Analyzer(
            self.lang_config.languages,
            threshold_low=self.app_config.threshold_low,
            threshold_high=self.app_config.threshold_high,
            churn_period_days=self.app_config.churn_period
        )

        # Allow swapping report generator (None means multi-format mode)
        self.report_generator_cls = self._determine_report_generator_cls(report_generator_cls)

        # Backward compatibility alias: self.config -> self.app_config
        self.config = self.app_config

    def _ensure_output_file_for_file_formats(self):
        """
        Ensure output_file is set when any format requires a file.

        Follows Configuration Object Pattern: This logic was moved from main.py
        to keep main.py focused on orchestration only.
        """
        file_based_formats = {'html', 'json', 'machine'}
        needs_file = any(fmt in file_based_formats for fmt in self.app_config.output_formats)

        if needs_file and not self.app_config.output_file:
            # Generate default output filename for file-based formats
            # For now, use a simple default
            self.app_config.output_file = "complexity_report.html"

    def _determine_report_generator_cls(self, report_generator_cls):
        """
        Determine which report generator class to use.

        Follows Factory Pattern: Logic moved from main.py to keep main.py simple.
        Uses ReportGeneratorFactory for single-format, None for multi-format.

        Args:
            report_generator_cls: Explicitly provided generator class (for testing)

        Returns:
            Report generator class or None for multi-format mode
        """
        if report_generator_cls is not None:
            # Explicitly provided (for testing/backward compatibility)
            return report_generator_cls

        # Configuration Object Pattern: Use config to determine mode
        if len(self.app_config.output_formats) > 1:
            # Multi-format: ReportCoordinator handles generator selection
            return None
        else:
            # Single format: Use factory pattern
            from src.report.report_generator_factory import ReportGeneratorFactory
            generator_cls = ReportGeneratorFactory.create(self.app_config.output_format)
            if generator_cls is None:
                # Factory returns None for 'html' - use default ReportGenerator
                generator_cls = ReportGenerator
            return generator_cls

    def _scan_files(self):
        """Scan directories and return list of files."""
        debug_print(f"[DEBUG] scan dirs: {self.app_config.directories}")
        files = self.scanner.scan(self.app_config.directories)
        debug_print(f"[DEBUG] scanned files: {len(files)}")
        return files

    def _analyze_files(self, files):
        """Analyze files and return repo info objects."""
        summary = self.analyzer.analyze(files)
        debug_print(f"[DEBUG] summary keys: {list(summary.keys())}")

        repo_infos = []
        for repo_root, repo_info in summary.items():
            debug_print(f"[DEBUG] repo_info: root={repo_info.repo_root_path}, name={repo_info.repo_name}")
            repo_infos.append(repo_info)

        return repo_infos

    def _prepare_report_links(self, repo_infos):
        """Prepare cross-links for multi-repo reports."""
        return FileNameGenerator.prepare_report_links(
            repo_infos, self.app_config.output_file
        )

    def run(self):
        """
        Main entry point for running the analysis pipeline.

        Pipeline steps:
        1. Scan files in configured directories
        2. Analyze files for complexity metrics
        3. Generate reports in configured formats
        4. Run optional analyses (hotspots, review strategy, delta review)
        """
        timing_reporter = TimingReporter()

        # Core pipeline: scan → analyze → report
        files, repo_infos = self._run_core_pipeline(timing_reporter)
        report_links = self._prepare_report_links(repo_infos)
        self._run_report_generation(timing_reporter, repo_infos, report_links)

        # Optional analyses
        self._run_optional_analyses(repo_infos)

        # Print timing summary
        self._print_timing_summary(timing_reporter)

    def _run_core_pipeline(self, timing_reporter: TimingReporter):
        """
        Execute the core scan and analysis pipeline.

        Args:
            timing_reporter: TimingReporter instance for tracking execution time

        Returns:
            Tuple of (files, repo_infos)
        """
        # Step 1: Scan files
        timing_reporter.start_scan()
        files = self._scan_files()
        timing_reporter.end_scan()

        # Step 2: Analyze files
        timing_reporter.start_analysis()
        repo_infos = self._analyze_files(files)
        timing_reporter.end_analysis()

        return files, repo_infos

    def _run_report_generation(self, timing_reporter: TimingReporter, repo_infos, report_links):
        """
        Execute report generation for all configured formats.

        Args:
            timing_reporter: TimingReporter instance for tracking execution time
            repo_infos: List of RepoInfo objects from analysis
            report_links: Cross-links for multi-repo reports
        """
        timing_reporter.start_report_generation()
        os.makedirs(self.app_config.report_folder, exist_ok=True)
        is_multi_format = len(self.app_config.output_formats) > 1

        self._generate_all_reports(repo_infos, report_links, is_multi_format)
        timing_reporter.end_report_generation()

    def _run_optional_analyses(self, repo_infos):
        """
        Run optional analyses based on configuration flags.

        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        if self.app_config.list_hotspots:
            self._run_hotspot_analysis(repo_infos)

        if self.app_config.review_strategy:
            self._run_review_strategy_analysis(repo_infos)

        if self.app_config.delta_review:
            self._run_delta_review_analysis(repo_infos)

    def _print_timing_summary(self, timing_reporter: TimingReporter):
        """
        Print timing summary for the analysis run.

        Args:
            timing_reporter: TimingReporter instance with recorded timings
        """
        if self.app_config.no_timing:
            return

        analyzer_timing = getattr(self.analyzer, 'timing', None)
        timing_reporter.print_summary(analyzer_timing)

    def _generate_all_reports(self, repo_infos, report_links, is_multi_format):
        """Generate reports for all configured output formats using ReportCoordinator."""
        coordinator = ReportCoordinator(
            self.app_config,
            self.report_generator_cls
        )

        for output_format in self.app_config.output_formats:
            debug_print(f"[DEBUG] Generating reports for format: {output_format}")

            # Handle review-strategy formats (aggregate report, not per-repo)
            if output_format in ['review-strategy', 'review-strategy-branch']:
                review_branch_only = (output_format == 'review-strategy-branch')
                output_filename = ('review_strategy_branch.md' if review_branch_only
                                   else 'review_strategy.md')
                self._run_review_strategy_analysis(
                    repo_infos, review_branch_only, output_filename
                )
                continue

            # Use coordinator for standard report generation
            coordinator.generate_reports_for_format(
                output_format,
                repo_infos,
                report_links,
                is_multi_format
            )

    def _run_hotspot_analysis(self, repo_infos):
        """
        Run hotspot analysis on the analyzed repositories.

        Uses HotspotService for separation of concerns (Refactoring #9).

        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        service = HotspotService(
            threshold=self.app_config.hotspot_threshold,
            output_path=self.app_config.hotspot_output,
            report_folder=self.app_config.report_folder
        )
        service.analyze(repo_infos)

    def _run_review_strategy_analysis(self, repo_infos, review_branch_only=None,
                                      output_filename=None):
        """
        Generate code review strategy report based on KPI metrics.

        Args:
            repo_infos: List of RepoInfo objects from analysis
            review_branch_only: Override for branch-only mode (default: use config.review_branch_only)
            output_filename: Override output filename (default: use config.review_output)
        """
        # Use parameter if provided, otherwise fall back to config
        if review_branch_only is not None:
            review_branch_only = review_branch_only
        else:
            review_branch_only = self.app_config.review_branch_only
        output_filename = output_filename if output_filename is not None else self.app_config.review_output

        # Convert and merge repo data
        all_data = self._convert_and_merge_repo_data(repo_infos)

        # Get changed files if branch-only mode is enabled
        filter_files, current_branch = self._get_changed_files_for_review(review_branch_only)

        # Generate and save the report
        self._generate_and_save_review_report(
            all_data, filter_files, current_branch,
            review_branch_only, output_filename
        )

    def _convert_and_merge_repo_data(self, repo_infos):
        """Convert RepoInfo objects to dict format and merge multiple repos."""
        all_data = {}
        for repo_info in repo_infos:
            repo_data = DataConverter.convert_repo_info_to_dict_with_ownership(repo_info)
            # Merge data from multiple repos
            if 'files' not in all_data:
                all_data = repo_data
            else:
                # Merge files (shallow update is fine)
                all_data['files'].update(repo_data.get('files', {}))
                # Deep merge scan_dirs to avoid overwriting shared directories
                self._deep_merge_scan_dirs(all_data['scan_dirs'], repo_data.get('scan_dirs', {}))
        return all_data

    def _merge_files_at_level(self, target, source):
        """
        Merge files from source into target at the current directory level.

        Args:
            target: Target directory dictionary
            source: Source directory dictionary
        """
        if 'files' in source:
            if 'files' not in target:
                target['files'] = {}
            target['files'].update(source['files'])

    def _merge_subdirectories(self, target, source):
        """
        Recursively merge subdirectories from source into target.

        Args:
            target: Target directory dictionary
            source: Source directory dictionary
        """
        if 'scan_dirs' in source:
            if 'scan_dirs' not in target:
                target['scan_dirs'] = {}
            self._deep_merge_scan_dirs(target['scan_dirs'], source['scan_dirs'])

    def _merge_other_keys(self, target, source):
        """
        Merge non-structural keys (KPIs, metadata) from source into target.

        Args:
            target: Target directory dictionary
            source: Source directory dictionary
        """
        for key in source:
            if key not in ['files', 'scan_dirs']:
                target[key] = source[key]

    def _deep_merge_scan_dirs(self, target, source):
        """
        Recursively merge scan_dirs dictionaries.

        When multiple scan directories (e.g., src/, tests/) contain the same subdirectory
        (e.g., analysis/), we need to merge them instead of overwriting.

        This method has been refactored (Refactoring #3) to use helper methods for
        improved readability and maintainability.

        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Both have this directory - merge recursively using helper methods
                self._merge_files_at_level(target[key], value)
                self._merge_subdirectories(target[key], value)
                self._merge_other_keys(target[key], value)
            else:
                # Key doesn't exist in target or not both dicts - simple assignment
                target[key] = value

    def _get_changed_files_for_review(self, review_branch_only):
        """
        Get list of changed files if branch-only mode is enabled.

        Returns:
            Tuple[Optional[List[str]], Optional[str]]: (filter_files, current_branch)
        """
        if not review_branch_only or not self.app_config.directories:
            return None, None

        # Use ExceptionHandler for git operations (Refactoring #2)
        result = ExceptionHandler.handle_git_operation(
            "determine changed files",
            self._get_changed_files_impl,
            review_branch_only
        )
        return result if result else (None, None)

    def _get_changed_files_impl(self, review_branch_only):
        """
        Implementation of changed files detection (separated for exception handling).

        Uses FileChangeDetector service for separation of concerns (Refactoring #5).
        """
        repo_path = self.app_config.directories[0]

        # Use FileChangeDetector service (Refactoring #5)
        detector = FileChangeDetector(repo_path=repo_path)
        current_branch, filter_files = detector.get_changed_files(
            base_branch=self.app_config.review_base_branch
        )

        if not current_branch:
            return None, None

        print(f"\n🔍 Filtering review strategy to changed files in branch: {current_branch}")
        print(f"   Comparing against base branch: {self.app_config.review_base_branch}")

        if filter_files:
            print(f"   Found {len(filter_files)} changed files")
        else:
            print("   ⚠️  No changed files found, showing all files")

        return filter_files, current_branch

    def _generate_and_save_review_report(self, all_data, filter_files, current_branch,
                                         review_branch_only, output_filename):
        """Generate and save the code review strategy report."""
        # Use ExceptionHandler for report generation (Refactoring #2)
        ExceptionHandler.handle_report_generation(
            "review strategy report generation",
            self._generate_review_report_impl,
            all_data, filter_files, current_branch, review_branch_only, output_filename
        )

    def _generate_review_report_impl(self, all_data, filter_files, current_branch,
                                     review_branch_only, output_filename):
        """Implementation of review report generation (separated for exception handling)."""
        from src.analysis.code_review_advisor import generate_review_report

        os.makedirs(self.app_config.report_folder, exist_ok=True)
        output_path = normalize_output_path(self.app_config.report_folder, output_filename)

        generate_review_report(
            all_data,
            output_file=output_path,
            filter_files=filter_files,
            branch_name=current_branch,
            base_branch=self.app_config.review_base_branch if review_branch_only else None
        )

        print("\n✅ Code review strategy report generated successfully!")

    def _run_delta_review_analysis(self, repo_infos):
        """
        Generate delta review report using function-level diff analysis.

        Following Open/Closed Principle, this method delegates all logic to
        DeltaReviewCoordinator, keeping MetricMancerApp simple.

        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        if not repo_infos or not self.app_config.directories:
            return

        # Use first repository path for delta analysis
        repo_path = self.app_config.directories[0]

        # Generate delta review using coordinator
        delta_diff = DeltaReviewCoordinator.generate_delta_review(
            repo_path=repo_path,
            config=self.app_config
        )

        if delta_diff is None:
            print("\n⚠️  Delta review analysis failed or was skipped")
            return

        # Write report to file
        output_path = normalize_output_path(
            self.app_config.report_folder,
            self.app_config.delta_output
        )
        DeltaReviewCoordinator.write_delta_review_file(delta_diff, output_path)

        # Print summary to console
        DeltaReviewCoordinator.print_delta_summary(delta_diff)
