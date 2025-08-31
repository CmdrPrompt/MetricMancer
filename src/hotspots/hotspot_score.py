class HotspotScore:
    """
    Beräknar hotspot-score för en fil baserat på komplexitet och churn.
    Hotspot-score = komplexitet * churn
    """
    def __init__(self, complexity: float, churn: float):
        self.complexity = complexity
        self.churn = churn
        self.score = self.calculate_score()

    def calculate_score(self) -> float:
        if self.complexity is not None and self.churn is not None:
            return self.complexity * self.churn
        return 0.0

    def is_hotspot(self, threshold: float = 300) -> bool:
        """Returnerar True om hotspot-score överstiger threshold."""
        return self.score > threshold

    def __repr__(self):
        return f"HotspotScore(complexity={self.complexity}, churn={self.churn}, score={self.score})"
