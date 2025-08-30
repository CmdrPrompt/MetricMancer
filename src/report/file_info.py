from dataclasses import dataclass

@dataclass
class FileInfo:
    path: str
    complexity: float
    functions: int = 0
    grade: str = ''
    test_cases: int = 0  # Minimum number of test cases required
