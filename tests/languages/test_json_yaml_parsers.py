"""
Tests for JSON, YAML, and Shell Script complexity parsers.
"""

import unittest
from src.languages.parsers.json_yaml import (
    JSONComplexityParser,
    YAMLComplexityParser,
    ShellComplexityParser
)


class TestJSONComplexityParser(unittest.TestCase):
    """Test JSON structural complexity calculation."""

    def test_simple_json(self):
        """Test complexity of simple JSON."""
        json_content = '{"name": "John", "age": 30}'

        parser = JSONComplexityParser()
        complexity = parser.compute_complexity(json_content)
        self.assertGreater(complexity, 0)
        self.assertLess(complexity, 5)  # Simple structure

    def test_nested_json(self):
        """Test complexity of nested JSON."""
        json_content = '''{
            "user": {
                "profile": {
                    "name": "John",
                    "address": {
                        "city": "New York",
                        "country": "USA"
                    }
                },
                "settings": {
                    "theme": "dark",
                    "notifications": true
                }
            }
        }'''

        parser = JSONComplexityParser()
        complexity = parser.compute_complexity(json_content)
        self.assertGreater(complexity, 5)  # More complex structure

    def test_json_with_arrays(self):
        """Test complexity of JSON with arrays."""
        json_content = '''{
            "users": [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25}
            ],
            "settings": {
                "features": ["feature1", "feature2", "feature3"]
            }
        }'''

        parser = JSONComplexityParser()
        complexity = parser.compute_complexity(json_content)
        self.assertGreater(complexity, 3)


class TestYAMLComplexityParser(unittest.TestCase):
    """Test YAML structural complexity calculation."""

    def test_simple_yaml(self):
        """Test complexity of simple YAML."""
        yaml_content = '''name: John
age: 30
city: New York'''

        parser = YAMLComplexityParser()
        complexity = parser.compute_complexity(yaml_content)
        self.assertGreater(complexity, 0)
        self.assertLess(complexity, 5)

    def test_nested_yaml(self):
        """Test complexity of nested YAML."""
        yaml_content = '''user:
  profile:
    name: John
    address:
      city: New York
      country: USA
  settings:
    theme: dark
    notifications: true'''

        parser = YAMLComplexityParser()
        complexity = parser.compute_complexity(yaml_content)
        self.assertGreater(complexity, 5)

    def test_yaml_with_anchors(self):
        """Test complexity of YAML with anchors and aliases."""
        yaml_content = '''defaults: &defaults
  adapter: postgres
  host: localhost

development:
  <<: *defaults
  database: dev_db

production:
  <<: *defaults
  database: prod_db'''

        parser = YAMLComplexityParser()
        complexity = parser.compute_complexity(yaml_content)
        self.assertGreater(complexity, 3)  # Anchors add complexity

    def test_yaml_multiline_strings(self):
        """Test complexity with multi-line strings."""
        yaml_content = '''description: |
  This is a multi-line
  description that spans
  multiple lines
command: >
  echo "This is a folded
  multi-line string"'''

        parser = YAMLComplexityParser()
        complexity = parser.compute_complexity(yaml_content)
        self.assertGreater(complexity, 0)


class TestShellComplexityParser(unittest.TestCase):
    """Test shell script cyclomatic complexity calculation."""

    def test_simple_shell_script(self):
        """Test complexity of simple shell script."""
        shell_content = '''#!/bin/bash
echo "Hello World"
ls -la
pwd'''

        parser = ShellComplexityParser()
        complexity = parser.compute_complexity(shell_content)
        self.assertEqual(complexity, 1)  # Base complexity only

    def test_shell_with_conditionals(self):
        """Test complexity with if statements."""
        shell_content = '''#!/bin/bash
if [ -f "file.txt" ]; then
    echo "File exists"
elif [ -d "dir" ]; then
    echo "Directory exists"
else
    echo "Nothing found"
fi'''

        parser = ShellComplexityParser()
        complexity = parser.compute_complexity(shell_content)
        self.assertGreater(complexity, 1)  # if + elif = +2

    def test_shell_with_loops(self):
        """Test complexity with loops."""
        shell_content = '''#!/bin/bash
for file in *.txt; do
    echo "$file"
done

while read line; do
    echo "$line"
done < input.txt'''

        parser = ShellComplexityParser()
        complexity = parser.compute_complexity(shell_content)
        self.assertGreaterEqual(complexity, 3)  # Base + for + while

    def test_shell_with_functions(self):
        """Test complexity with function definitions."""
        shell_content = '''#!/bin/bash
function hello() {
    echo "Hello"
}

goodbye() {
    echo "Goodbye"
}

hello
goodbye'''

        parser = ShellComplexityParser()
        complexity = parser.compute_complexity(shell_content)
        self.assertGreaterEqual(complexity, 1)  # Base complexity

        # Test function counting
        func_count = parser.count_functions(shell_content)
        self.assertEqual(func_count, 2)

        # Test function analysis
        functions = parser.analyze_functions(shell_content)
        self.assertEqual(len(functions), 2)
        func_names = [f['name'] for f in functions]
        self.assertIn('hello', func_names)
        self.assertIn('goodbye', func_names)

    def test_shell_with_logical_operators(self):
        """Test complexity with logical operators."""
        shell_content = '''#!/bin/bash
[ -f "file1.txt" ] && [ -f "file2.txt" ] && echo "Both exist"
[ -d "dir1" ] || [ -d "dir2" ] || echo "No directory found"'''

        parser = ShellComplexityParser()
        complexity = parser.compute_complexity(shell_content)
        self.assertGreaterEqual(complexity, 5)  # Base + 2 && + 2 ||

    def test_shell_with_case_statement(self):
        """Test complexity with case statement."""
        shell_content = '''#!/bin/bash
case "$1" in
    start)
        echo "Starting"
        ;;
    stop)
        echo "Stopping"
        ;;
    restart)
        echo "Restarting"
        ;;
    *)
        echo "Unknown command"
        ;;
esac'''

        parser = ShellComplexityParser()
        complexity = parser.compute_complexity(shell_content)
        self.assertGreaterEqual(complexity, 2)  # Base + case


if __name__ == '__main__':
    unittest.main()
