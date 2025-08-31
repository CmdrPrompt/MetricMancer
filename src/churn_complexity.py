from .code_churn import FileMetrics

class ChurnComplexityAnalysis:
    def __init__(self, metrics_list, churn_threshold=100, complexity_threshold=10):
        self.metrics_list = metrics_list
        self.churn_threshold = churn_threshold
        self.complexity_threshold = complexity_threshold

    def refactoring_candidates(self):
        """
        Filer med hög churn och hög komplexitet
        """
        return [
            m for m in self.metrics_list
            if m.churn > self.churn_threshold and m.complexity > self.complexity_threshold
        ]

    def stable_risky_files(self):
        """
        Filer med låg churn och hög komplexitet
        """
        return [
            m for m in self.metrics_list
            if m.churn < 10 and m.complexity > self.complexity_threshold
        ]

    def summary(self):
        return {
            "refactoring_candidates": self.refactoring_candidates(),
            "stable_risky_files": self.stable_risky_files(),
        }
