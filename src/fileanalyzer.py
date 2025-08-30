import re
import os

class FileAnalyzer:
	def __init__(self, filepath, root_dir, config):
		self.filepath = filepath
		self.root_dir = root_dir
		self.config = config
		self.code = ""

	def load(self):
		try:
			with open(self.filepath, 'r', encoding='utf-8', errors='ignore') as f:
				self.code = f.read()
			return True
		except Exception as e:
			print(f"⚠️ Kunde inte läsa {self.filepath}: {e}")
			return False

	def analyze(self):
		# The sorting should be handled when aggregating results, but if you want to ensure
		# the path is always normalized for sorting, you can do it here. Otherwise, sort in report generation.
		return {
			'language': self.config['name'],
			'root': self.root_dir,
			'path': self._relative_path(),
			'functions': self._count_functions(),
			'complexity': self._calculate_complexity(),
		}

	def _calculate_complexity(self):
		return 1 + sum(len(re.findall(p, self.code)) for p in self.config['patterns'])

	def _count_functions(self):
		return len(re.findall(self.config['function_pattern'], self.code))

	def _relative_path(self):
		return os.path.relpath(self.filepath, self.root_dir)
