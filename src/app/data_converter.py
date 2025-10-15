"""
Data Converter Module

Handles conversion of RepoInfo objects to dictionary format
for various analysis and reporting purposes.
"""
from typing import Dict, Any
from src.kpis.model import RepoInfo, ScanDir, File


class DataConverter:
    """
    Converts RepoInfo and related objects to dictionary format.
    
    Separates the concern of data transformation from application logic.
    """
    
    @staticmethod
    def extract_kpi_values(file_obj: File) -> Dict[str, float]:
        """
        Extract KPI values from a file object.
        
        Args:
            file_obj: File object containing KPIs
            
        Returns:
            Dictionary with complexity, churn, and hotspot values
        """
        complexity_kpi = file_obj.kpis.get('complexity')
        churn_kpi = file_obj.kpis.get('churn')
        hotspot_kpi = file_obj.kpis.get('hotspot')
        
        return {
            'complexity': getattr(complexity_kpi, 'value', 0) if complexity_kpi else 0,
            'churn': getattr(churn_kpi, 'value', 0) if churn_kpi else 0,
            'hotspot': getattr(hotspot_kpi, 'value', 0) if hotspot_kpi else 0
        }
    
    @staticmethod
    def extract_ownership_data(file_obj: File) -> Dict[str, Any]:
        """
        Extract ownership data from a file object if available.
        
        Args:
            file_obj: File object containing ownership KPI
            
        Returns:
            Ownership data dictionary or None if not available
        """
        ownership_kpi = file_obj.kpis.get('ownership')
        if ownership_kpi and hasattr(ownership_kpi, 'calculation_values'):
            ownership_data = ownership_kpi.calculation_values.get('ownership', {})
            if ownership_data:
                return ownership_data
        return None
    
    @staticmethod
    def convert_file_to_dict(file_obj: File) -> Dict[str, Any]:
        """
        Convert a single file object to dict format with KPIs.
        
        Args:
            file_obj: File object to convert
            
        Returns:
            Dictionary with KPI data
        """
        return {'kpis': DataConverter.extract_kpi_values(file_obj)}
    
    @staticmethod
    def convert_file_to_dict_with_ownership(file_obj: File) -> Dict[str, Any]:
        """
        Convert a single file object to dict format with ownership.
        
        Args:
            file_obj: File object to convert
            
        Returns:
            Dictionary with KPI and ownership data
        """
        file_data = {'kpis': DataConverter.extract_kpi_values(file_obj)}
        
        ownership_data = DataConverter.extract_ownership_data(file_obj)
        if ownership_data:
            file_data['ownership'] = ownership_data
        
        return file_data
    
    @staticmethod
    def convert_scandir_to_dict(scandir: ScanDir) -> Dict[str, Any]:
        """
        Recursively convert ScanDir to dict.
        
        Args:
            scandir: ScanDir object to convert
            
        Returns:
            Dictionary representation of the directory tree
        """
        result = {
            'files': {},
            'scan_dirs': {}
        }

        # Convert files
        for filename, file_obj in scandir.files.items():
            result['files'][filename] = DataConverter.convert_file_to_dict(file_obj)

        # Convert subdirectories recursively
        for dirname, subdir in scandir.scan_dirs.items():
            result['scan_dirs'][dirname] = DataConverter.convert_scandir_to_dict(subdir)

        return result
    
    @staticmethod
    def convert_scandir_to_dict_with_ownership(scandir: ScanDir) -> Dict[str, Any]:
        """
        Recursively convert ScanDir to dict with ownership.
        
        Args:
            scandir: ScanDir object to convert
            
        Returns:
            Dictionary representation with ownership data
        """
        result = {
            'files': {},
            'scan_dirs': {}
        }

        # Convert files
        for filename, file_obj in scandir.files.items():
            result['files'][filename] = DataConverter.convert_file_to_dict_with_ownership(file_obj)

        # Convert subdirectories recursively
        for dirname, subdir in scandir.scan_dirs.items():
            result['scan_dirs'][dirname] = DataConverter.convert_scandir_to_dict_with_ownership(subdir)

        return result
    
    @staticmethod
    def convert_repo_info_to_dict(repo_info: RepoInfo) -> Dict[str, Any]:
        """
        Convert RepoInfo object to dictionary format compatible with hotspot analysis.
        
        Args:
            repo_info: RepoInfo object from analysis
            
        Returns:
            Dictionary representation suitable for hotspot extraction
        """
        return DataConverter.convert_scandir_to_dict(repo_info)
    
    @staticmethod
    def convert_repo_info_to_dict_with_ownership(repo_info: RepoInfo) -> Dict[str, Any]:
        """
        Convert RepoInfo object to dictionary format with ownership data.
        
        Args:
            repo_info: RepoInfo object from analysis
            
        Returns:
            Dictionary representation with KPIs and ownership data
        """
        return DataConverter.convert_scandir_to_dict_with_ownership(repo_info)
