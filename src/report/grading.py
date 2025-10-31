"""
Grading utilities for complexity assessment.
"""


def grade(complexity: float, threshold_low: float = 10.0, threshold_high: float = 20.0) -> str:
    """
    Assign a grade based on complexity value.

    Args:
        complexity: The complexity value to grade
        threshold_low: Lower threshold for acceptable complexity
        threshold_high: Upper threshold for high complexity

    Returns:
        Grade string: 'A', 'B', 'C', 'D', or 'F'
    """
    if complexity < threshold_low:
        return 'A'
    elif complexity < threshold_high:
        return 'B'
    elif complexity < threshold_high * 1.5:
        return 'C'
    elif complexity < threshold_high * 2:
        return 'D'
    else:
        return 'F'
