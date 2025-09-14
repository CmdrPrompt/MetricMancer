import re
from src.languages.parsers.base import ComplexityParser

class GoComplexityParser(ComplexityParser):
	"""
	Complexity parser for Go source code.
	Computes cyclomatic complexity and counts functions using regex patterns.
	"""
	def compute_complexity(self, code: str) -> int:
		"""
		Compute the cyclomatic complexity of the given Go code string.
		"""
		complexity = 1
		for pattern in self.CONTROL_KEYWORDS:
			complexity += len(re.findall(pattern, code))
		return complexity
	CONTROL_KEYWORDS = [
		r'\bif\b', r'\belse\s+if\b', r'\bfor\b', r'\bswitch\b', r'\bcase\b',
		r'\bselect\b', r'\bgo\b', r'\bdefer\b', r'\breturn\b', r'&&', r'\|\|'
	]
	FUNCTION_PATTERN = r'func\s+([a-zA-Z_]\w*)\s*\(.*?\)\s*\{'
