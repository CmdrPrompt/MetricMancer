"""
Test module for FunctionDiffParser.

Following TDD (RED-GREEN-REFACTOR):
- Tests written first to define behavior
- Implementation follows tests
"""

import pytest
from textwrap import dedent


class TestParseDiff:
    """Test parsing git diffs to extract changed files and line ranges."""

    def test_parse_simple_diff_single_file(self):
        """Test parsing a simple diff with one file change."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        # Valid unified diff format (copied from real git diff)
        diff_text = dedent("""
            diff --git a/src/test.py b/src/test.py
            index abc123..def456 100644
            --- a/src/test.py
            +++ b/src/test.py
            @@ -1,2 +1,3 @@
             def test_function():
                 return True
            +    print("debug")
        """).strip()

        parser = FunctionDiffParser()
        file_changes = parser.parse_git_diff(diff_text)

        assert len(file_changes) == 1
        assert file_changes[0]['file_path'] == 'src/test.py'
        assert len(file_changes[0]['changed_lines']) > 0

    def test_parse_diff_multiple_files(self):
        """Test parsing diff with multiple files."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        diff_text = dedent("""
            diff --git a/src/file1.py b/src/file1.py
            index abc123..def456 100644
            --- a/src/file1.py
            +++ b/src/file1.py
            @@ -1,1 +1,2 @@
             def func1():
            +    pass
            diff --git a/src/file2.py b/src/file2.py
            index xyz789..uvw012 100644
            --- a/src/file2.py
            +++ b/src/file2.py
            @@ -1,1 +1,2 @@
             def func2():
            +    return 42
        """).strip()

        parser = FunctionDiffParser()
        file_changes = parser.parse_git_diff(diff_text)

        assert len(file_changes) == 2
        file_paths = [fc['file_path'] for fc in file_changes]
        assert 'src/file1.py' in file_paths
        assert 'src/file2.py' in file_paths

    def test_parse_empty_diff(self):
        """Test parsing empty diff (no changes)."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        parser = FunctionDiffParser()
        file_changes = parser.parse_git_diff("")

        assert len(file_changes) == 0

    def test_parse_diff_with_additions_only(self):
        """Test parsing diff with only additions (new file)."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        diff_text = dedent("""
            diff --git a/src/new_file.py b/src/new_file.py
            new file mode 100644
            index 0000000..abc123
            --- /dev/null
            +++ b/src/new_file.py
            @@ -0,0 +1,2 @@
            +def new_function():
            +    return True
        """).strip()

        parser = FunctionDiffParser()
        file_changes = parser.parse_git_diff(diff_text)

        assert len(file_changes) == 1
        assert file_changes[0]['file_path'] == 'src/new_file.py'
        assert len(file_changes[0]['changed_lines']) > 0

    def test_parse_diff_with_deletions_only(self):
        """Test parsing diff with only deletions (deleted file)."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        diff_text = dedent("""
            diff --git a/src/old_file.py b/src/old_file.py
            deleted file mode 100644
            index abc123..0000000
            --- a/src/old_file.py
            +++ /dev/null
            @@ -1,2 +0,0 @@
            -def old_function():
            -    return False
        """).strip()

        parser = FunctionDiffParser()
        file_changes = parser.parse_git_diff(diff_text)

        assert len(file_changes) == 1
        assert file_changes[0]['file_path'] == 'src/old_file.py'


class TestMapLinesToFunctions:
    """Test mapping changed lines to specific functions."""

    def test_map_single_line_to_function(self):
        """Test mapping a single changed line to its containing function."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        # Simple Python file with one function
        source_code = dedent("""
            def test_function():
                x = 1
                y = 2
                return x + y
        """).strip()

        parser = FunctionDiffParser()
        changed_lines = {3}  # Line 3 changed

        # For this test, we need a method that can parse and map
        functions = parser.extract_functions_from_source(source_code, 'python')

        assert len(functions) > 0
        assert functions[0]['name'] == 'test_function'
        assert functions[0]['start_line'] <= 3 <= functions[0]['end_line']

    def test_map_multiple_lines_to_same_function(self):
        """Test multiple changed lines in same function."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = dedent("""
            def large_function():
                a = 1
                b = 2
                c = 3
                d = 4
                return a + b + c + d
        """).strip()

        parser = FunctionDiffParser()
        changed_lines = {2, 3, 4}  # Multiple lines changed

        functions = parser.extract_functions_from_source(source_code, 'python')

        assert len(functions) == 1
        func = functions[0]
        assert func['name'] == 'large_function'
        # All changed lines should be within this function
        for line in changed_lines:
            assert func['start_line'] <= line <= func['end_line']

    def test_map_lines_to_multiple_functions(self):
        """Test changed lines in different functions."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = dedent("""
            def function_one():
                return 1

            def function_two():
                return 2
        """).strip()

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(source_code, 'python')

        assert len(functions) == 2
        assert functions[0]['name'] == 'function_one'
        assert functions[1]['name'] == 'function_two'

    def test_extract_functions_with_nested_functions(self):
        """Test extracting functions with nested definitions."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = dedent("""
            def outer_function():
                def inner_function():
                    return 1
                return inner_function()
        """).strip()

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(source_code, 'python')

        # Should extract both outer and inner functions
        assert len(functions) >= 2
        function_names = [f['name'] for f in functions]
        assert 'outer_function' in function_names
        assert 'inner_function' in function_names

    def test_extract_functions_from_class(self):
        """Test extracting methods from a class."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = dedent("""
            class MyClass:
                def method_one(self):
                    return 1

                def method_two(self):
                    return 2
        """).strip()

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(source_code, 'python')

        assert len(functions) >= 2
        function_names = [f['name'] for f in functions]
        assert 'method_one' in function_names
        assert 'method_two' in function_names


class TestLanguageSupport:
    """Test parser works with different languages."""

    def test_parse_python_functions(self):
        """Test parsing Python function definitions."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = dedent("""
            def my_function():
                pass
        """).strip()

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(source_code, 'python')

        assert len(functions) == 1
        assert functions[0]['name'] == 'my_function'

    def test_parse_javascript_functions(self):
        """Test parsing JavaScript function definitions."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = dedent("""
            function myFunction() {
                return true;
            }
        """).strip()

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(source_code, 'javascript')

        assert len(functions) >= 1
        # Should extract the function
        assert any('myFunction' in f['name'] for f in functions)

    def test_unsupported_language_returns_empty(self):
        """Test that unsupported languages return empty list gracefully."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = "some random text"

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(source_code, 'unsupported_lang')

        # Should not crash, just return empty
        assert functions == []


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_malformed_diff(self):
        """Test parsing malformed diff doesn't crash."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        malformed_diff = "this is not a valid diff"

        parser = FunctionDiffParser()
        file_changes = parser.parse_git_diff(malformed_diff)

        # Should return empty list, not crash
        assert file_changes == []

    def test_parse_invalid_python_syntax(self):
        """Test parsing invalid Python doesn't crash."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        invalid_code = "def incomplete_function("

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(invalid_code, 'python')

        # Should handle gracefully
        assert isinstance(functions, list)

    def test_parse_empty_file(self):
        """Test parsing empty file."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source("", 'python')

        assert functions == []

    def test_parse_file_with_no_functions(self):
        """Test parsing file with no function definitions."""
        from src.analysis.delta.function_diff_parser import FunctionDiffParser

        source_code = dedent("""
            # Just comments
            x = 1
            y = 2
        """).strip()

        parser = FunctionDiffParser()
        functions = parser.extract_functions_from_source(source_code, 'python')

        assert len(functions) == 0
