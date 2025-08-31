import re
from .base import ComplexityParser

class CSharpComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\bfor\b', r'\bwhile\b', r'\bswitch\b',
        r'\bcase\b', r'\bcatch\b', r'\bthrow\b', r'\breturn\b',
        r'&&', r'\|\|'
    ]
    FUNCTION_PATTERN = r'(public|private|protected)?\s+\w+\s+\w+\s*\(.*?\)\s*\{'

