import re
from .base import ComplexityParser

class CppComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b', r'\bdo\b',
        r'\bswitch\b', r'\bcase\b', r'\bdefault\b', r'\bbreak\b', r'\bcontinue\b',
        r'\bgoto\b', r'\breturn\b', r'&&', r'\|\|'
    ]
    FUNCTION_PATTERN = r'(?:\b\w+\s+)+\w+\s*\(.*?\)\s*\{'

