import re
from .base import ComplexityParser

class GoComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bswitch\b', r'\bcase\b',
        r'\bselect\b', r'\bgo\b', r'\bdefer\b', r'\breturn\b', r'&&', r'\|\|'
    ]
    FUNCTION_PATTERN = r'func\s+\w+\s*\(.*?\)\s*\{'

