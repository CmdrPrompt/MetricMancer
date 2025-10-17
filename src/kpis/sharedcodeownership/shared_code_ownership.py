from src.kpis.base_kpi import BaseKPI
from src.kpis.codeownership.code_ownership import CodeOwnershipKPI
from typing import Mapping, Optional, Union, List, Dict


class SharedOwnershipKPI(BaseKPI):
    """
    Calculates shared ownership for a file or function.
    Shared ownership is defined as the number (or proportion) of authors
    whose ownership exceeds a given threshold (default: 20%).
    Aggregation can be done by summing or averaging shared files/functions per directory/repo.
    """

    def __init__(self, file_path: str, repo_root: str, threshold: float = 20.0,
                 ownership_data: Optional[Dict[str, float]] = None):
        super().__init__(
            name="Shared Ownership",
            description="Number/proportion of significant authors per file/function (ownership > threshold)",
            value=None
        )
        self.file_path = file_path
        self.repo_root = repo_root
        self.threshold = threshold
        # Allow passing in precomputed ownership data for efficiency
        if ownership_data is not None:
            self.value = self.calculate_shared_ownership(ownership_data)
        else:
            ownership = CodeOwnershipKPI(file_path, repo_root).value
            self.value = self.calculate_shared_ownership(ownership)

    def calculate_shared_ownership(
            self, ownership: Mapping[str, Union[float, str]]) -> Mapping[str, Union[float, str, int, List[str]]]:
        # Debug: print(ownership)
        if (
            not isinstance(ownership, dict)
            or (set(ownership.keys()) == {"ownership"} and ownership["ownership"] == "N/A")
        ):
            return {"shared_ownership": "N/A"}
        significant_authors = [
            author for author, percent in ownership.items()
            if isinstance(percent, (int, float)) and percent >= self.threshold
        ]
        return {
            "num_significant_authors": len(significant_authors),
            "authors": significant_authors,
            "threshold": self.threshold
        }

    def calculate(self):
        # Required by BaseKPI, but not used here
        return self.value
