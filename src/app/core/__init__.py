"""Core analysis modules.

This module contains the main analysis engine components:
- Analyzer: Main analysis coordinator (uses FileAnalyzer via KPICalculator)
"""

from src.app.core.analyzer import Analyzer

__all__ = ['Analyzer']
