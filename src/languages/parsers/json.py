"""
JSON complexity parser - wrapper for json_yaml module.

This file exists to maintain compatibility with the naming convention
expected by ComplexityAnalyzer (JSONComplexityParser -> json.py).
"""

from src.languages.parsers.json_yaml import JSONComplexityParser

__all__ = ['JSONComplexityParser']
