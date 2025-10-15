import os
from typing import Optional

from src.app.analyzer import Analyzer
from src.app.scanner import Scanner
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

    def run(self):
        import time

        debug_print(f"[DEBUG] scan dirs: {self.directories}")
        t_scan_start = time.perf_counter()
        files = self.scanner.scan(self.directories)
        t_scan_end = time.perf_counter()
        debug_print(f"[DEBUG] scanned files: {len(files)}")
        debug_print(f"[TIME] Scanning took {t_scan_end - t_scan_start:.2f} seconds.")

        t_analyze_start = time.perf_counter()
        summary = self.analyzer.analyze(files)
        t_analyze_end = time.perf_counter()
        debug_print(f"[DEBUG] summary keys: {list(summary.keys())}")
        debug_print(f"[TIME] Analysis took {t_analyze_end - t_analyze_start:.2f} seconds.")

        repo_infos = []
        for repo_root, repo_info in summary.items():
            debug_print(f"[DEBUG] repo_info: root={repo_info.repo_root_path}, name={repo_info.repo_name}")
            repo_infos.append(repo_info)

        # Prepare report_links for cross-linking if multiple repos
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

        t_reportgen_start = time.perf_counter()
        # Ensure report folder exists
        os.makedirs(self.report_folder, exist_ok=True)

        # Check if we're in multi-format mode (used to decide file vs stdout for CLI formats)
        is_multi_format = len(self.app_config.output_formats) > 1

        # Loop over all output formats (multi-format support)
        for output_format in self.app_config.output_formats:
            debug_print(f"[DEBUG] Generating reports for format: {output_format}")

            # Handle review-strategy formats (aggregate report, not per-repo)
            if output_format in ['review-strategy', 'review-strategy-branch']:
                # Set flags based on format
                review_branch_only = (output_format == 'review-strategy-branch')
                # Use different filename for branch-only version
                output_filename = ('review_strategy_branch.md' if review_branch_only
                                   else 'review_strategy.md')
                self._run_review_strategy_analysis(
                    repo_infos, review_branch_only, output_filename
                )
                continue

            # Generate one report per repo_info for this format
            for idx, repo_info in enumerate(repo_infos):
                output_file = self.output_file or "complexity_report.html"

                # Adjust extension based on format
                base, ext = os.path.splitext(output_file)
                if output_format == 'json':
                    ext = '.json'
                elif output_format == 'machine':
                    ext = '.csv'
                elif output_format == 'html':
                    ext = '.html'
                elif output_format in ['summary', 'quick-wins', 'human-tree'] and is_multi_format:
                    # In multi-format mode ONLY, save CLI formats to files
                    # All CLI formats use markdown for proper monospace rendering
                    ext = '.md'
                    # Use descriptive filenames
                    if output_format == 'summary':
                        base = 'summary_report'
                    elif output_format == 'quick-wins':
                        base = 'quick_wins_report'
                    elif output_format == 'human-tree':
                        base = 'file_tree_report'
                # For other formats, keep original or default to .txt

                # If multiple repos, append index to filename
                if len(repo_infos) > 1:
                    output_file = f"{base}_{idx + 1}{ext}"
                    # Mark the current as selected
                    for link in report_links:
                        link['selected'] = (link['href'] == output_file)
                    links_for_this = [link for link in report_links if link['href'] != output_file]
                else:
                    output_file = f"{base}{ext}"
                    links_for_this = report_links

                # Construct full output path with report folder
                output_path = os.path.join(self.report_folder, output_file)

                # Create appropriate generator for this format
                if self.report_generator_cls is None:
                    # Multi-format mode: use factory to create generator for each format
                    from src.report.report_generator_factory import ReportGeneratorFactory
                    generator_cls = ReportGeneratorFactory.create(output_format)
                    # Factory returns None for 'html' format - use default ReportGenerator
                    if generator_cls is None:
                        from src.report.report_generator import ReportGenerator
                        generator_cls = ReportGenerator
                else:
                    # Single format mode: use provided generator class
                    generator_cls = self.report_generator_cls

                # All generators now accept a single repo_info object, making the call uniform.
                report = generator_cls(
                    repo_info, self.threshold_low, self.threshold_high, self.problem_file_threshold
                )
                
                # For CLI formats in multi-format mode, we want to save to file
                save_cli_to_file = (
                    is_multi_format and 
                    output_format in ['summary', 'quick-wins', 'human-tree']
                )
                
                report.generate(
                    output_file=output_path,
                    level=self.level,
                    hierarchical=self.hierarchical,
                    output_format=output_format,
                    report_links=links_for_this,
                    save_cli_to_file=save_cli_to_file
                )
        t_reportgen_end = time.perf_counter()

        debug_print(f"[TIME] Report generation took "
                    f"{t_reportgen_end - t_reportgen_start:.2f} seconds.")

        # Run hotspot analysis if requested
        if self.list_hotspots:
            self._run_hotspot_analysis(repo_infos)

        # Run review strategy analysis if requested
        if self.review_strategy:
            self._run_review_strategy_analysis(repo_infos)

        print("\n=== TIME SUMMARY ===")
        print(f"Scanning:           {t_scan_end - t_scan_start:.2f} seconds")
        print(f"Analysis:           "
              f"{t_analyze_end - t_analyze_start:.2f} seconds")
        print(f"Report generation:  "
              f"{t_reportgen_end - t_reportgen_start:.2f} seconds")
        timing = getattr(self.analyzer, 'timing', None)
        if timing:
            print("-- Analysis breakdown --")

            def safe_fmt(val):
                try:
                    return f"{float(val):.2f}"
                except Exception:
                    return "N/A"
            print(f"  Cache pre-building:     "
                  f"{safe_fmt(timing['cache_prebuild'])} seconds")
            print(f"  Complexity analysis:    "
                  f"{safe_fmt(timing['complexity'])} seconds")
            print(f"  ChurnKPI (per file):    "
                  f"{safe_fmt(timing['filechurn'])} seconds")
            print(f"  HotspotKPI:             "
                  f"{safe_fmt(timing['hotspot'])} seconds")
            print(f"  CodeOwnershipKPI:       "
                  f"{safe_fmt(timing['ownership'])} seconds")
            print(f"  SharedOwnershipKPI:     "
                  f"{safe_fmt(timing['sharedownership'])} seconds")

    def _run_hotspot_analysis(self, repo_infos):
        """
        Run hotspot analysis on the analyzed repositories.

        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        all_hotspots = []

        for repo_info in repo_infos:
            # Convert repo_info to dict format that extract_hotspots_from_data expects
            repo_data = self._convert_repo_info_to_dict(repo_info)
            hotspots = extract_hotspots_from_data(repo_data, self.hotspot_threshold)
            all_hotspots.extend(hotspots)

        if not all_hotspots:
            print(f"\n✅ No hotspots found above threshold {self.hotspot_threshold}.")
            return

        # Display or save results
        if self.hotspot_output:
            # Save to file in report folder
            import os
            os.makedirs(self.report_folder, exist_ok=True)
            output_path = os.path.join(self.report_folder, self.hotspot_output)
            save_hotspots_to_file(all_hotspots, output_path, show_risk_categories=True)
            print_hotspots_summary(all_hotspots)
        else:
            # Display on terminal
            print("\n" + format_hotspots_table(all_hotspots, show_risk_categories=True))

    def _convert_repo_info_to_dict(self, repo_info):
        """
        Convert RepoInfo object to dictionary format compatible with hotspot analysis.

        Args:
            repo_info: RepoInfo object from analysis

        Returns:
            Dictionary representation suitable for hotspot extraction
        """
        def scandir_to_dict(scandir):
            """Recursively convert ScanDir to dict."""
            result = {
                'files': {},
                'scan_dirs': {}
            }

            # Convert files
            for filename, file_obj in scandir.files.items():
                complexity_kpi = file_obj.kpis.get('complexity')
                churn_kpi = file_obj.kpis.get('churn')
                hotspot_kpi = file_obj.kpis.get('hotspot')
                result['files'][filename] = {
                    'kpis': {
                        'complexity': getattr(complexity_kpi, 'value', 0) if complexity_kpi else 0,
                        'churn': getattr(churn_kpi, 'value', 0) if churn_kpi else 0,
                        'hotspot': getattr(hotspot_kpi, 'value', 0) if hotspot_kpi else 0
                    }
                }

            # Convert subdirectories
            for dirname, subdir in scandir.scan_dirs.items():
                result['scan_dirs'][dirname] = scandir_to_dict(subdir)

            return result

        return scandir_to_dict(repo_info)

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

        # Convert repo_info to dict format
        all_data = {}
        for repo_info in repo_infos:
            repo_data = self._convert_repo_info_to_dict_with_ownership(repo_info)
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

    def _convert_repo_info_to_dict_with_ownership(self, repo_info):
        """
        Convert RepoInfo object to dictionary format with ownership data.

        Args:
            repo_info: RepoInfo object from analysis

        Returns:
            Dictionary representation with KPIs and ownership data
        """
        def scandir_to_dict(scandir):
            """Recursively convert ScanDir to dict with ownership."""
            result = {
                'files': {},
                'scan_dirs': {}
            }

            # Convert files
            for filename, file_obj in scandir.files.items():
                complexity_kpi = file_obj.kpis.get('complexity')
                churn_kpi = file_obj.kpis.get('churn')
                hotspot_kpi = file_obj.kpis.get('hotspot')
                file_data = {
                    'kpis': {
                        'complexity': getattr(complexity_kpi, 'value', 0) if complexity_kpi else 0,
                        'churn': getattr(churn_kpi, 'value', 0) if churn_kpi else 0,
                        'hotspot': getattr(hotspot_kpi, 'value', 0) if hotspot_kpi else 0
                    }
                }

                # Add ownership data if available
                ownership_kpi = file_obj.kpis.get('ownership')
                if ownership_kpi and hasattr(ownership_kpi, 'calculation_values'):
                    ownership_data = ownership_kpi.calculation_values.get('ownership', {})
                    if ownership_data:
                        file_data['ownership'] = ownership_data

                result['files'][filename] = file_data

            # Convert subdirectories
            for dirname, subdir in scandir.scan_dirs.items():
                result['scan_dirs'][dirname] = scandir_to_dict(subdir)

            return result

        return scandir_to_dict(repo_info)
