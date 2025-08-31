import re
from src.languages.parsers.base import ComplexityParser

class PythonComplexityParser(ComplexityParser):
	def compute_complexity(self, code: str) -> int:
		complexity = 1
		for pattern in self.CONTROL_KEYWORDS:
			complexity += len(re.findall(pattern, code))
		return complexity
	CONTROL_KEYWORDS = [
		r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
		r'\btry\b', r'\bexcept\b', r'\breturn\b', r'\band\b', r'\bor\b'
	]
	FUNCTION_PATTERN = r'def\s+\w+\s*\(.*?\)\s*:'
