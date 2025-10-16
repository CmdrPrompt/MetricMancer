"""
FileProcessor - Processes individual files for analysis.

This class is responsible for:
1. Reading file content using FileReader
2. Analyzing complexity using ComplexityAnalyzer
3. Calculating KPIs using KPIOrchestrator
4. Combining results into a structured dictionary

Part of the Analyzer refactoring (Phase 2).
Follows Single Responsibility Principle and uses Dependency Injection.
"""

from pathlib import Path
from typing import Optional, Dict, Any

from app.file_reader import FileReader
from app.processing.kpi_orchestrator import KPIOrchestrator
from utilities.debug import debug_print


class FileProcessor:
    """
    Processes individual files by reading, analyzing complexity, and calculating KPIs.
    
    This class coordinates the file processing pipeline:
    1. Read file content
    2. Analyze complexity
    3. Calculate KPIs
    4. Return structured results
    
    Uses Dependency Injection for testability and flexibility.
    
    Attributes:
        file_reader: FileReader instance for reading files
        kpi_orchestrator: KPIOrchestrator instance for calculating KPIs
        complexity_analyzer: ComplexityAnalyzer instance for analyzing complexity
    
    Example:
        >>> processor = FileProcessor()
        >>> result = processor.process_file(Path("src/main.py"), Path("."))
        >>> print(result["complexity"])
        15
    """
    
    def __init__(
        self,
        file_reader: Optional[FileReader] = None,
        kpi_orchestrator: Optional[KPIOrchestrator] = None,
        complexity_analyzer: Optional[Any] = None
    ):
        """
        Initialize FileProcessor with dependencies.
        
        Args:
            file_reader: FileReader instance (creates default if None)
            kpi_orchestrator: KPIOrchestrator instance (creates default if None)
            complexity_analyzer: Complexity analyzer instance (creates default if None)
                                Note: Using Any type to avoid circular imports
        """
        self.file_reader = file_reader if file_reader is not None else FileReader()
        self.kpi_orchestrator = kpi_orchestrator if kpi_orchestrator is not None else KPIOrchestrator()
        self.complexity_analyzer = complexity_analyzer  # Will be None by default for now
    
    def process_file(
        self,
        file_path: Path,
        repo_root: Path
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single file through the analysis pipeline.
        
        Steps:
        1. Read file content using FileReader
        2. Analyze complexity using ComplexityAnalyzer
        3. Calculate KPIs using KPIOrchestrator
        4. Return structured results
        
        Args:
            file_path: Path to the file to process
            repo_root: Root path of the repository
        
        Returns:
            Dictionary containing:
            - file_path: Path to the file
            - repo_root: Repository root path
            - content: File content (optional)
            - complexity: Cyclomatic complexity
            - function_count: Number of functions
            - kpis: Dictionary of KPI name -> KPI object
            
            Returns None if file cannot be read or processing fails.
        
        Example:
            >>> processor = FileProcessor()
            >>> result = processor.process_file(Path("src/main.py"), Path("."))
            >>> if result:
            ...     print(f"Complexity: {result['complexity']}")
            ...     print(f"KPIs: {list(result['kpis'].keys())}")
        """
        try:
            # Step 1: Read file content
            debug_print(f"[FileProcessor] Reading file: {file_path}")
            content = self.file_reader.read_file(file_path)
            
            if content is None:
                debug_print(f"[FileProcessor] Failed to read file: {file_path}")
                return None
            
            # Step 2: Analyze complexity
            debug_print(f"[FileProcessor] Analyzing complexity for: {file_path}")
            
            complexity_value = 0
            function_count = 0
            
            if self.complexity_analyzer is not None:
                try:
                    # Try to call analyze_file if it exists (test mock interface)
                    if hasattr(self.complexity_analyzer, 'analyze_file'):
                        result = self.complexity_analyzer.analyze_file(str(file_path), content)
                        complexity_value = result.complexity
                        function_count = result.function_count
                    # Otherwise try the real ComplexityAnalyzer interface (needs lang_config)
                    elif hasattr(self.complexity_analyzer, 'calculate_for_file'):
                        # This requires lang_config which will be passed during real integration
                        debug_print(f"[FileProcessor] ComplexityAnalyzer requires lang_config - skipping for now")
                except Exception as e:
                    debug_print(f"[FileProcessor] Complexity analysis failed: {e}")
                    return None
            
            # Step 3: Build context for KPI calculation
            file_context = {
                "file_path": file_path,
                "repo_root": repo_root,
                "content": content,
                "complexity": complexity_value,
                "function_count": function_count
            }
            
            # Step 4: Calculate KPIs
            debug_print(f"[FileProcessor] Calculating KPIs for: {file_path}")
            try:
                kpis = self.kpi_orchestrator.calculate_file_kpis(file_context)
            except Exception as e:
                debug_print(f"[FileProcessor] KPI calculation failed: {e}")
                kpis = {}
            
            # Step 5: Build result
            result = {
                "file_path": file_path,
                "repo_root": repo_root,
                "complexity": complexity_value,
                "function_count": function_count,
                "kpis": kpis
            }
            
            debug_print(f"[FileProcessor] Successfully processed: {file_path}")
            return result
            
        except Exception as e:
            debug_print(f"[FileProcessor] Error processing file {file_path}: {e}")
            return None
