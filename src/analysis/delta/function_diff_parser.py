"""
Function-level diff parser for delta analysis.

Parses git diffs and maps changed lines to specific functions using AST analysis.
"""

import ast
from typing import Dict, List, Set, Any
from unidiff import PatchSet


class FunctionDiffParser:
    """
    Parse git diffs and map changes to specific functions.

    Uses unidiff to parse git unified diff format, then uses AST
    to map changed lines to function definitions.
    """

    def parse_git_diff(self, diff_text: str) -> List[Dict[str, Any]]:
        """
        Parse git diff text to extract changed files and line ranges.

        Args:
            diff_text: Git unified diff output

        Returns:
            List of dicts with keys:
                - file_path: Path to changed file
                - changed_lines: Set of line numbers that changed
        """
        if not diff_text or not diff_text.strip():
            return []

        try:
            patch_set = PatchSet(diff_text)
        except Exception:
            # Malformed diff - return empty
            return []

        file_changes = []

        for patched_file in patch_set:
            # Get file path (use target_file for new files, source for deleted)
            if patched_file.is_added_file:
                file_path = patched_file.target_file[2:]  # Remove 'b/' prefix
            elif patched_file.is_removed_file:
                file_path = patched_file.source_file[2:]  # Remove 'a/' prefix
            else:
                file_path = patched_file.target_file[2:] if patched_file.target_file else \
                    patched_file.source_file[2:]

            # Extract all changed line numbers
            changed_lines = set()

            for hunk in patched_file:
                # Add target lines (lines in new version)
                for line in hunk:
                    if line.target_line_no is not None:
                        changed_lines.add(line.target_line_no)

            file_changes.append({
                'file_path': file_path,
                'changed_lines': changed_lines,
                'is_added': patched_file.is_added_file,
                'is_deleted': patched_file.is_removed_file,
            })

        return file_changes

    def extract_functions_from_source(self, source_code: str, language: str) -> List[Dict[str, Any]]:
        """
        Extract function definitions from source code.

        Args:
            source_code: Source code text
            language: Programming language (e.g., 'python', 'javascript')

        Returns:
            List of dicts with keys:
                - name: Function name
                - start_line: Starting line number (1-indexed)
                - end_line: Ending line number (1-indexed)
        """
        if not source_code or not source_code.strip():
            return []

        # For now, only support Python (most common in test suite)
        if language.lower() == 'python':
            return self._extract_python_functions(source_code)
        elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
            return self._extract_javascript_functions(source_code)
        else:
            # Unsupported language - return empty gracefully
            return []

    def _extract_python_functions(self, source_code: str) -> List[Dict[str, Any]]:
        """Extract functions from Python source using AST."""
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            # Invalid syntax - return empty
            return []

        functions = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append({
                    'name': node.name,
                    'start_line': node.lineno,
                    'end_line': node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                })

        return functions

    def _extract_javascript_functions(self, source_code: str) -> List[Dict[str, Any]]:
        """
        Extract functions from JavaScript source.

        Note: This is a simplified implementation using regex.
        For production, consider using a proper JS parser like esprima.
        """
        import re

        functions = []
        lines = source_code.split('\n')

        # Simple regex for function declarations
        # Matches: function name() {...}
        function_pattern = re.compile(r'^\s*function\s+(\w+)\s*\(')

        for i, line in enumerate(lines, start=1):
            match = function_pattern.match(line)
            if match:
                function_name = match.group(1)
                # Approximate end line (find closing brace)
                # This is simplified - real implementation would need proper parsing
                end_line = self._find_closing_brace(lines, i - 1)
                functions.append({
                    'name': function_name,
                    'start_line': i,
                    'end_line': end_line if end_line else i,
                })

        return functions

    def _find_closing_brace(self, lines: List[str], start_index: int) -> int:
        """
        Find the closing brace for a function starting at start_index.

        Simple implementation that counts braces.
        """
        brace_count = 0
        for i in range(start_index, len(lines)):
            line = lines[i]
            brace_count += line.count('{')
            brace_count -= line.count('}')
            if brace_count == 0 and '{' in lines[start_index]:
                return i + 1  # Convert to 1-indexed
        return start_index + 1  # Default to start line if not found

    def map_lines_to_functions(
        self,
        functions: List[Dict[str, Any]],
        changed_lines: Set[int]
    ) -> List[Dict[str, Any]]:
        """
        Map changed line numbers to specific functions.

        Args:
            functions: List of function definitions
            changed_lines: Set of line numbers that changed

        Returns:
            List of functions that contain changed lines
        """
        affected_functions = []

        for func in functions:
            start = func['start_line']
            end = func['end_line']

            # Check if any changed line is within this function
            for line in changed_lines:
                if start <= line <= end:
                    affected_functions.append(func)
                    break  # Already added this function

        return affected_functions
