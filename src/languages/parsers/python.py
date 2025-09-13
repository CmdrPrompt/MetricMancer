import re
from src.languages.parsers.base import ComplexityParser

	"""
	Complexity parser for Python source code.
	Computes cyclomatic complexity and counts functions using regex patterns.
	"""
	def compute_complexity(self, code: str) -> int:
		"""
		Compute the cyclomatic complexity of the given Python code string.
		"""
		complexity = 1
		for pattern in self.CONTROL_KEYWORDS:
			complexity += len(re.findall(pattern, code))
		return complexity
	CONTROL_KEYWORDS = [
		r'\bif\b', r'\belif\b', r'\bfor\b', r'\bwhile\b',
		r'\btry\b', r'\bexcept\b', r'\breturn\b', r'\band\b', r'\bor\b'
	]
	FUNCTION_PATTERN = r'def\s+\w+\s*\(.*?\)\s*:'
