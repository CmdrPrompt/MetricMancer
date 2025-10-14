import os

from ..base_kpi import BaseKPI


class ChurnKPI(BaseKPI):
    def __init__(self, value=None, calculation_values=None):
        super().__init__(
            name="churn",
            value=value,
            unit="commits/month",
            description="Number of commits per month affecting the file",
            calculation_values=calculation_values
        )

    def calculate(self, file_path: str, churn_data: dict = None, repo_root: str = None, **kwargs):
        """
        Looks up a pre-calculated churn value from a dictionary.
        Robust to absolute/relative path mismatches and filename-only matches.
        If churn_data is None, uses the git cache instead (Issue #41).
        """
        # If no churn_data provided, use git cache
        if churn_data is None and repo_root is not None:
            try:
                from src.utilities.git_cache import get_git_cache
                git_cache = get_git_cache()
                # Convert to relative path for cache lookup
                rel_path = os.path.relpath(file_path, repo_root) if os.path.isabs(file_path) else file_path
                self.value = git_cache.get_churn_data(repo_root, rel_path)
                self.calculation_values = {"time_period_months": kwargs.get("time_period_months", 6)}
                return self
            except Exception:
                # Fallback to 0 if cache fails
                self.value = 0
                self.calculation_values = {"time_period_months": kwargs.get("time_period_months", 6)}
                return self

        # Legacy behavior: lookup in churn_data dictionary
        if churn_data is None:
            self.value = 0
            self.calculation_values = {"time_period_months": kwargs.get("time_period_months", 6)}
            return self

        abs_path = os.path.normcase(os.path.normpath(os.path.abspath(file_path)))
        # Try absolute path match
        for key in churn_data:
            norm_key = os.path.normcase(os.path.normpath(key))
            if abs_path == norm_key:
                self.value = churn_data[key]
                self.calculation_values = {"time_period_months": kwargs.get("time_period_months", 6)}
                break
        else:
            # Try filename match if absolute path fails
            file_name = os.path.basename(file_path)
            for key in churn_data:
                if os.path.basename(key) == file_name:
                    self.value = churn_data[key]
                    self.calculation_values = {"time_period_months": kwargs.get("time_period_months", 6)}
                    break
            else:
                self.value = 0
                self.calculation_values = {"time_period_months": kwargs.get("time_period_months", 6)}
        return self
