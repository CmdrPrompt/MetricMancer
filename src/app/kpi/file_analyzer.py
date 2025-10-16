"""
File Analyzer - Analyzes individual files and calculates KPIs

Single Responsibility: File-level analysis only.
Delegates KPI calculation to KPICalculator (Strategy pattern).

Part of analyzer.py refactoring (Phase 2).
"""
from pathlib import Path
from typing import Dict, List, Optional

from src.kpis.model import File, Function
from src.kpis.complexity import ComplexityKPI
from src.utilities.debug import debug_print
from src.app.kpi.kpi_calculator import KPICalculator


class FileAnalyzer:
    """
    Analyzes individual files for complexity and KPIs.
    
    Responsibilities:
    - Read and validate file content
    - Parse functions with complexity analyzer (via KPICalculator)
    - Create File and Function objects
    - Calculate all file-level KPIs
    
    Does NOT:
    - Group files by repository (RepoGrouper's job)
    - Build directory hierarchy (HierarchyBuilder's job)
    - Aggregate KPIs (KPIAggregator's job)
    
    Usage:
        analyzer = FileAnalyzer(languages_config, kpi_calculator)
        file_obj = analyzer.analyze_file(file_info, repo_root)
    """
    
    def __init__(self, languages_config: Dict, kpi_calculator: KPICalculator):
        """
        Initialize FileAnalyzer.
        
        Args:
            languages_config: Dict mapping file extensions to language configs
                             Example: {'.py': {'parser': 'python', ...}}
            kpi_calculator: KPICalculator instance for calculating KPIs
        """
        self.config = languages_config
        self.kpi_calculator = kpi_calculator
    
    def analyze_file(
        self,
        file_info: Dict,
        repo_root: Path
    ) -> Optional[File]:
        """
        Analyze a single file and return File object with KPIs.
        
        This is the main entry point for per-file analysis. It orchestrates:
        1. File validation and reading
        2. Function parsing (via complexity analyzer)
        3. KPI calculation (via KPICalculator)
        4. File and Function object creation
        
        Args:
            file_info: Dict with keys:
                      - 'path': Absolute path to file
                      - 'ext': File extension (e.g., '.py')
            repo_root: Path to repository root directory
        
        Returns:
            File object with calculated KPIs and functions
            None if file cannot be analyzed (invalid extension, read error, etc.)
        
        Example:
            file_info = {'path': '/repo/src/main.py', 'ext': '.py'}
            repo_root = Path('/repo')
            file_obj = analyzer.analyze_file(file_info, repo_root)
            # file_obj.kpis = {'complexity': ..., 'churn': ..., ...}
            # file_obj.functions = [Function(...), ...]
        """
        file_path = Path(file_info['path'])
        ext = file_info.get('ext')
        
        # Step 1: Validate file extension
        if not self._is_supported_extension(ext):
            debug_print(
                f"FileAnalyzer: Skipping file with unknown extension: "
                f"{str(file_path.resolve())}"
            )
            return None
        
        # Step 2: Read file content
        content = self._read_file_content(file_path)
        if content is None:
            return None
        
        # Step 3: Get language configuration
        lang_config = self.config[ext]
        
        # Step 4: Analyze functions in the file
        functions_data = self.kpi_calculator.complexity_analyzer.analyze_functions(
            content, lang_config
        )
        
        # Step 5: Create Function objects with complexity KPIs
        function_objects = self._create_function_objects(functions_data)
        
        # Step 6: Calculate all file-level KPIs
        file_kpis = self.kpi_calculator.calculate_all(
            file_info=file_info,
            repo_root=repo_root,
            content=content,
            functions_data=functions_data
        )
        
        # Step 7: Create and return File object
        file_obj = File(
            name=file_path.name,
            file_path=str(file_path.relative_to(repo_root)),
            kpis=file_kpis,
            functions=function_objects
        )
        
        return file_obj
    
    def _is_supported_extension(self, ext: str) -> bool:
        """
        Check if file extension is supported.
        
        Args:
            ext: File extension (e.g., '.py', '.java')
        
        Returns:
            True if extension is in config, False otherwise
        """
        return ext in self.config
    
    def _read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content with error handling.
        
        Args:
            file_path: Path to file
        
        Returns:
            File content as string
            None if file cannot be read
        """
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            debug_print(f"[WARN] Unable to read {file_path}: {e}")
            return None
    
    def _create_function_objects(
        self,
        functions_data: List[Dict]
    ) -> List[Function]:
        """
        Create Function objects with complexity KPIs.
        
        Args:
            functions_data: List of dicts with keys:
                          - 'name': Function name
                          - 'complexity': Cyclomatic complexity value
        
        Returns:
            List of Function objects with complexity KPIs
        
        Example:
            functions_data = [
                {'name': 'main', 'complexity': 5},
                {'name': 'helper', 'complexity': 2}
            ]
            # Returns: [
            #   Function(name='main', kpis={'complexity': ComplexityKPI(5)}),
            #   Function(name='helper', kpis={'complexity': ComplexityKPI(2)})
            # ]
        """
        function_objects = []
        
        for func_data in functions_data:
            # Create complexity KPI for this function
            func_complexity_kpi = ComplexityKPI().calculate(
                complexity=func_data.get('complexity', 0),
                function_count=1
            )
            
            # Create Function object
            function_objects.append(
                Function(
                    name=func_data.get('name', 'N/A'),
                    kpis={func_complexity_kpi.name: func_complexity_kpi}
                )
            )
        
        return function_objects
    
    def analyze_multiple_files(
        self,
        files_info: List[Dict],
        repo_root: Path
    ) -> List[File]:
        """
        Analyze multiple files and return list of File objects.
        
        This is a convenience method for batch processing.
        Filters out files that fail analysis (returns None).
        
        Args:
            files_info: List of file info dicts
            repo_root: Repository root path
        
        Returns:
            List of successfully analyzed File objects
            (excludes files that returned None)
        
        Example:
            files_info = [
                {'path': '/repo/a.py', 'ext': '.py'},
                {'path': '/repo/b.py', 'ext': '.py'},
                {'path': '/repo/c.txt', 'ext': '.txt'}  # Not supported
            ]
            results = analyzer.analyze_multiple_files(files_info, Path('/repo'))
            # Returns: [File('a.py'), File('b.py')]  (c.txt filtered out)
        """
        analyzed_files = []
        
        for file_info in files_info:
            file_obj = self.analyze_file(file_info, repo_root)
            if file_obj is not None:
                analyzed_files.append(file_obj)
        
        return analyzed_files
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about analysis operations.
        
        Returns timing information from KPICalculator.
        
        Returns:
            Dict with keys:
            - 'kpi_timing': Dict of KPI name → cumulative time
            - 'total_kpi_time': Sum of all KPI calculation times
        
        Example:
            stats = analyzer.get_statistics()
            # {
            #     'kpi_timing': {
            #         'complexity': 0.123,
            #         'churn': 0.456,
            #         'hotspot': 0.001,
            #         ...
            #     },
            #     'total_kpi_time': 0.580
            # }
        """
        kpi_timing = self.kpi_calculator.get_timing_report()
        total_time = sum(kpi_timing.values())
        
        return {
            'kpi_timing': kpi_timing,
            'total_kpi_time': total_time
        }
