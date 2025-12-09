"""
Filename Generator Module

Handles generation of output filenames for different formats and repositories.
Extracted from report_coordinator.py to reduce complexity.
"""
import os
from typing import List, Dict, Tuple

from src.app.coordination.format_mapper import FormatMapper


class FileNameGenerator:
    """
    Generates appropriate filenames for report outputs.
    
    Responsibilities:
    - Generate filenames based on format and repository count
    - Handle multi-repository filename numbering
    - Manage file extensions based on format type
    - Prepare cross-repository links
    """
    
    def __init__(self, default_output_file: str, using_output_formats_flag: bool):
        """
        Initialize FileNameGenerator.
        
        Args:
            default_output_file: Default output filename
            using_output_formats_flag: Whether --output-formats flag was used
        """
        self.default_output_file = default_output_file
        self.using_output_formats_flag = using_output_formats_flag
    
    def get_base_and_extension(self, output_format: str, is_multi_format: bool) -> Tuple[str, str]:
        """
        Get appropriate base name and extension for output format.
        
        Args:
            output_format: Output format name
            is_multi_format: Whether multiple formats are being generated
            
        Returns:
            Tuple of (base_name, extension)
        """
        # Start with default file parts
        base, ext = os.path.splitext(self.default_output_file or "complexity_report.html")
        
        # Check for simple formats first (json, csv, html)
        simple_ext = FormatMapper.get_extension(output_format)
        if simple_ext:
            return base, simple_ext
        
        # Check for CLI formats that need markdown extension
        if FormatMapper.is_cli_format(output_format):
            if is_multi_format or self.using_output_formats_flag:
                ext = '.md'
                cli_base = FormatMapper.get_cli_base_name(output_format)
                if cli_base:
                    base = cli_base
        
        return base, ext
    
    def generate_filename(self, base: str, ext: str, repo_index: int, 
                         total_repos: int) -> str:
        """
        Generate output filename with optional repository index.
        
        Args:
            base: Base filename without extension
            ext: File extension with dot
            repo_index: Current repository index (0-based)
            total_repos: Total number of repositories
            
        Returns:
            Generated filename
        """
        if total_repos > 1:
            return f"{base}_{repo_index + 1}{ext}"
        return f"{base}{ext}"
    
    def generate_with_links(self, base: str, ext: str, repo_index: int,
                          total_repos: int, report_links: List[Dict]) -> Tuple[str, List[Dict]]:
        """
        Generate filename and update cross-repository links.
        
        Args:
            base: Base filename without extension
            ext: File extension with dot
            repo_index: Current repository index (0-based)
            total_repos: Total number of repositories
            report_links: List of report link dictionaries
            
        Returns:
            Tuple of (filename, links_for_this_report)
        """
        filename = self.generate_filename(base, ext, repo_index, total_repos)
        
        if total_repos > 1:
            # Mark current report as selected
            for link in report_links:
                link['selected'] = (link['href'] == filename)
            # Exclude self from links
            links_for_this = [link for link in report_links if link['href'] != filename]
        else:
            links_for_this = report_links
        
        return filename, links_for_this
    
    @staticmethod
    def prepare_report_links(repo_infos: List, default_output_file: str) -> List[Dict]:
        """
        Prepare cross-links for multi-repository reports.
        
        Args:
            repo_infos: List of repository information objects
            default_output_file: Base output filename
            
        Returns:
            List of report link dictionaries
        """
        report_links = []
        
        if len(repo_infos) > 1:
            base, ext = os.path.splitext(default_output_file or "complexity_report.html")
            
            for idx, repo_info in enumerate(repo_infos):
                filename = f"{base}_{idx + 1}{ext}"
                report_links.append({
                    'href': filename,
                    'name': getattr(repo_info, 'repo_name', f'Repo {idx + 1}'),
                    'selected': False
                })
        
        return report_links
