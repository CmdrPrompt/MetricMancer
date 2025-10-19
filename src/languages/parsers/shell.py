"""
Shell script complexity parser - wrapper for json_yaml module.

This file exists to maintain compatibility with the naming convention
expected by ComplexityAnalyzer (ShellComplexityParser -> shell.py).
"""

from src.languages.parsers.json_yaml import ShellComplexityParser

__all__ = ['ShellComplexityParser']
