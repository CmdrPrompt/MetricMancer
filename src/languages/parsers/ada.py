import re
from src.languages.parsers.base import ComplexityParser

class AdaComplexityParser(ComplexityParser):
	def compute_complexity(self, code: str) -> int:
		complexity = 1
		for pattern in self.CONTROL_KEYWORDS:
			complexity += len(re.findall(pattern, code))
		return complexity
	CONTROL_KEYWORDS = [
		r'\bif(?!\s*;)\b', r'\belsif\b', r'\bcase\b', r'\bwhen\b',
		r'\bloop\b', r'\bwhile\b', r'\bfor\b', r'\bexit\b', r'\bexception\b'
	]
	"""
	Complexity parser for Ada source code.
	Computes cyclomatic complexity using regex patterns for control flow keywords.
	"""
	def compute_complexity(self, code: str) -> int:
		"""
		Compute the cyclomatic complexity of the given Ada code string.
		"""
