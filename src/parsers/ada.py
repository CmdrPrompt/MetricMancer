import re
from .base import ComplexityParser

class AdaComplexityParser(ComplexityParser):
    CONTROL_KEYWORDS = [
        r'\bif(?!\s*;)\b', r'\belsif\b', r'\bcase\b', r'\bwhen\b',
        r'\bloop\b', r'\bwhile\b', r'\bfor\b', r'\bexit\b', r'\bexception\b'
    ]

