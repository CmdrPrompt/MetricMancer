"""
Report Coordinator Module

Handles coordination of report generation across multiple formats and repositories.
Separates report generation logic from main application flow.
"""
import os
from typing import List, Dict, Any, Optional

from src.kpis.model import RepoInfo
from src.utilities.debug import debug_print


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
    
    @staticmethod
    def get_cli_format_details(output_format: str) -> Optional[str]:
        """
        Get base filename for CLI output formats.
        
        Args:
            output_format: Output format name
            
        Returns:
            Base filename or None if not a CLI format
        """
        format_map = {
            'summary': 'summary_report',
            'quick-wins': 'quick_wins_report',
            'human-tree': 'file_tree_report'
        }
        return format_map.get(output_format)
    
    @staticmethod
    def get_simple_format_extension(output_format: str) -> Optional[str]:
        """
        Get extension for simple formats (json, csv, html).
        
        Args:
            output_format: Output format name
            
        Returns:
            File extension or None if not a simple format
        """
        extensions = {
            'json': '.json',
            'machine': '.csv',
            'html': '.html'
        }
        return extensions.get(output_format)
    
    def get_file_extension_for_format(self, output_format: str, 
                                       is_multi_format: bool, base: str) -> tuple:
        """
        Get appropriate file extension and base name for output format.
        
        Args:
            output_format: Output format name
            is_multi_format: Whether multiple formats are being generated
            base: Base filename
            
        Returns:
            Tuple of (base_name, extension)
        """
        ext = os.path.splitext(self.output_file or "complexity_report.html")[1]
        
        simple_ext = self.get_simple_format_extension(output_format)
        if simple_ext:
            return base, simple_ext
        
        if output_format in ['summary', 'quick-wins', 'human-tree'] and is_multi_format:
            ext = '.md'
            cli_base = self.get_cli_format_details(output_format)
            if cli_base:
                base = cli_base
        
        return base, ext
    
    @staticmethod
    def get_output_filename(base: str, ext: str, idx: int, 
                           num_repos: int, report_links: List[Dict]) -> tuple:
        """
        Generate output filename and associated links for a report.
        
        Args:
            base: Base filename
            ext: File extension
            idx: Repository index
            num_repos: Total number of repositories
            report_links: List of report links
            
        Returns:
            Tuple of (output_filename, links_for_this_report)
        """
        if num_repos > 1:
            output_file = f"{base}_{idx + 1}{ext}"
            for link in report_links:
                link['selected'] = (link['href'] == output_file)
            links_for_this = [link for link in report_links if link['href'] != output_file]
        else:
            output_file = f"{base}{ext}"
            links_for_this = report_links
        
        return output_file, links_for_this
    
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
        output_path = os.path.join(self.report_folder, output_file)
        generator_cls = self.create_report_generator(output_format)
        
        report = generator_cls(
            repo_info, self.threshold_low, self.threshold_high, 
            self.problem_file_threshold
        )
        
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
        if output_format in ['review-strategy', 'review-strategy-branch']:
            if review_strategy_callback:
                review_branch_only = (output_format == 'review-strategy-branch')
                output_filename = ('review_strategy_branch.md' if review_branch_only
                                   else 'review_strategy.md')
                review_strategy_callback(repo_infos, review_branch_only, output_filename)
            return

        # Generate one report per repo_info for this format
        for idx, repo_info in enumerate(repo_infos):
            output_file = self.output_file or "complexity_report.html"
            base, ext = os.path.splitext(output_file)
            
            base, ext = self.get_file_extension_for_format(output_format, is_multi_format, base)
            output_file, links_for_this = self.get_output_filename(
                base, ext, idx, len(repo_infos), report_links
            )
            
            self.generate_single_report(
                repo_info, output_format, output_file, links_for_this, is_multi_format
            )
    
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
        report_links = []
        if len(repo_infos) > 1:
            for idx, repo_info in enumerate(repo_infos):
                base, ext = os.path.splitext(output_file or "complexity_report.html")
                filename = f"{base}_{idx + 1}{ext}"
                report_links.append({
                    'href': filename,
                    'name': getattr(repo_info, 'repo_name', f'Repo {idx + 1}'),
                    'selected': False
                })
        return report_links
