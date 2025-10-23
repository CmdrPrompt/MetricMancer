import os
from typing import Optional

from src.app.core.analyzer import Analyzer
from src.app.scanning.scanner import Scanner
from src.app.hierarchy.data_converter import DataConverter
from src.app.coordination.report_coordinator import ReportCoordinator
from src.app.coordination.delta_review_coordinator import DeltaReviewCoordinator
from src.app.infrastructure.timing_reporter import TimingReporter
from src.utilities.path_helpers import normalize_output_path
from src.languages.config import Config
from src.config.app_config import AppConfig
from src.report.report_generator import ReportGenerator  # noqa: F401 - used in tests for mocking
from src.utilities.debug import debug_print
from src.analysis.hotspot_analyzer import (
    extract_hotspots_from_data, format_hotspots_table,
    save_hotspots_to_file, print_hotspots_summary
)


class MetricMancerApp:
    def __init__(self, directories=None, threshold_low=10.0, threshold_high=20.0,
                 problem_file_threshold=None, output_file='complexity_report.html',
                 report_generator_cls=None, level="file", hierarchical=False,
                 output_format="human", list_hotspots=False, hotspot_threshold=50,
                 hotspot_output=None, review_strategy=False,
                 review_output="review_strategy.md", review_branch_only=False,
                 review_base_branch="main", churn_period=30, report_folder=None,
                 config: Optional[AppConfig] = None):
        """
        Initialize MetricMancerApp.

        Args:
            config: AppConfig object with all settings (preferred, Configuration Object Pattern)
            directories: List of directories to analyze (legacy, for backward compatibility)
            threshold_low: Low complexity threshold (legacy)
            threshold_high: High complexity threshold (legacy)
            ... (other legacy parameters for backward compatibility)

        Note:
            If config is provided, it takes precedence over individual parameters.
            Individual parameters maintained for backward compatibility during transition.
        """
        # Configuration Object Pattern: config parameter takes precedence
        self.app_config = self._initialize_config(
            config, directories, threshold_low, threshold_high,
            problem_file_threshold, output_file, level, hierarchical,
            output_format, report_folder, list_hotspots, hotspot_threshold,
            hotspot_output, review_strategy, review_output, review_branch_only,
            review_base_branch, churn_period
        )

        # Ensure output_file is set for file-based formats (moved from main.py)
        self._ensure_output_file_for_file_formats()

        # Initialize dependencies (Dependency Injection)
        self.lang_config = Config()
        self.scanner = Scanner(self.lang_config.languages)
        self.analyzer = Analyzer(
            self.lang_config.languages,
            threshold_low=self.app_config.threshold_low,
            threshold_high=self.app_config.threshold_high,
            churn_period_days=self.app_config.churn_period
        )

        # Allow swapping report generator (None means multi-format mode)
        self.report_generator_cls = self._determine_report_generator_cls(report_generator_cls)

        # Expose frequently used config values for backward compatibility
        self._expose_config_attributes()

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
                from src.report.report_generator import ReportGenerator
                generator_cls = ReportGenerator
            return generator_cls

    def _initialize_config(self, config, directories, threshold_low, threshold_high,
                           problem_file_threshold, output_file, level, hierarchical,
                           output_format, report_folder, list_hotspots, hotspot_threshold,
                           hotspot_output, review_strategy, review_output, review_branch_only,
                           review_base_branch, churn_period) -> AppConfig:
        """
        Initialize configuration using Configuration Object Pattern.

        Returns:
            AppConfig: Validated configuration object
        """
        if config is not None:
            # Validate config
            config.validate()
            return config

        # Legacy mode: create config from individual parameters
        if directories is None:
            raise TypeError("MetricMancerApp() missing required argument: 'directories' or 'config'")

        return AppConfig(
            directories=directories,
            threshold_low=threshold_low,
            threshold_high=threshold_high,
            problem_file_threshold=problem_file_threshold,
            output_file=output_file,
            level=level,
            hierarchical=hierarchical,
            output_format=output_format,
            report_folder=report_folder if report_folder is not None else 'output',
            list_hotspots=list_hotspots,
            hotspot_threshold=hotspot_threshold,
            hotspot_output=hotspot_output,
            review_strategy=review_strategy,
            review_output=review_output,
            review_branch_only=review_branch_only,
            review_base_branch=review_base_branch,
            churn_period=churn_period,
            debug=False
        )

    def _expose_config_attributes(self):
        """
        Expose config values as instance attributes for backward compatibility.

        Following the Configuration Object Pattern while maintaining
        legacy API compatibility during transition period.
        """
        self.directories = self.app_config.directories
        self.threshold_low = self.app_config.threshold_low
        self.threshold_high = self.app_config.threshold_high
        self.problem_file_threshold = self.app_config.problem_file_threshold
        self.output_file = self.app_config.output_file
        self.level = self.app_config.level
        self.hierarchical = self.app_config.hierarchical
        self.output_format = self.app_config.output_format
        self.report_folder = self.app_config.report_folder
        self.list_hotspots = self.app_config.list_hotspots
        self.hotspot_threshold = self.app_config.hotspot_threshold
        self.hotspot_output = self.app_config.hotspot_output
        self.review_strategy = self.app_config.review_strategy
        self.review_output = self.app_config.review_output
        self.review_branch_only = self.app_config.review_branch_only
        self.review_base_branch = self.app_config.review_base_branch
        self.churn_period = self.app_config.churn_period
        self.config = self.app_config

    def _scan_files(self):
        """Scan directories and return list of files."""
        debug_print(f"[DEBUG] scan dirs: {self.directories}")
        files = self.scanner.scan(self.directories)
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
        report_links = []
        if len(repo_infos) > 1:
            for idx, repo_info in enumerate(repo_infos):
                output_file = self.output_file or "complexity_report.html"
                base, ext = os.path.splitext(output_file)
                filename = f"{base}_{idx + 1}{ext}"
                report_links.append({
                    'href': filename,
                    'name': getattr(repo_info, 'repo_name', f'Repo {idx + 1}'),
                    'selected': False
                })
        return report_links

    def run(self):
        # Initialize timing reporter
        timing_reporter = TimingReporter()

        # Step 1: Scan files
        timing_reporter.start_scan()
        files = self._scan_files()
        timing_reporter.end_scan()

        # Step 2: Analyze files
        timing_reporter.start_analysis()
        repo_infos = self._analyze_files(files)
        timing_reporter.end_analysis()

        # Step 3: Prepare report links
        report_links = self._prepare_report_links(repo_infos)

        # Step 4: Generate reports
        timing_reporter.start_report_generation()
        os.makedirs(self.report_folder, exist_ok=True)
        is_multi_format = len(self.app_config.output_formats) > 1

        self._generate_all_reports(repo_infos, report_links, is_multi_format)
        timing_reporter.end_report_generation()

        # Run hotspot analysis if requested
        if self.list_hotspots:
            self._run_hotspot_analysis(repo_infos)

        # Run review strategy analysis if requested
        if self.review_strategy:
            self._run_review_strategy_analysis(repo_infos)

        # Run delta review analysis if requested
        if self.app_config.delta_review:
            self._run_delta_review_analysis(repo_infos)

        # Print timing summary
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

        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        all_hotspots = self._extract_all_hotspots(repo_infos)

        if not all_hotspots:
            print(f"\n✅ No hotspots found above threshold {self.hotspot_threshold}.")
            return

        self._display_or_save_hotspots(all_hotspots)

    def _extract_all_hotspots(self, repo_infos):
        """Extract hotspots from all repo_infos."""
        all_hotspots = []
        for repo_info in repo_infos:
            # Convert repo_info to dict format using DataConverter
            repo_data = DataConverter.convert_repo_info_to_dict(repo_info)
            hotspots = extract_hotspots_from_data(repo_data, self.hotspot_threshold)
            all_hotspots.extend(hotspots)
        return all_hotspots

    def _display_or_save_hotspots(self, all_hotspots):
        """Display hotspots to console or save to file."""
        if self.hotspot_output:
            output_path = normalize_output_path(self.report_folder, self.hotspot_output)
            save_hotspots_to_file(all_hotspots, output_path, show_risk_categories=True)
            print_hotspots_summary(all_hotspots)
        else:
            print("\n" + format_hotspots_table(all_hotspots, show_risk_categories=True))

    def _run_review_strategy_analysis(self, repo_infos, review_branch_only=None,
                                      output_filename=None):
        """
        Generate code review strategy report based on KPI metrics.

        Args:
            repo_infos: List of RepoInfo objects from analysis
            review_branch_only: Override for branch-only mode (default: use self.review_branch_only)
            output_filename: Override output filename (default: use self.review_output)
        """
        # Use parameter if provided, otherwise fall back to instance variable
        review_branch_only = review_branch_only if review_branch_only is not None else self.review_branch_only
        output_filename = output_filename if output_filename is not None else self.review_output

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

    def _deep_merge_scan_dirs(self, target, source):
        """
        Recursively merge scan_dirs dictionaries.

        When multiple scan directories (e.g., src/, tests/) contain the same subdirectory
        (e.g., analysis/), we need to merge them instead of overwriting.

        Args:
            target: Target dictionary to merge into
            source: Source dictionary to merge from
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                # Both have this directory - merge recursively
                if 'files' in value:
                    # Merge files from this directory level
                    if 'files' not in target[key]:
                        target[key]['files'] = {}
                    target[key]['files'].update(value['files'])

                if 'scan_dirs' in value:
                    # Recursively merge subdirectories
                    if 'scan_dirs' not in target[key]:
                        target[key]['scan_dirs'] = {}
                    self._deep_merge_scan_dirs(target[key]['scan_dirs'], value['scan_dirs'])

                # Merge other keys (kpis, etc.)
                for other_key in value:
                    if other_key not in ['files', 'scan_dirs']:
                        target[key][other_key] = value[other_key]
            else:
                # Key doesn't exist in target or not both dicts - simple assignment
                target[key] = value

    def _get_changed_files_for_review(self, review_branch_only):
        """
        Get list of changed files if branch-only mode is enabled.

        Returns:
            Tuple[Optional[List[str]], Optional[str]]: (filter_files, current_branch)
        """
        from src.utilities.git_helpers import get_changed_files_in_branch, get_current_branch

        if not review_branch_only or not self.directories:
            return None, None

        try:
            repo_path = self.directories[0]
            current_branch = get_current_branch(repo_path)

            if not current_branch:
                return None, None

            print(f"\n🔍 Filtering review strategy to changed files in branch: {current_branch}")
            print(f"   Comparing against base branch: {self.review_base_branch}")

            filter_files = get_changed_files_in_branch(repo_path, self.review_base_branch)

            if filter_files:
                print(f"   Found {len(filter_files)} changed files")
            else:
                print("   ⚠️  No changed files found, showing all files")

            return filter_files, current_branch

        except Exception as e:
            print(f"   ⚠️  Could not determine changed files: {e}")
            debug_print(f"[DEBUG] Error getting changed files: {e}")
            return None, None

    def _generate_and_save_review_report(self, all_data, filter_files, current_branch,
                                         review_branch_only, output_filename):
        """Generate and save the code review strategy report."""
        from src.analysis.code_review_advisor import generate_review_report

        try:
            os.makedirs(self.report_folder, exist_ok=True)
            output_path = normalize_output_path(self.report_folder, output_filename)

            generate_review_report(
                all_data,
                output_file=output_path,
                filter_files=filter_files,
                branch_name=current_branch,
                base_branch=self.review_base_branch if review_branch_only else None
            )

            print("\n✅ Code review strategy report generated successfully!")

        except Exception as e:
            print(f"\n❌ Error generating review strategy report: {e}")
            debug_print(f"[DEBUG] Full traceback: {e}")
            import traceback
            traceback.print_exc()

    def _run_delta_review_analysis(self, repo_infos):
        """
        Generate delta review report using function-level diff analysis.

        Following Open/Closed Principle, this method delegates all logic to
        DeltaReviewCoordinator, keeping MetricMancerApp simple.

        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        if not repo_infos or not self.directories:
            return

        # Use first repository path for delta analysis
        repo_path = self.directories[0]

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
            self.report_folder,
            self.app_config.delta_output
        )
        DeltaReviewCoordinator.write_delta_review_file(delta_diff, output_path)

        # Print summary to console
        DeltaReviewCoordinator.print_delta_summary(delta_diff)
