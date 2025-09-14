import os
from collections import defaultdict
from typing import List, Union

from src.kpis.model import RepoInfo, ScanDir, File, Function
from src.kpis.codechurn import ChurnKPI
from src.kpis.codechurn.code_churn import CodeChurnAnalyzer
from src.kpis.complexity import ComplexityAnalyzer, ComplexityKPI
from src.kpis.hotspot import HotspotKPI
from pathlib import Path

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
        from src.utilities.debug import debug_print

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
        complexity_analyzer = ComplexityAnalyzer()
        
        # 3. Build the hierarchical data model and calculate KPIs
        for file_info in files_in_repo:
            file_path = Path(file_info['path'])
            ext = file_info.get('ext')
            if ext not in self.config:
                debug_print(f"_analyze_repo: Skipping file with unknown extension: {file_path}")
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
            churn_kpi = ChurnKPI().calculate(file_path=str(file_path), churn_data=churn_data)

            hotspot_kpi = HotspotKPI().calculate(complexity=file_complexity_kpi.value, churn=churn_kpi.value)

            # Create the File object
            file_obj = File(
                name=file_path.name,
                file_path=str(file_path.relative_to(repo_root_path)),
                kpis={
                    file_complexity_kpi.name: file_complexity_kpi,
                    churn_kpi.name: churn_kpi,
                    hotspot_kpi.name: hotspot_kpi
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

        # Add logic to aggregate KPIs up the hierarchy (from File -> ScanDir -> RepoInfo)
        return repo_info

    def analyze(self, files):
        """Analyzes a list of files, groups them by repository, and returns a summary."""
        from src.utilities.debug import debug_print

        if not files:
            return {}

        files_by_root, scan_dirs_by_root = self._group_files_by_repo(files)
        debug_print(f"[DEBUG] Analyzer: Found {len(files_by_root)} repositories to analyze.")

        summary = {}
        for repo_root in sorted(files_by_root.keys()):
            summary[repo_root] = self._analyze_repo(
                repo_root, files_by_root[repo_root], list(scan_dirs_by_root[repo_root])
            )

        return summary
