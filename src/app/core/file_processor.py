"""
FileProcessor - Processes individual files for analysis.

This class is part of Phase 5 of the analyzer.py refactoring.
Extracts file processing logic into dedicated component.

Responsibilities:
1. Reading file content with error handling
2. Analyzing function complexity
3. Calculating KPIs (churn, ownership, hotspot)
4. Creating File objects with complete KPI data
5. Tracking timing for each operation

GREEN PHASE: Minimum implementation to pass tests.
"""

import time
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from src.kpis.complexity import ComplexityKPI, ComplexityAnalyzer
from src.kpis.codechurn import ChurnKPI
from src.kpis.codeownership import CodeOwnershipKPI
from src.kpis.hotspot import HotspotKPI
from src.kpis.model import File, Function
from src.kpis.sharedcodeownership.shared_code_ownership import SharedOwnershipKPI
from src.kpis.codeownership.fallback_kpi import FallbackCodeOwnershipKPI
from src.kpis.sharedcodeownership.fallback_kpi import FallbackSharedOwnershipKPI
from src.utilities.debug import debug_print


class FileProcessor:
    """
    Processes individual files: read, analyze, calculate KPIs.

    Coordinates file-level operations extracted from analyzer.py.
    Follows Single Responsibility Principle.
    """

    def __init__(self, complexity_analyzer: ComplexityAnalyzer, lang_config: dict):
        """
        Initialize FileProcessor with dependencies.

        Args:
            complexity_analyzer: ComplexityAnalyzer instance for function analysis
            lang_config: Language configuration for parsing
        """
        self.complexity_analyzer = complexity_analyzer
        self.lang_config = lang_config

    def read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content with error handling.

        Args:
            file_path: Path to file to read

        Returns:
            str: File content, or None if reading fails
        """
        try:
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            debug_print(f"[WARN] Unable to read {file_path}: {e}")
            return None

    def analyze_functions_complexity(
        self,
        content: str,
        lang_config: dict
    ) -> Tuple[List[Function], float, float]:
        """
        Analyze functions in file content and return complexity metrics.

        Args:
            content: File content to analyze
            lang_config: Language configuration for parsing

        Returns:
            tuple: (function_objects, total_complexity, elapsed_time)
        """
        t_start = time.perf_counter()
        functions_data = self.complexity_analyzer.analyze_functions(content, lang_config)
        t_end = time.perf_counter()

        function_objects = []
        total_complexity = 0

        for func_data in functions_data:
            func_complexity = func_data.get('complexity', 0)
            func_complexity_kpi = ComplexityKPI().calculate(
                complexity=func_complexity,
                function_count=1
            )
            total_complexity += func_complexity_kpi.value
            function_objects.append(
                Function(
                    name=func_data.get('name', 'N/A'),
                    kpis={func_complexity_kpi.name: func_complexity_kpi}
                )
            )

        return function_objects, total_complexity, t_end - t_start

    def calculate_churn_kpi(
        self,
        file_path: Path,
        repo_root_path: Path
    ) -> Tuple[ChurnKPI, float]:
        """
        Calculate churn KPI for a file.

        Args:
            file_path: Path to file
            repo_root_path: Repository root path

        Returns:
            tuple: (churn_kpi, elapsed_time)
        """
        t_start = time.perf_counter()
        relative_path = str(file_path.relative_to(repo_root_path))
        debug_print(f"[DEBUG] Looking up churn for file_path: {relative_path}")

        churn_kpi = ChurnKPI().calculate(
            file_path=str(file_path),
            repo_root=str(repo_root_path.resolve())
        )

        t_end = time.perf_counter()
        debug_print(f"[DEBUG] Setting churn for: {relative_path}: {churn_kpi.value}")

        return churn_kpi, t_end - t_start

    def calculate_ownership_kpis(
        self,
        file_path: Path,
        repo_root_path: Path
    ) -> Tuple[CodeOwnershipKPI, SharedOwnershipKPI, float, float]:
        """
        Calculate code ownership and shared ownership KPIs.

        Args:
            file_path: Path to file
            repo_root_path: Repository root path

        Returns:
            tuple: (code_ownership_kpi, shared_ownership_kpi, ownership_time, shared_time)
        """
        # Code Ownership KPI
        t_ownership_start = time.perf_counter()
        try:
            code_ownership_kpi = CodeOwnershipKPI(
                file_path=str(file_path.resolve()),
                repo_root=str(repo_root_path.resolve())
            )
        except Exception as e:
            code_ownership_kpi = FallbackCodeOwnershipKPI(str(e))
        t_ownership_end = time.perf_counter()

        # Shared Ownership KPI
        t_shared_start = time.perf_counter()
        try:
            shared_ownership_kpi = SharedOwnershipKPI(
                file_path=str(file_path.resolve()),
                repo_root=str(repo_root_path.resolve())
            )
        except Exception as e:
            shared_ownership_kpi = FallbackSharedOwnershipKPI(str(e))
        t_shared_end = time.perf_counter()

        return (code_ownership_kpi, shared_ownership_kpi,
                t_ownership_end - t_ownership_start,
                t_shared_end - t_shared_start)

    def process_file(
        self,
        file_info: Dict[str, Any],
        repo_root_path: Path
    ) -> Tuple[Optional[File], Dict[str, float]]:
        """
        Process single file: read, analyze, calculate KPIs.

        This is the main method that coordinates all file processing operations.

        Args:
            file_info: Dictionary with file information (path, ext, etc.)
            repo_root_path: Repository root path

        Returns:
            tuple: (File object with KPIs, timing dict) or (None, empty dict) if processing fails
        """
        file_path = Path(file_info['path'])
        ext = file_info.get('ext')

        # Initialize timing dict
        timing = {
            'complexity': 0.0,
            'filechurn': 0.0,
            'ownership': 0.0,
            'sharedownership': 0.0
        }

        # 1. Read file content
        content = self.read_file_content(file_path)
        if content is None:
            debug_print(f"[WARN] Skipping file {file_path} - could not read content")
            return (None, timing)

        # 2. Get language-specific config for this file extension
        lang_config = self.lang_config.get(ext)
        if lang_config is None:
            debug_print(f"[WARN] No language config found for extension: {ext}")
            return (None, timing)

        # 3. Analyze function complexity
        functions, total_complexity, complexity_time = self.analyze_functions_complexity(
            content, lang_config
        )
        timing['complexity'] = complexity_time

        # 4. Calculate churn KPI
        churn_kpi, churn_time = self.calculate_churn_kpi(file_path, repo_root_path)
        timing['filechurn'] = churn_time

        # 5. Calculate ownership KPIs
        code_ownership_kpi, shared_ownership_kpi, ownership_time, shared_time = \
            self.calculate_ownership_kpis(file_path, repo_root_path)
        timing['ownership'] = ownership_time
        timing['sharedownership'] = shared_time

        # 6. Calculate hotspot KPI (before creating file complexity KPI)
        # Note: HotspotKPI expects complexity and churn parameters
        hotspot_kpi = HotspotKPI().calculate(
            complexity=int(total_complexity),
            churn=int(churn_kpi.value)
        )

        # 7. Create File object with all KPIs
        # Calculate file-level complexity KPI with function count
        file_complexity_kpi = ComplexityKPI().calculate(
            complexity=int(total_complexity),  # Convert to int
            function_count=len(functions)
        )

        file_obj = File(
            name=file_path.name,
            file_path=str(file_path),
            functions=functions,
            kpis={
                file_complexity_kpi.name: file_complexity_kpi,
                churn_kpi.name: churn_kpi,
                hotspot_kpi.name: hotspot_kpi,
                code_ownership_kpi.name: code_ownership_kpi,
                shared_ownership_kpi.name: shared_ownership_kpi
            }
        )

        return file_obj, timing
