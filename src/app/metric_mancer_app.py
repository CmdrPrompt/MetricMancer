import os
import json

from src.app.analyzer import Analyzer
from src.app.scanner import Scanner
from src.languages.config import Config
from src.report.report_generator import ReportGenerator
from src.utilities.debug import debug_print
from src.utilities.hotspot_analyzer import (
    extract_hotspots_from_data, format_hotspots_table, 
    save_hotspots_to_file, print_hotspots_summary
)


class MetricMancerApp:
    def __init__(self, directories, threshold_low=10.0, threshold_high=20.0, problem_file_threshold=None, output_file='complexity_report.html', report_generator_cls=None, level="file", hierarchical=False, output_format="human", list_hotspots=False, hotspot_threshold=50, hotspot_output=None, review_strategy=False, review_output="review_strategy.txt", review_branch_only=False, review_base_branch="main"):
        self.config = Config()
        self.scanner = Scanner(self.config.languages)
        self.analyzer = Analyzer(self.config.languages, threshold_low=threshold_low, threshold_high=threshold_high)
        self.directories = directories
        # Report settings
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.problem_file_threshold = problem_file_threshold
        self.output_file = output_file
        self.level = level
        self.hierarchical = hierarchical
        self.output_format = output_format
        
        # Hotspot analysis settings
        self.list_hotspots = list_hotspots
        self.hotspot_threshold = hotspot_threshold
        self.hotspot_output = hotspot_output
        
        # Review strategy settings
        self.review_strategy = review_strategy
        self.review_output = review_output
        self.review_branch_only = review_branch_only
        self.review_base_branch = review_base_branch

        # Allow swapping report generator
        self.report_generator_cls = report_generator_cls or ReportGenerator

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
        # Generate one HTML report per repo_info
        for idx, repo_info in enumerate(repo_infos):
            output_file = self.output_file or "complexity_report.html"
            # If multiple repos, append index to filename
            if len(repo_infos) > 1:
                base, ext = os.path.splitext(output_file)
                output_file = f"{base}_{idx + 1}{ext}"
                # Mark the current as selected
                for link in report_links:
                    link['selected'] = (link['href'] == output_file)
                links_for_this = [link for link in report_links if link['href'] != output_file]
            else:
                links_for_this = report_links

            # All generators now accept a single repo_info object, making the call uniform.
            report = self.report_generator_cls(
                repo_info, self.threshold_low, self.threshold_high, self.problem_file_threshold
            )
            report.generate(
                output_file=output_file,
                level=self.level,
                hierarchical=self.hierarchical,
                output_format=self.output_format,
                report_links=links_for_this
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
            # Save to file
            save_hotspots_to_file(all_hotspots, self.hotspot_output, show_risk_categories=True)
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
                result['files'][filename] = {
                    'kpis': {
                        'complexity': getattr(file_obj.kpis.get('complexity'), 'value', 0) if file_obj.kpis.get('complexity') else 0,
                        'churn': getattr(file_obj.kpis.get('churn'), 'value', 0) if file_obj.kpis.get('churn') else 0,
                        'hotspot': getattr(file_obj.kpis.get('hotspot'), 'value', 0) if file_obj.kpis.get('hotspot') else 0
                    }
                }
            
            # Convert subdirectories
            for dirname, subdir in scandir.scan_dirs.items():
                result['scan_dirs'][dirname] = scandir_to_dict(subdir)
            
            return result
        
        return scandir_to_dict(repo_info)
    
    def _run_review_strategy_analysis(self, repo_infos):
        """
        Generate code review strategy report based on KPI metrics.
        
        Args:
            repo_infos: List of RepoInfo objects from analysis
        """
        from src.utilities.code_review_advisor import generate_review_report
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
        if self.review_branch_only and self.directories:
            try:
                repo_path = self.directories[0]
                current_branch = get_current_branch(repo_path)
                if current_branch:
                    print(f"\n🔍 Filtering review strategy to changed files in branch: {current_branch}")
                    print(f"   Comparing against base branch: {self.review_base_branch}")
                    filter_files = get_changed_files_in_branch(repo_path, self.review_base_branch)
                    if filter_files:
                        print(f"   Found {len(filter_files)} changed files")
                    else:
                        print(f"   ⚠️  No changed files found, showing all files")
            except Exception as e:
                print(f"   ⚠️  Could not determine changed files: {e}")
                debug_print(f"[DEBUG] Error getting changed files: {e}")
        
        # Generate the report
        try:
            report = generate_review_report(
                all_data, 
                output_file=self.review_output,
                filter_files=filter_files,
                branch_name=current_branch,
                base_branch=self.review_base_branch if self.review_branch_only else None
            )
            print(f"\n✅ Code review strategy report generated successfully!")
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
                file_data = {
                    'kpis': {
                        'complexity': getattr(file_obj.kpis.get('complexity'), 'value', 0) if file_obj.kpis.get('complexity') else 0,
                        'churn': getattr(file_obj.kpis.get('churn'), 'value', 0) if file_obj.kpis.get('churn') else 0,
                        'hotspot': getattr(file_obj.kpis.get('hotspot'), 'value', 0) if file_obj.kpis.get('hotspot') else 0
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
