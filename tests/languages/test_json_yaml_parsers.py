"""
Tests for JSON, YAML, and Shell Script complexity parsers.
"""

import unittest
import tempfile
import os
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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = f.name

        try:
            parser = JSONComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 0)
            self.assertLess(complexity, 5)  # Simple structure
        finally:
            os.unlink(temp_path)

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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = f.name

        try:
            parser = JSONComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 5)  # More complex structure
        finally:
            os.unlink(temp_path)

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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(json_content)
            temp_path = f.name

        try:
            parser = JSONComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 3)
        finally:
            os.unlink(temp_path)


class TestYAMLComplexityParser(unittest.TestCase):
    """Test YAML structural complexity calculation."""

    def test_simple_yaml(self):
        """Test complexity of simple YAML."""
        yaml_content = '''name: John
age: 30
city: New York'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = YAMLComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 0)
            self.assertLess(complexity, 5)
        finally:
            os.unlink(temp_path)

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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = YAMLComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 5)
        finally:
            os.unlink(temp_path)

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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = YAMLComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 3)  # Anchors add complexity
        finally:
            os.unlink(temp_path)

    def test_yaml_multiline_strings(self):
        """Test complexity with multi-line strings."""
        yaml_content = '''description: |
  This is a multi-line
  description that spans
  multiple lines
command: >
  echo "This is a folded
  multi-line string"'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(yaml_content)
            temp_path = f.name

        try:
            parser = YAMLComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 0)
        finally:
            os.unlink(temp_path)


class TestShellComplexityParser(unittest.TestCase):
    """Test shell script cyclomatic complexity calculation."""

    def test_simple_shell_script(self):
        """Test complexity of simple shell script."""
        shell_content = '''#!/bin/bash
echo "Hello World"
ls -la
pwd'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(shell_content)
            temp_path = f.name

        try:
            parser = ShellComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertEqual(complexity, 1)  # Base complexity only
        finally:
            os.unlink(temp_path)

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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(shell_content)
            temp_path = f.name

        try:
            parser = ShellComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreater(complexity, 1)  # if + elif = +2
        finally:
            os.unlink(temp_path)

    def test_shell_with_loops(self):
        """Test complexity with loops."""
        shell_content = '''#!/bin/bash
for file in *.txt; do
    echo "$file"
done

while read line; do
    echo "$line"
done < input.txt'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(shell_content)
            temp_path = f.name

        try:
            parser = ShellComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreaterEqual(complexity, 3)  # Base + for + while
        finally:
            os.unlink(temp_path)

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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(shell_content)
            temp_path = f.name

        try:
            parser = ShellComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreaterEqual(complexity, 3)  # Base + 2 functions

            functions = parser.get_functions()
            self.assertEqual(len(functions), 2)
            self.assertIn('hello', functions)
            self.assertIn('goodbye', functions)
        finally:
            os.unlink(temp_path)

    def test_shell_with_logical_operators(self):
        """Test complexity with logical operators."""
        shell_content = '''#!/bin/bash
[ -f "file1.txt" ] && [ -f "file2.txt" ] && echo "Both exist"
[ -d "dir1" ] || [ -d "dir2" ] || echo "No directory found"'''

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(shell_content)
            temp_path = f.name

        try:
            parser = ShellComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreaterEqual(complexity, 5)  # Base + 2 && + 2 ||
        finally:
            os.unlink(temp_path)

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

        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
            f.write(shell_content)
            temp_path = f.name

        try:
            parser = ShellComplexityParser(temp_path)
            complexity = parser.calculate_complexity()
            self.assertGreaterEqual(complexity, 2)  # Base + case
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
