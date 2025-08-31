"""
Shared helpers for file list operations in report generation.
"""
from typing import Any, Dict, List, Union
from src.report.file_info import FileInfo
from src.metrics import grade

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
