import os
from collections import defaultdict
from pathlib import Path
from typing import List, Union

from src.kpis.base_kpi import BaseKPI
from src.kpis.codeownership import CodeOwnershipKPI
from src.kpis.codechurn import ChurnKPI
from src.kpis.codechurn.code_churn import CodeChurnAnalyzer
from src.kpis.complexity import ComplexityAnalyzer, ComplexityKPI
from src.kpis.hotspot import HotspotKPI
from src.kpis.model import RepoInfo, ScanDir, File, Function
from src.kpis.sharedcodeownership.shared_code_ownership import SharedOwnershipKPI
from src.utilities.debug import debug_print


class Analyzer:
    def __init__(self, languages_config, threshold_low=10.0, threshold_high=20.0):
        self.config = languages_config
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def _group_files_by_repo(self, files):
        """Groups files by their repository root directory."""
        files_by_root = defaultdict(list)
        scan_dirs_by_root = defaultdict(set)
        for file in files:
            repo_root = file.get('root', '')
            files_by_root[repo_root].append(file)
            scan_dirs_by_root[repo_root].add(repo_root)
        return files_by_root, scan_dirs_by_root

    def _analyze_repo(self, repo_root, files_in_repo, scan_dirs):
        """Analyzes a single repository's files for complexity, churn, and other metrics."""
        debug_print(f"[DEBUG] Analyzing repo: {repo_root} with {len(files_in_repo)} files.")

        repo_root_path = Path(repo_root)
        # 1. Create the top-level object for the repo
        repo_info = RepoInfo(
            repo_root_path=repo_root,
            repo_name=repo_root_path.name,
            dir_name=repo_root_path.name,
            scan_dir_path="."
        )

        # 2. Collect churn data for all files in the repo
        churn_analyzer = CodeChurnAnalyzer([(repo_root, d) for d in scan_dirs])
        churn_data = churn_analyzer.analyze()
        debug_print(f"[DEBUG] churn_data after analyze: {churn_data}")
        debug_print(f"[DEBUG] churn_data keys after analyze: {list(churn_data.keys())}")
        complexity_analyzer = ComplexityAnalyzer()

        # 3. Build the hierarchical data model and calculate KPIs
        if not files_in_repo:
            debug_print(f"[DEBUG] No files to analyze for repo: {repo_root}, returning None.")
            return None
        for file_info in files_in_repo:
            file_path = Path(file_info['path'])
            ext = file_info.get('ext')
            if ext not in self.config:
                # Always print absolute path with correct separator for platform
                debug_print(f"_analyze_repo: Skipping file with unknown extension: {str(file_path.resolve())}")
                continue

            # Read file content for complexity analysis
            try:
                with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                debug_print(f"[WARN] Unable to read {file_path}: {e}")
                continue

            # Create and populate KPI objects for the file
            lang_config = self.config[ext]

            # Analyze functions in the file
            functions_data = complexity_analyzer.analyze_functions(content, lang_config)

            function_objects = []
            total_complexity = 0
            for func_data in functions_data:
                func_complexity_kpi = ComplexityKPI().calculate(complexity=func_data.get('complexity', 0), function_count=1)
                total_complexity += func_complexity_kpi.value

                # (Future) Churn per function can be added here
                
                function_objects.append(
                    Function(name=func_data.get('name', 'N/A'), kpis={func_complexity_kpi.name: func_complexity_kpi})
                )

            # Aggregate KPIs for the entire file
            file_complexity_kpi = ComplexityKPI().calculate(complexity=total_complexity, function_count=len(function_objects))

            # Create and calculate ChurnKPI efficiently
            debug_print(f"[DEBUG] churn_data keys: {list(churn_data.keys())}")
            debug_print(f"[DEBUG] Looking up churn for file_path: {file_path}")
            churn_kpi = ChurnKPI().calculate(file_path=str(file_path), churn_data=churn_data)
            debug_print(f"[DEBUG] Setting churn for:              {file_path}: {churn_kpi.value}")

            hotspot_kpi = HotspotKPI().calculate(complexity=file_complexity_kpi.value, churn=churn_kpi.value)

            # --- Code Ownership KPI ---
            try:
                code_ownership_kpi = CodeOwnershipKPI(file_path=str(file_path.resolve()), repo_root=str(repo_root_path.resolve()))
            except Exception as e:
                from src.kpis.base_kpi import BaseKPI

                class FallbackCodeOwnershipKPI(BaseKPI):
                    def __init__(self):
                        super().__init__(
                            name="Code Ownership",
                            value={"error": f"Could not calculate: {e}"},
                            description="Proportion of code lines owned by each author (via git blame)"
                        )
 
                    def calculate(self, *args, **kwargs):
                        return self.value
                code_ownership_kpi = FallbackCodeOwnershipKPI()

            # --- Shared Ownership KPI ---
            try:
                shared_ownership_kpi = SharedOwnershipKPI(file_path=str(file_path.resolve()), repo_root=str(repo_root_path.resolve()))
            except Exception as e:
                from src.kpis.base_kpi import BaseKPI

                class FallbackSharedOwnershipKPI(BaseKPI):
                    def __init__(self):
                        super().__init__(
                            name="Shared Ownership",
                            value={"error": f"Could not calculate: {e}"},
                            description="Number of significant authors per file (ownership > threshold)"
                        )
                    
                    def calculate(self, *args, **kwargs):
                        return self.value
                shared_ownership_kpi = FallbackSharedOwnershipKPI()

            # Create the File object
            file_obj = File(
                name=file_path.name,
                file_path=str(file_path.relative_to(repo_root_path)),
                kpis={
                    file_complexity_kpi.name: file_complexity_kpi,
                    churn_kpi.name: churn_kpi,
                    hotspot_kpi.name: hotspot_kpi,
                    code_ownership_kpi.name: code_ownership_kpi,
                    shared_ownership_kpi.name: shared_ownership_kpi
                },
                functions=function_objects
            )

            # Find or create ScanDir objects in the hierarchy
            relative_dir_path = file_path.relative_to(repo_root_path).parent
            current_dir_container = repo_info
            path_parts = [part for part in relative_dir_path.parts if part and part != '.']
    
            if not path_parts:
                # The file is in the root directory of the repo
                repo_info.files[file_obj.name] = file_obj
            else:
                # The file is in a subdirectory, navigate there
                current_path = Path()
                for part in path_parts:
                    current_path = current_path / part
                    if part not in current_dir_container.scan_dirs:
                        current_dir_container.scan_dirs[part] = ScanDir(
                            dir_name=part, 
                            scan_dir_path=str(current_path),
                            repo_root_path=repo_info.repo_root_path,
                            repo_name=repo_info.repo_name
                        )
                    current_dir_container = current_dir_container.scan_dirs[part]
                current_dir_container.files[file_obj.name] = file_obj

        # TODO: Add logic to aggregate KPIs up the hierarchy (from File -> ScanDir -> RepoInfo)
        debug_print(f"[DEBUG] Returning repo_info for {repo_root}: {repo_info}")
        return repo_info

    def analyze(self, files):
        """Analyzes a list of files, groups them by repository, and returns a summary."""
        if not files:
            return {}

        files_by_root, scan_dirs_by_root = self._group_files_by_repo(files)
        debug_print(f"[DEBUG] Analyzer: Found {len(files_by_root)} repositories to analyze.")

        summary = {}
        for repo_root in sorted(files_by_root.keys()):
            repo_info = self._analyze_repo(
                repo_root, files_by_root[repo_root], list(scan_dirs_by_root[repo_root])
            )
            if repo_info is not None:
                summary[repo_root] = repo_info

        return summary
