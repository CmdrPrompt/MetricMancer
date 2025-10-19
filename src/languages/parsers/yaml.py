"""
YAML complexity parser - wrapper for json_yaml module.

This file exists to maintain compatibility with the naming convention
expected by ComplexityAnalyzer (YAMLComplexityParser -> yaml.py).
"""

from src.languages.parsers.json_yaml import YAMLComplexityParser

__all__ = ['YAMLComplexityParser']
