from collections import defaultdict
from pathlib import Path
from tqdm import tqdm
import time

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


def initialize_timing():
    """Initialize timing dictionary for performance tracking."""
    return {
        'cache_prebuild': 0.0,
        'complexity': 0.0,
        'filechurn': 0.0,
        'hotspot': 0.0,
        'ownership': 0.0,
        'sharedownership': 0.0
    }


def prebuild_git_cache(repo_root_path, files_in_repo, churn_period_days):
    """
    Pre-build git cache for all files in the repository.
    
    Returns:
        tuple: (cache_prebuild_time, git_cache)
    """
    from src.utilities.git_cache import get_git_cache
    
    t_start = time.perf_counter()
    git_cache = get_git_cache(churn_period_days=churn_period_days)
    
    file_paths = [
        str(Path(file_info['path']).relative_to(repo_root_path))
        for file_info in files_in_repo
    ]
    debug_print(f"[PREBUILD] Pre-building cache for {len(file_paths)} files")
    git_cache.prebuild_cache_for_files(str(repo_root_path.resolve()), file_paths)
    
    t_end = time.perf_counter()
    elapsed = t_end - t_start
    debug_print(f"[PREBUILD] Cache pre-building completed in {elapsed:.3f} seconds")
    
    return elapsed


def read_file_content(file_path):
    """
    Read file content with error handling.
    
    Returns:
        str or None: File content, or None if reading fails
    """
    try:
        with file_path.open('r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception as e:
        debug_print(f"[WARN] Unable to read {file_path}: {e}")
        return None


def analyze_functions_complexity(content, lang_config, complexity_analyzer):
    """
    Analyze functions in file content and return complexity metrics.
    
    Returns:
        tuple: (function_objects, total_complexity, elapsed_time)
    """
    t_start = time.perf_counter()
    functions_data = complexity_analyzer.analyze_functions(content, lang_config)
    t_end = time.perf_counter()
    
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
    
    return function_objects, total_complexity, t_end - t_start


def calculate_churn_kpi(file_path, repo_root_path):
    """
    Calculate churn KPI for a file.
    
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


def calculate_ownership_kpis(file_path, repo_root_path):
    """
    Calculate code ownership and shared ownership KPIs.
    
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
        from src.kpis.codeownership.fallback_kpi import FallbackCodeOwnershipKPI
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
        from src.kpis.sharedcodeownership.fallback_kpi import FallbackSharedOwnershipKPI
        shared_ownership_kpi = FallbackSharedOwnershipKPI(str(e))
    t_shared_end = time.perf_counter()
    
    return (code_ownership_kpi, shared_ownership_kpi,
            t_ownership_end - t_ownership_start,
            t_shared_end - t_shared_start)


def extract_numeric_kpi(file, kpi_name):
    """Extract a numeric KPI value from a file if valid."""
    kpi = file.kpis.get(kpi_name)
    if kpi and isinstance(kpi.value, (int, float)):
        return kpi.value
    return None


def extract_shared_ownership_count(file):
    """Extract shared ownership count from a file if valid."""
    kpi = file.kpis.get('Shared Ownership')
    if kpi and isinstance(kpi.value, dict):
        count = kpi.value.get('num_significant_authors')
        if isinstance(count, int):
            return count
    return None


def collect_kpi_values(scan_dir):
    """
    Collect KPI values from files in a scan directory.
    
    Returns:
        dict: Dictionary of KPI value lists
    """
    complexity_vals = []
    churn_vals = []
    hotspot_vals = []
    shared_ownership_counts = []
    
    for file in scan_dir.files.values():
        val = extract_numeric_kpi(file, 'complexity')
        if val is not None:
            complexity_vals.append(val)
        
        val = extract_numeric_kpi(file, 'churn')
        if val is not None:
            churn_vals.append(val)
        
        val = extract_numeric_kpi(file, 'hotspot')
        if val is not None:
            hotspot_vals.append(val)
        
        count = extract_shared_ownership_count(file)
        if count is not None:
            shared_ownership_counts.append(count)
    
    return {
        'complexity': complexity_vals,
        'churn': churn_vals,
        'hotspot': hotspot_vals,
        'shared_ownership': shared_ownership_counts
    }


def extract_file_authors(file):
    """Extract authors from a file's Shared Ownership KPI."""
    kpi = file.kpis.get('Shared Ownership')
    if not kpi or not isinstance(kpi.value, dict):
        return []
    
    authors = kpi.value.get('authors', [])
    return [a for a in authors if a != 'Not Committed Yet']


def extract_subdir_authors(subdir):
    """Extract authors from a subdirectory's Shared Ownership KPI."""
    kpi = subdir.kpis.get('Shared Ownership')
    if not kpi or not isinstance(kpi.value, dict):
        return []
    
    authors = kpi.value.get('authors', [])
    return [a for a in authors if a != 'Not Committed Yet']


def collect_authors_from_hierarchy(scan_dir):
    """
    Collect all unique authors from files and subdirectories.
    
    Returns:
        set: Set of author names
    """
    authors_set = set()
    
    # Collect from files
    for file in scan_dir.files.values():
        authors_set.update(extract_file_authors(file))
    
    # Collect from subdirectories
    for subdir in scan_dir.scan_dirs.values():
        authors_set.update(extract_subdir_authors(subdir))
    
    return authors_set


def calculate_average_kpis(kpi_values):
    """
    Calculate average values for KPIs.
    
    Returns:
        dict: Dictionary of average KPI values
    """
    avg_complexity = (
        round(sum(kpi_values['complexity']) / len(kpi_values['complexity']), 1)
        if kpi_values['complexity'] else None
    )
    avg_churn = (
        round(sum(kpi_values['churn']) / len(kpi_values['churn']), 1)
        if kpi_values['churn'] else None
    )
    avg_hotspot = (
        round(sum(kpi_values['hotspot']) / len(kpi_values['hotspot']), 1)
        if kpi_values['hotspot'] else None
    )
    avg_shared_ownership = (
        round(sum(kpi_values['shared_ownership']) / len(kpi_values['shared_ownership']), 1)
        if kpi_values['shared_ownership'] else None
    )
    
    return {
        'complexity': avg_complexity,
        'churn': avg_churn,
        'hotspot': avg_hotspot,
        'shared_ownership': avg_shared_ownership
    }


class AggregatedSharedOwnershipKPI(BaseKPI):
    """Aggregated version of SharedOwnershipKPI for directory aggregation."""

    def calculate(self, *args, **kwargs):
        return self.value


class Analyzer:
    def __init__(self, languages_config, threshold_low=10.0,
                 threshold_high=20.0, churn_period_days=30):
        self.config = languages_config
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.churn_period_days = churn_period_days
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

        # Initialize timing accumulators
        if not hasattr(self, 'timing'):
            self.timing = initialize_timing()

        # 2. Pre-build cache before KPI calculation
        cache_time = prebuild_git_cache(repo_root_path, files_in_repo, self.churn_period_days)
        self.timing['cache_prebuild'] += cache_time

        # 3. Build the hierarchical data model and calculate KPIs
        if not files_in_repo:
            debug_print(f"[DEBUG] No files to analyze for repo: {repo_root}, returning None.")
            return None
        
        complexity_analyzer = ComplexityAnalyzer()
        
        for file_info in tqdm(files_in_repo, desc=f"Analyzing files in {repo_root_path.name}", unit="file"):
            file_obj = self._process_file(file_info, repo_root_path, complexity_analyzer)
            if file_obj:
                self.hierarchy_builder.add_file_to_hierarchy(repo_info, file_obj)
        
        # Aggregate KPIs for the directory hierarchy
        self._aggregate_scan_dir_kpis(repo_info)
        return repo_info
    
    def _process_file(self, file_info, repo_root_path, complexity_analyzer):
        """Process a single file and return a File object with all KPIs."""
        file_path = Path(file_info['path'])
        ext = file_info.get('ext')
        
        if ext not in self.config:
            debug_print(f"_analyze_repo: Skipping file with unknown extension: {str(file_path.resolve())}")
            return None
        
        # Read file content
        content = read_file_content(file_path)
        if content is None:
            return None
        
        # Analyze complexity
        lang_config = self.config[ext]
        function_objects, total_complexity, complexity_time = analyze_functions_complexity(
            content, lang_config, complexity_analyzer
        )
        self.timing['complexity'] += complexity_time
        
        # Calculate file-level complexity KPI
        file_complexity_kpi = ComplexityKPI().calculate(
            complexity=total_complexity,
            function_count=len(function_objects)
        )
        
        # Calculate churn KPI
        churn_kpi, churn_time = calculate_churn_kpi(file_path, repo_root_path)
        self.timing['filechurn'] += churn_time
        
        # Calculate hotspot KPI
        t_hotspot_start = time.perf_counter()
        hotspot_kpi = HotspotKPI().calculate(
            complexity=file_complexity_kpi.value,
            churn=churn_kpi.value
        )
        self.timing['hotspot'] += time.perf_counter() - t_hotspot_start
        
        # Calculate ownership KPIs
        code_ownership_kpi, shared_ownership_kpi, ownership_time, shared_time = calculate_ownership_kpis(
            file_path, repo_root_path
        )
        self.timing['ownership'] += ownership_time
        self.timing['sharedownership'] += shared_time
        
        # Create the File object
        return File(
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
    
    def _aggregate_scan_dir_kpis(self, scan_dir):
        """
        Recursively aggregate KPIs from files and subdirectories.
        
        Returns:
            dict: Dictionary of average KPI values
        """
        # Collect KPI values from files
        kpi_values = collect_kpi_values(scan_dir)
        
        # Recursively aggregate from subdirectories
        for subdir in scan_dir.scan_dirs.values():
            sub_kpis = self._aggregate_scan_dir_kpis(subdir)
            if sub_kpis['complexity'] is not None:
                kpi_values['complexity'].append(sub_kpis['complexity'])
            if sub_kpis['churn'] is not None:
                kpi_values['churn'].append(sub_kpis['churn'])
            if sub_kpis['hotspot'] is not None:
                kpi_values['hotspot'].append(sub_kpis['hotspot'])
            if sub_kpis['shared_ownership'] is not None:
                kpi_values['shared_ownership'].append(sub_kpis['shared_ownership'])
        
        # Calculate averages
        avg_kpis = calculate_average_kpis(kpi_values)
        
        # Store aggregated KPIs in scan_dir
        scan_dir.kpis['complexity'] = ComplexityKPI(value=avg_kpis['complexity'])
        scan_dir.kpis['churn'] = ChurnKPI(value=avg_kpis['churn'])
        scan_dir.kpis['hotspot'] = HotspotKPI(value=avg_kpis['hotspot'])
        
        # Aggregate authors
        authors_set = collect_authors_from_hierarchy(scan_dir)
        shared_ownership_dict = {
            'num_significant_authors': avg_kpis['shared_ownership'],
            'authors': list(authors_set),
            'threshold': 20.0
        }
        scan_dir.kpis['Shared Ownership'] = AggregatedSharedOwnershipKPI(
            'Shared Ownership', shared_ownership_dict, unit='authors',
            description='Avg significant authors'
        )
        
        return avg_kpis

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
