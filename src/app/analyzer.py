from collections import defaultdict
from pathlib import Path
from tqdm import tqdm

from src.app.hierarchy_builder import HierarchyBuilder
from src.kpis.base_kpi import BaseKPI
from src.kpis.codeownership import CodeOwnershipKPI
from src.kpis.codechurn import ChurnKPI
from src.kpis.complexity import ComplexityAnalyzer, ComplexityKPI
from src.kpis.hotspot import HotspotKPI
from src.kpis.model import RepoInfo, ScanDir, File, Function
from src.kpis.sharedcodeownership.shared_code_ownership import (
    SharedOwnershipKPI
)
from src.utilities.debug import debug_print


class AggregatedSharedOwnershipKPI(BaseKPI):
    """Aggregated version of SharedOwnershipKPI for directory aggregation."""

    def calculate(self, *args, **kwargs):
        return self.value


class Analyzer:
    def __init__(self, languages_config, threshold_low=10.0,
                 threshold_high=20.0, churn_time_period_months=6):
        self.config = languages_config
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.churn_time_period_months = churn_time_period_months
        self.hierarchy_builder = HierarchyBuilder()

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

        import time
        # Initialize accumulators for timing
        if not hasattr(self, 'timing'):  # Set on first repo analysis
            self.timing = {
                'cache_prebuild': 0.0,
                'complexity': 0.0,
                'filechurn': 0.0,
                'hotspot': 0.0,
                'ownership': 0.0,
                'sharedownership': 0.0
            }

        # 2. Pre-build cache before KPI calculation (Issue #40)
        t_prefetch_start = time.perf_counter()
        from src.utilities.git_cache import get_git_cache
        git_cache = get_git_cache()

        # Collect all file paths for cache pre-building
        file_paths = [
            str(Path(file_info['path']).relative_to(repo_root_path))
            for file_info in files_in_repo
        ]
        debug_print(f"[PREBUILD] Pre-building cache for {len(file_paths)} "
                    f"files")
        git_cache.prebuild_cache_for_files(
            str(repo_root_path.resolve()), file_paths
        )
        t_prefetch_end = time.perf_counter()
        self.timing['cache_prebuild'] += t_prefetch_end - t_prefetch_start
        debug_print(f"[PREBUILD] Cache pre-building completed in "
                    f"{t_prefetch_end - t_prefetch_start:.3f} seconds")

        # Legacy churn_data for backward compatibility (cache handles churn)
        complexity_analyzer = ComplexityAnalyzer()

        # 3. Build the hierarchical data model and calculate KPIs
        if not files_in_repo:
            debug_print(f"[DEBUG] No files to analyze for repo: {repo_root}, returning None.")
            return None
        for file_info in tqdm(files_in_repo, desc=f"Analyzing files in {repo_root_path.name}", unit="file"):
            file_path = Path(file_info['path'])
            ext = file_info.get('ext')
            if ext not in self.config:
                # Always print absolute path with correct separator for platform
                debug_print(f"_analyze_repo: Skipping file with unknown "
                            f"extension: {str(file_path.resolve())}")
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
            t_complexity_start = time.perf_counter()
            functions_data = complexity_analyzer.analyze_functions(
                content, lang_config
            )
            t_complexity_end = time.perf_counter()
            self.timing['complexity'] += (
                t_complexity_end - t_complexity_start
            )

            function_objects = []
            total_complexity = 0
            for func_data in functions_data:
                func_complexity_kpi = ComplexityKPI().calculate(
                    complexity=func_data.get('complexity', 0),
                    function_count=1
                )
                total_complexity += func_complexity_kpi.value
                function_objects.append(
                    Function(
                        name=func_data.get('name', 'N/A'),
                        kpis={func_complexity_kpi.name: func_complexity_kpi}
                    )
                )

            # Aggregate KPIs for the entire file
            file_complexity_kpi = ComplexityKPI().calculate(
                complexity=total_complexity,
                function_count=len(function_objects)
            )

            # Create and calculate ChurnKPI using git cache (Issue #41)
            t_filechurn_start = time.perf_counter()
            relative_path = str(file_path.relative_to(repo_root_path))
            debug_print(f"[DEBUG] Looking up churn for file_path: "
                        f"{relative_path}")
            # Use git cache by passing repo_root instead of churn_data
            churn_kpi = ChurnKPI().calculate(
                file_path=str(file_path),
                repo_root=str(repo_root_path.resolve())
            )
            t_filechurn_end = time.perf_counter()
            debug_print(f"[DEBUG] Setting churn for:              "
                        f"{relative_path}: {churn_kpi.value}")
            self.timing['filechurn'] += t_filechurn_end - t_filechurn_start

            t_hotspot_start = time.perf_counter()
            hotspot_kpi = HotspotKPI().calculate(
                complexity=file_complexity_kpi.value,
                churn=churn_kpi.value
            )
            t_hotspot_end = time.perf_counter()
            self.timing['hotspot'] += t_hotspot_end - t_hotspot_start

            # --- Code Ownership KPI ---
            t_ownership_start = time.perf_counter()
            try:
                code_ownership_kpi = CodeOwnershipKPI(
                    file_path=str(file_path.resolve()),
                    repo_root=str(repo_root_path.resolve())
                )
            except Exception as e:
                from src.kpis.codeownership.fallback_kpi import (
                    FallbackCodeOwnershipKPI
                )
                code_ownership_kpi = FallbackCodeOwnershipKPI(str(e))
            t_ownership_end = time.perf_counter()
            self.timing['ownership'] += t_ownership_end - t_ownership_start

            # --- Shared Ownership KPI ---
            t_sharedownership_start = time.perf_counter()
            try:
                shared_ownership_kpi = SharedOwnershipKPI(
                    file_path=str(file_path.resolve()),
                    repo_root=str(repo_root_path.resolve())
                )
            except Exception as e:
                from src.kpis.sharedcodeownership.fallback_kpi import (
                    FallbackSharedOwnershipKPI
                )
                shared_ownership_kpi = FallbackSharedOwnershipKPI(str(e))
            t_sharedownership_end = time.perf_counter()
            self.timing['sharedownership'] += (
                t_sharedownership_end - t_sharedownership_start
            )

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

            # Add file to hierarchy (delegates to HierarchyBuilder)
            self.hierarchy_builder.add_file_to_hierarchy(repo_info, file_obj)
            # Add logic to aggregate KPIs up the hierarchy (from File -> ScanDir -> RepoInfo)
            # debug_print(f"[DEBUG] Returning repo_info for {repo_root}: {repo_info}")
            # --- Aggregate KPIs for each ScanDir (folder) ---

            def aggregate_scan_dir_kpis(scan_dir):
                # Aggregate KPIs from files and subdirectories
                complexity_vals = []
                churn_vals = []
                hotspot_vals = []
                ownership_vals = []
                shared_ownership_counts = []
                for file in scan_dir.files.values():
                    if file.kpis.get('complexity') and isinstance(file.kpis['complexity'].value, (int, float)):
                        complexity_vals.append(file.kpis['complexity'].value)
                    if file.kpis.get('churn') and isinstance(file.kpis['churn'].value, (int, float)):
                        churn_vals.append(file.kpis['churn'].value)
                    if file.kpis.get('hotspot') and isinstance(file.kpis['hotspot'].value, (int, float)):
                        hotspot_vals.append(file.kpis['hotspot'].value)
                    if file.kpis.get('Code Ownership') and isinstance(file.kpis['Code Ownership'].value, dict):
                        ownership_vals.append(file.kpis['Code Ownership'].value)
                    if file.kpis.get('Shared Ownership') and isinstance(file.kpis['Shared Ownership'].value, dict):
                        count = file.kpis['Shared Ownership'].value.get('num_significant_authors')
                        if isinstance(count, int):
                            shared_ownership_counts.append(count)
                # Recursively aggregate from subdirectories
                for subdir in scan_dir.scan_dirs.values():
                    sub_kpis = aggregate_scan_dir_kpis(subdir)
                    if sub_kpis['complexity'] is not None:
                        complexity_vals.append(sub_kpis['complexity'])
                    if sub_kpis['churn'] is not None:
                        churn_vals.append(sub_kpis['churn'])
                    if sub_kpis['hotspot'] is not None:
                        hotspot_vals.append(sub_kpis['hotspot'])
                    if sub_kpis['shared_ownership'] is not None:
                        shared_ownership_counts.append(sub_kpis['shared_ownership'])
                # Compute averages (or None if no data)
                avg_complexity = round(sum(complexity_vals) / len(complexity_vals), 1) if complexity_vals else None
                avg_churn = round(sum(churn_vals) / len(churn_vals), 1) if churn_vals else None
                avg_hotspot = round(sum(hotspot_vals) / len(hotspot_vals), 1) if hotspot_vals else None
                avg_shared_ownership = round(sum(shared_ownership_counts) / len(shared_ownership_counts), 1) \
                    if shared_ownership_counts else None
                # Store in scan_dir.kpis
                from src.kpis.complexity import ComplexityKPI
                from src.kpis.codechurn import ChurnKPI
                from src.kpis.hotspot import HotspotKPI
                scan_dir.kpis['complexity'] = ComplexityKPI(value=avg_complexity)
                scan_dir.kpis['churn'] = ChurnKPI(value=avg_churn)
                scan_dir.kpis['hotspot'] = HotspotKPI(value=avg_hotspot)
                # Store as dict to match file-level format
                # Aggregate all unique significant authors from files and subdirs
                authors_set = set()
                for file in scan_dir.files.values():
                    if file.kpis.get('Shared Ownership') and isinstance(file.kpis['Shared Ownership'].value, dict):
                        file_authors = [a for a in file.kpis['Shared Ownership'].value.get('authors', [])
                                        if a != 'Not Committed Yet']
                        authors_set.update(file_authors)
                for subdir in scan_dir.scan_dirs.values():
                    subdir_authors = subdir.kpis.get('Shared Ownership')
                    if subdir_authors and isinstance(subdir_authors.value, dict):
                        sub_authors = [a for a in subdir_authors.value.get('authors', []) if a != 'Not Committed Yet']
                        authors_set.update(sub_authors)
                shared_ownership_dict = {
                    'num_significant_authors': avg_shared_ownership,
                    'authors': list(authors_set),
                    'threshold': 20.0
                }
                scan_dir.kpis['Shared Ownership'] = AggregatedSharedOwnershipKPI(
                    'Shared Ownership', shared_ownership_dict, unit='authors',
                    description='Avg significant authors')
                return {
                    'complexity': avg_complexity,
                    'churn': avg_churn,
                    'hotspot': avg_hotspot,
                    'shared_ownership': avg_shared_ownership
                }
            aggregate_scan_dir_kpis(repo_info)
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
