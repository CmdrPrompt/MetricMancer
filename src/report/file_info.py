from dataclasses import dataclass

@dataclass
class FileInfo:
    path: str
    complexity: float
    functions: int = 0
    grade: str = ''
    test_cases: int = 0  # Minimum number of test cases required
    churn: int = 0  # Code churn value
    repo_root: str = ""
