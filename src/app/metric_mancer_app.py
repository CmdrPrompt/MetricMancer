import os
from typing import Optional

from src.app.core.analyzer import Analyzer
from src.app.scanning.scanner import Scanner
from src.app.hierarchy.data_converter import DataConverter
from src.app.coordination.report_coordinator import ReportCoordinator
from src.app.infrastructure.timing_reporter import TimingReporter
from src.app.coordination.hotspot_coordinator import HotspotCoordinator
from src.app.coordination.review_coordinator import ReviewCoordinator
from src.languages.config import Config
from src.config.app_config import AppConfig
from src.report.report_generator import ReportGenerator
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
        if config is not None:
            # Validate config
            config.validate()
            self.app_config = config
        else:
            # Legacy mode: create config from individual parameters
            if directories is None:
                raise TypeError("MetricMancerApp() missing required argument: 'directories' or 'config'")

            self.app_config = AppConfig(
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

        # Initialize language config, scanner, and analyzer
        self.lang_config = Config()
        self.scanner = Scanner(self.lang_config.languages)
        self.analyzer = Analyzer(
            self.lang_config.languages,
            threshold_low=self.app_config.threshold_low,
            threshold_high=self.app_config.threshold_high,
            churn_period_days=self.app_config.churn_period
        )

        # Expose config values as instance attributes for backward compatibility
        self.directories = self.app_config.directories
        self.threshold_low = self.app_config.threshold_low
        self.threshold_high = self.app_config.threshold_high
        self.problem_file_threshold = self.app_config.problem_file_threshold
        self.output_file = self.app_config.output_file
        self.level = self.app_config.level
        self.hierarchical = self.app_config.hierarchical
        self.output_format = self.app_config.output_format
        self.report_folder = self.app_config.report_folder

        # Hotspot analysis settings
        self.list_hotspots = self.app_config.list_hotspots
        self.hotspot_threshold = self.app_config.hotspot_threshold
        self.hotspot_output = self.app_config.hotspot_output

        # Review strategy settings
        self.review_strategy = self.app_config.review_strategy
        self.review_output = self.app_config.review_output
        self.review_branch_only = self.app_config.review_branch_only
        self.review_base_branch = self.app_config.review_base_branch

        # Code churn settings
        self.churn_period = self.app_config.churn_period

        # Allow swapping report generator (None means multi-format mode)
        self.report_generator_cls = report_generator_cls

        # Provide direct access to config for new code
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
        all_hotspots = []

        for repo_info in repo_infos:
            # Convert repo_info to dict format using DataConverter
            repo_data = DataConverter.convert_repo_info_to_dict(repo_info)
            hotspots = extract_hotspots_from_data(repo_data, self.hotspot_threshold)
            all_hotspots.extend(hotspots)

        if not all_hotspots:
            print(f"\n✅ No hotspots found above threshold {self.hotspot_threshold}.")
            return

        # Display or save results using HotspotCoordinator
        if self.hotspot_output:
            output_path = os.path.join(self.report_folder, self.hotspot_output)
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
        if review_branch_only is None:
            review_branch_only = self.review_branch_only
        if output_filename is None:
            output_filename = self.review_output
        from src.analysis.code_review_advisor import generate_review_report
        from src.utilities.git_helpers import get_changed_files_in_branch, get_current_branch

        # Convert repo_info to dict format using DataConverter
        all_data = {}
        for repo_info in repo_infos:
            repo_data = DataConverter.convert_repo_info_to_dict_with_ownership(repo_info)
            # Merge data from multiple repos
            if 'files' not in all_data:
                all_data = repo_data
            else:
                # Merge files and directories
                all_data['files'].update(repo_data.get('files', {}))
                all_data['scan_dirs'].update(repo_data.get('scan_dirs', {}))

        # Get changed files if branch-only mode is enabled
        filter_files = None
        current_branch = None
        if review_branch_only and self.directories:
            try:
                repo_path = self.directories[0]
                current_branch = get_current_branch(repo_path)
                if current_branch:
                    print(f"\n🔍 Filtering review strategy to changed files in branch: "
                          f"{current_branch}")
                    print(f"   Comparing against base branch: "
                          f"{self.review_base_branch}")
                    filter_files = get_changed_files_in_branch(repo_path, self.review_base_branch)
                    if filter_files:
                        print(f"   Found {len(filter_files)} changed files")
                    else:
                        print("   ⚠️  No changed files found, showing all files")
            except Exception as e:
                print(f"   ⚠️  Could not determine changed files: {e}")
                debug_print(f"[DEBUG] Error getting changed files: {e}")

        # Generate the report in report folder
        try:
            os.makedirs(self.report_folder, exist_ok=True)
            output_path = os.path.join(self.report_folder, output_filename)
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
            import traceback
            traceback.print_exc()
