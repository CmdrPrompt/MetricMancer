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
		if 'parser' in self.config:
			parser_class_name = self.config['parser']
			module_name = parser_class_name.replace('ComplexityParser', '').lower()
			parser_module = f"src.parsers.{module_name}"
			parser_class = getattr(__import__(parser_module, fromlist=[parser_class_name]), parser_class_name)
			parser = parser_class()
			complexity = parser.compute_complexity(self.code)
			# Ada har ingen count_functions, returnera None om ej implementerad
			function_count = getattr(parser, 'count_functions', lambda code: None)(self.code)
		else:
			complexity = self._calculate_complexity()
			function_count = self._count_functions()
		return {
			'language': self.config['name'],
			'root': self.root_dir,
			'path': self._relative_path(),
			'functions': function_count,
			'complexity': complexity,
		}

	def _calculate_complexity(self):
		return 1 + sum(len(re.findall(p, self.code)) for p in self.config.get('patterns', []))

	def _count_functions(self):
		pattern = self.config.get('function_pattern')
		if pattern:
			return len(re.findall(pattern, self.code))
		return 0

	def _relative_path(self):
		return os.path.relpath(self.filepath, self.root_dir)
