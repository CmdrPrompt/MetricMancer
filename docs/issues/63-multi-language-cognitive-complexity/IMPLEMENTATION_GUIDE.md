# Implementation Guide: Multi-Language Cognitive Complexity

## Quick Start

### 1. Install Dependencies

```bash
pip install tree-sitter>=0.20.0 tree-sitter-languages>=1.10.0
```

### 2. Test Tree-sitter

```python
from tree_sitter_languages import get_parser

# Test JavaScript parsing
parser = get_parser('javascript')
code = """
function example(x) {
    if (x > 0) {
        for (let i = 0; i < x; i++) {
            console.log(i);
        }
    }
}
"""
tree = parser.parse(bytes(code, 'utf8'))
print(tree.root_node.sexp())  # S-expression of AST
```

## Tree-sitter Node Type Mapping

### JavaScript/TypeScript Control Structures

```python
# Control flow structures that increment complexity
INCREMENTS = {
    # Conditionals
    'if_statement': 1,
    'else_clause': 1,
    'ternary_expression': 1,

    # Loops
    'for_statement': 1,
    'for_in_statement': 1,
    'while_statement': 1,
    'do_statement': 1,

    # Switch
    'switch_case': 1,  # Each case adds 1

    # Error handling
    'catch_clause': 1,

    # Logical operators (when used in conditions)
    'binary_expression': {  # Only && and ||
        '&&': 1,
        '||': 1
    }
}

# Structures that increase nesting level
NESTING_INCREMENTS = {
    'function_declaration',
    'arrow_function',
    'function_expression',
    'method_definition',
    'if_statement',
    'for_statement',
    'for_in_statement',
    'for_of_statement',
    'while_statement',
    'do_statement',
    'switch_statement',
    'catch_clause',
    'class_declaration'
}
```

### Java Control Structures

```python
INCREMENTS = {
    'if_statement': 1,
    'else_clause': 1,
    'for_statement': 1,
    'enhanced_for_statement': 1,  # for-each
    'while_statement': 1,
    'do_statement': 1,
    'switch_label': 1,
    'catch_clause': 1,
    'ternary_expression': 1,
    'binary_expression': {
        '&&': 1,
        '||': 1
    }
}
```

## Example Implementation Skeleton

```python
# src/kpis/cognitive_complexity/calculator_javascript.py

from typing import List, Dict
from tree_sitter import Node
from tree_sitter_languages import get_parser

class JavaScriptCognitiveComplexityCalculator:
    """
    Calculate cognitive complexity for JavaScript/TypeScript code.

    Based on SonarSource Cognitive Complexity specification.
    """

    INCREMENTS = {
        'if_statement': 1,
        'else_clause': 1,
        'for_statement': 1,
        'while_statement': 1,
        'do_statement': 1,
        'switch_case': 1,
        'catch_clause': 1,
        'ternary_expression': 1,
    }

    NESTING_INCREMENTS = {
        'function_declaration',
        'arrow_function',
        'if_statement',
        'for_statement',
        'while_statement',
    }

    def __init__(self):
        self.parser = get_parser('javascript')

    def calculate_for_file(self, content: str) -> Dict[str, int]:
        """
        Calculate cognitive complexity for all functions in a file.

        Returns:
            Dict mapping function names to their complexity values
        """
        tree = self.parser.parse(bytes(content, 'utf8'))
        functions = self._find_functions(tree.root_node)

        result = {}
        for func_node in functions:
            name = self._get_function_name(func_node)
            complexity = self._calculate_complexity(func_node)
            result[name] = complexity

        return result

    def _find_functions(self, node: Node) -> List[Node]:
        """Find all function declarations in the tree."""
        functions = []

        if node.type in ('function_declaration', 'arrow_function',
                         'function_expression', 'method_definition'):
            functions.append(node)

        for child in node.children:
            functions.extend(self._find_functions(child))

        return functions

    def _get_function_name(self, node: Node) -> str:
        """Extract function name from node."""
        if node.type == 'function_declaration':
            for child in node.children:
                if child.type == 'identifier':
                    return child.text.decode('utf8')

        # For arrow functions, method definitions, etc.
        # Additional logic needed

        return 'anonymous'

    def _calculate_complexity(self, function_node: Node) -> int:
        """Calculate complexity for a single function."""
        complexity = 0

        def traverse(node: Node, nesting_level: int):
            nonlocal complexity

            # Check if this node increments complexity
            if node.type in self.INCREMENTS:
                increment = self.INCREMENTS[node.type]
                complexity += increment + nesting_level

            # Handle binary expressions (&&, ||)
            if node.type == 'binary_expression':
                operator = self._get_operator(node)
                if operator in ('&&', '||'):
                    complexity += 1 + nesting_level

            # Calculate new nesting level for children
            new_nesting = nesting_level
            if node.type in self.NESTING_INCREMENTS:
                new_nesting += 1

            # Recursively process children
            for child in node.children:
                traverse(child, new_nesting)

        # Start traversal from function body
        body = self._get_function_body(function_node)
        if body:
            traverse(body, nesting_level=0)

        return complexity

    def _get_function_body(self, node: Node) -> Node:
        """Get the body node of a function."""
        for child in node.children:
            if child.type == 'statement_block':
                return child
        return None

    def _get_operator(self, binary_expr: Node) -> str:
        """Get operator from binary expression."""
        for child in binary_expr.children:
            text = child.text.decode('utf8')
            if text in ('&&', '||', '??'):
                return text
        return None
```

## Testing Strategy

### 1. Simple Test Cases

```python
# tests/kpis/test_cognitive_complexity_javascript.py

def test_simple_if():
    code = """
    function test() {
        if (true) {
            return 1;
        }
    }
    """
    calculator = JavaScriptCognitiveComplexityCalculator()
    result = calculator.calculate_for_file(code)
    assert result['test'] == 1  # One if statement

def test_nested_if():
    code = """
    function test() {
        if (a) {           // +1
            if (b) {       // +2 (1 + nesting)
                return 1;
            }
        }
    }
    """
    calculator = JavaScriptCognitiveComplexityCalculator()
    result = calculator.calculate_for_file(code)
    assert result['test'] == 3  # 1 + 2
```

### 2. Real-world Test

Use actual files from BlockAssistant:

```python
def test_calculate_block_outcome():
    """Test real-world JavaScript file."""
    with open('../BlockAsisstant/src/utils/calculateBlockOutcome.js') as f:
        code = f.read()

    calculator = JavaScriptCognitiveComplexityCalculator()
    result = calculator.calculate_for_file(code)

    # Expected: similar to cyclomatic complexity but accounting for nesting
    assert 'calculateBlockOutcome' in result
    assert result['calculateBlockOutcome'] > 0
```

## Integration with Existing Code

### Update CognitiveComplexityKPI

```python
# src/kpis/cognitive_complexity/cognitive_complexity_kpi.py

class CognitiveComplexityKPI(BaseKPI):

    def calculate(self, file_path: str, file_content: str) -> 'CognitiveComplexityKPI':
        """Calculate cognitive complexity (multi-language support)."""

        # Detect language from file extension
        ext = Path(file_path).suffix

        if ext == '.py':
            calculator = PythonCognitiveComplexityCalculator()
        elif ext in ('.js', '.jsx'):
            calculator = JavaScriptCognitiveComplexityCalculator()
        elif ext in ('.ts', '.tsx'):
            calculator = TypeScriptCognitiveComplexityCalculator()
        elif ext == '.java':
            calculator = JavaCognitiveComplexityCalculator()
        else:
            # Unsupported language
            self.value = None
            self.calculation_values = {}
            return self

        # Calculate
        result = calculator.calculate_for_file(file_content)
        self.value = sum(result.values())
        self.calculation_values = result

        return self
```

## Performance Considerations

- Tree-sitter is fast, but parsing is still work
- Consider caching parsed trees for incremental analysis
- For very large files (>10k lines), consider chunking

## Debugging Tips

1. **View AST structure:**
   ```python
   tree = parser.parse(bytes(code, 'utf8'))
   print(tree.root_node.sexp())
   ```

2. **Inspect node types:**
   ```python
   def print_tree(node, indent=0):
       print('  ' * indent + node.type)
       for child in node.children:
           print_tree(child, indent + 1)

   print_tree(tree.root_node)
   ```

3. **Compare with SonarQube:**
   - Use SonarQube/SonarCloud to verify results
   - Test against their examples from the spec

## Resources

- [Tree-sitter Playground](https://tree-sitter.github.io/tree-sitter/playground) - Test queries
- [JavaScript Grammar](https://github.com/tree-sitter/tree-sitter-javascript)
- [TypeScript Grammar](https://github.com/tree-sitter/tree-sitter-typescript)
- [Java Grammar](https://github.com/tree-sitter/tree-sitter-java)
