"""
Shared helpers for file list operations in report generation.
"""
from typing import Any, Dict, List, Union
from src.report.file_info import FileInfo
from src.report.grading import grade

def sort_files(files: List[Union[Dict[str, Any], FileInfo]]) -> List[FileInfo]:
    allowed_keys = {'path', 'complexity', 'functions', 'grade', 'churn', 'repo_root'}
    file_objs: List[FileInfo] = []
    for f in files:
        if isinstance(f, FileInfo):
            file_objs.append(f)
        else:
            filtered = {k: v for k, v in f.items() if k in allowed_keys}
            file_objs.append(FileInfo(**filtered))
    return sorted(file_objs, key=lambda x: x.path)

def average_complexity(files: List[Union[Dict[str, Any], FileInfo]]) -> float:
    if not files:
        return 0.0
    def get_complexity(f: Union[Dict[str, Any], FileInfo]) -> float:
        return f.complexity if hasattr(f, 'complexity') else f['complexity']
    return sum(get_complexity(f) for f in files) / len(files)

def average_grade(files: List[Union[Dict[str, Any], FileInfo]], threshold_low: float, threshold_high: float) -> Union[str, Dict[str, Any]]:
    if not files:
        return "No code"
    avg = average_complexity(files)
    return {
        'value': avg,
        'label': grade(avg, threshold_low, threshold_high),
        'formatted': f"{grade(avg, threshold_low, threshold_high)} ({avg:.1f})"
    }

def filter_problem_files(files: List[FileInfo], problem_file_threshold: float) -> List[FileInfo]:
    """
    Filter and return files with complexity greater than or equal to the problem_file_threshold.
    Args:
        files: List of FileInfo objects.
        problem_file_threshold: Complexity threshold for flagging files as problematic.
    Returns:
        List of FileInfo objects exceeding the threshold.
    """
    return [f for f in files if f.complexity is not None and f.complexity >= problem_file_threshold]

def filter_hotspot_risk_files(files: List[FileInfo], high_score: float = 300, medium_score: float = 100, complexity_limit: float = 15, churn_limit: float = 15) -> List[FileInfo]:
    """
    Filter and return files that are considered hotspots based on churn and complexity.
    Args:
        files: List of FileInfo objects.
        high_score: Threshold for high hotspot score (complexity * churn).
        medium_score: Threshold for medium hotspot score.
        complexity_limit: Complexity threshold for hotspot risk.
        churn_limit: Churn threshold for hotspot risk.
    Returns:
        List of FileInfo objects flagged as hotspot risks.
    """
    hotspot_risk_files = []
    for f in files:
        if f.complexity is not None and f.churn is not None:
            hs_score = f.complexity * f.churn
            if hs_score > high_score or (f.complexity > complexity_limit and f.churn > churn_limit):
                hotspot_risk_files.append(f)
            elif hs_score >= medium_score:
                hotspot_risk_files.append(f)
    return hotspot_risk_files

def summarize_and_sort_report(summary: List[dict], sort_key: str = 'average', secondary_keys: List[str] = ['language', 'root'], reverse: bool = True) -> List[dict]:
    """
    Sort and summarize report data by the specified keys.
    Args:
        summary: List of report summary dictionaries.
        sort_key: Primary key to sort by (default 'average').
        secondary_keys: List of secondary keys for sorting.
        reverse: If True, sort the primary key in descending order.
    Returns:
        Sorted list of report summary dictionaries.
    """
    def sort_tuple(x):
        keys = [x.get(sort_key, 0)]
        for k in secondary_keys:
            keys.append(x.get(k, ''))
        # If reverse, sort the first key descending
        keys[0] = -keys[0] if reverse and isinstance(keys[0], (int, float)) else keys[0]
        return tuple(keys)
    return sorted(summary, key=sort_tuple)
