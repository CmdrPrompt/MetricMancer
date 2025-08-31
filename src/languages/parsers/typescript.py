import re
from src.languages.parsers.base import ComplexityParser

class TypeScriptComplexityParser(ComplexityParser):
	def compute_complexity(self, code: str) -> int:
		complexity = 1
		for pattern in self.CONTROL_KEYWORDS:
			complexity += len(re.findall(pattern, code))
		return complexity
	CONTROL_KEYWORDS = [
		r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bwhile\b',
		r'\bswitch\b', r'\bcase\b', r'\bcatch\b', r'\bthrow\b',
		r'\breturn\b', r'&&', r'\|\|'
	]
	FUNCTION_PATTERN = r'function\s+\w+\s*\(.*?\)\s*\{'
