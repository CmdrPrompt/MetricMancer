import re
from .base import ComplexityParser

class PythonComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
        r'\btry\b', r'\bexcept\b', r'\breturn\b', r'\band\b', r'\bor\b'
    ]
    FUNCTION_PATTERN = r'def\s+\w+\s*\(.*?\)\s*:'

