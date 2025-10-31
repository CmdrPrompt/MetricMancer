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

### Ada Control Structures

**Parser:** Use [briot/tree-sitter-ada](https://github.com/briot/tree-sitter-ada) (ABI v14, updated 2024-05-23)

```python
INCREMENTS = {
    # Conditionals
    'if_statement': 1,
    'elsif_statement_part': 1,
    'else_statement_part': 1,

    # Loops
    'loop_statement': 1,
    'while_loop_statement': 1,
    'for_loop_statement': 1,

    # Case statements
    'case_statement': 1,
    'case_statement_alternative': 1,  # Each 'when' clause

    # Exception handling
    'exception_handler': 1,  # Each 'when' in exception block

    # Exit/return
    'exit_statement': 1,
    'return_statement': 1,

    # Boolean operators
    'binary_expression': {
        'and': 1,
        'or': 1,
        'and then': 1,  # Short-circuit and
        'or else': 1    # Short-circuit or
    }
}

NESTING_INCREMENTS = {
    'subprogram_body',          # Procedure/function
    'package_body',
    'task_body',                # Ada-specific: tasks
    'protected_body',           # Ada-specific: protected objects
    'if_statement',
    'elsif_statement_part',
    'loop_statement',
    'while_loop_statement',
    'for_loop_statement',
    'case_statement',
    'exception_handler',
}
```

### Go Control Structures

```python
INCREMENTS = {
    'if_statement': 1,
    'for_statement': 1,          # Go's only loop type
    'switch_statement': 1,
    'case_clause': 1,
    'select_statement': 1,       # Channel operations
    'comm_clause': 1,            # Each case in select
    'defer_statement': 1,
    'go_statement': 1,           # Goroutine launch
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

### Create Calculator Factory (Recommended Pattern)

```python
# src/kpis/cognitive_complexity/calculator_factory.py

from pathlib import Path
from typing import Optional
from .calculator_base import CognitiveComplexityCalculatorBase
from .calculator_python import PythonCognitiveComplexityCalculator
from .calculator_javascript import JavaScriptCognitiveComplexityCalculator
from .calculator_typescript import TypeScriptCognitiveComplexityCalculator
from .calculator_java import JavaCognitiveComplexityCalculator
from .calculator_ada import AdaCognitiveComplexityCalculator
from .calculator_go import GoCognitiveComplexityCalculator

class CognitiveComplexityCalculatorFactory:
    """Factory for creating language-specific cognitive complexity calculators."""

    # Map extensions to calculator classes
    CALCULATORS = {
        '.py': PythonCognitiveComplexityCalculator,
        '.js': JavaScriptCognitiveComplexityCalculator,
        '.jsx': JavaScriptCognitiveComplexityCalculator,
        '.ts': TypeScriptCognitiveComplexityCalculator,
        '.tsx': TypeScriptCognitiveComplexityCalculator,
        '.java': JavaCognitiveComplexityCalculator,
        '.adb': AdaCognitiveComplexityCalculator,
        '.ads': AdaCognitiveComplexityCalculator,
        '.go': GoCognitiveComplexityCalculator,
        # Add more as implemented
    }

    @classmethod
    def create(cls, file_path: str) -> Optional[CognitiveComplexityCalculatorBase]:
        """
        Create calculator for given file path.

        Returns:
            Calculator instance or None if language not supported.
        """
        ext = Path(file_path).suffix.lower()
        calculator_class = cls.CALCULATORS.get(ext)

        if calculator_class:
            return calculator_class()
        return None

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if file extension is supported."""
        ext = Path(file_path).suffix.lower()
        return ext in cls.CALCULATORS

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of all supported file extensions."""
        return sorted(cls.CALCULATORS.keys())
```

### Update CognitiveComplexityKPI (Using Factory)

```python
# src/kpis/cognitive_complexity/cognitive_complexity_kpi.py

from .calculator_factory import CognitiveComplexityCalculatorFactory
import logging

logger = logging.getLogger(__name__)

class CognitiveComplexityKPI(BaseKPI):

    def calculate(self, file_path: str, file_content: str) -> 'CognitiveComplexityKPI':
        """
        Calculate cognitive complexity (multi-language support).

        Returns None if language not supported or parsing fails.
        """
        # Use factory to get appropriate calculator
        calculator = CognitiveComplexityCalculatorFactory.create(file_path)

        if calculator is None:
            # Language not supported
            self.value = None
            self.calculation_values = {}
            return self

        try:
            # Calculate per-function complexity
            function_complexities = calculator.calculate_for_file(file_content)

            # Aggregate to file level
            if function_complexities:
                self.value = sum(function_complexities.values())
                self.calculation_values = function_complexities
            else:
                # No functions found
                self.value = 0
                self.calculation_values = {}

        except Exception as e:
            # Handle parsing errors gracefully
            logger.warning(f"Failed to calculate cognitive complexity for {file_path}: {e}")
            self.value = None
            self.calculation_values = {}

        return self
```

## Performance Considerations

### Benchmarking
- Tree-sitter is fast, but parsing is still work
- Expected parse times: <100ms for typical files (<10KB)
- Memory usage: <50MB for large files (100KB)

### Optimization Strategies
- Consider caching parsed trees for incremental analysis
- For very large files (>10k lines), consider chunking
- Profile each language calculator separately

### Performance Testing Script
```python
# scripts/benchmark_cognitive_complexity.py

import time
from pathlib import Path
from src.kpis.cognitive_complexity.calculator_factory import CognitiveComplexityCalculatorFactory

def benchmark_file(file_path: str, iterations: int = 100):
    """Benchmark cognitive complexity calculation for a file."""
    content = Path(file_path).read_text()
    calculator = CognitiveComplexityCalculatorFactory.create(file_path)

    if calculator is None:
        print(f"Unsupported language: {file_path}")
        return

    # Warmup
    calculator.calculate_for_file(content)

    # Benchmark
    start = time.time()
    for _ in range(iterations):
        calculator.calculate_for_file(content)
    elapsed = time.time() - start

    avg_time = (elapsed / iterations) * 1000  # ms
    file_size = len(content) / 1024  # KB

    print(f"{file_path}:")
    print(f"  Size: {file_size:.1f} KB")
    print(f"  Avg time: {avg_time:.2f} ms")
    print(f"  Throughput: {file_size/avg_time*1000:.1f} KB/s")

# Run benchmarks
benchmark_file("src/app/metric_mancer_app.py")  # Python
benchmark_file("tests/fixtures/example.java")    # Java
benchmark_file("tests/fixtures/example.js")      # JavaScript
```

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

## Testing Strategy

### Test Matrix

| Language | Simple | Nested | Booleans | Switch | Loops | Exceptions | Specific | Total Tests |
|----------|--------|--------|----------|--------|-------|------------|----------|-------------|
| Python   | ✅     | ✅     | ✅       | ✅     | ✅    | ✅         | comprehensions | 21 (existing) |
| Java     | 📝     | 📝     | 📝       | 📝     | 📝    | 📝         | streams, lambdas | 30+ |
| Ada      | 📝     | 📝     | 📝       | 📝     | 📝    | 📝         | tasks, packages | 25+ |
| Go       | 📝     | 📝     | 📝       | 📝     | 📝    | 📝         | goroutines, defer | 25+ |
| JavaScript | 📝   | 📝     | 📝       | 📝     | 📝    | 📝         | async/await, arrow | 30+ |
| TypeScript | 📝   | 📝     | 📝       | 📝     | 📝    | 📝         | type guards | 25+ |

### Integration Tests

```python
# tests/integration/test_multi_language_analysis.py

def test_analyze_java_project():
    """Test full analysis of a Java project."""
    from src.app.metric_mancer_app import MetricMancerApp

    config = AppConfig(
        directories=['tests/fixtures/java_project'],
        output_format='json'
    )
    app = MetricMancerApp(config)
    results = app.run()

    # Verify Java files have cognitive complexity
    for file in results.files:
        if file.file_path.endswith('.java'):
            assert file.kpis['cognitive_complexity'].value is not None
            assert file.kpis['cognitive_complexity'].value > 0

def test_backward_compatibility_python():
    """Ensure Python cognitive complexity still works after tree-sitter integration."""
    # Use existing MetricMancer Python files
    config = AppConfig(directories=['src/app'])
    app = MetricMancerApp(config)
    results = app.run()

    # Compare with known baseline values
    main_file = next(f for f in results.files if f.name == 'metric_mancer_app.py')
    assert main_file.kpis['cognitive_complexity'].value is not None
```

### Regression Testing

```bash
# Run full test suite to ensure no breaking changes
python -m pytest tests/ -v

# Check that all 675+ tests still pass
python -m pytest tests/ --tb=short

# Generate coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

## Resources

### Tree-sitter Parsers

- [Tree-sitter Playground](https://tree-sitter.github.io/tree-sitter/playground) - Test queries
- [JavaScript Grammar](https://github.com/tree-sitter/tree-sitter-javascript)
- [TypeScript Grammar](https://github.com/tree-sitter/tree-sitter-typescript)
- [Java Grammar](https://github.com/tree-sitter/tree-sitter-java)
- [Ada Grammar](https://github.com/briot/tree-sitter-ada) - **Recommended for Ada support** (Last updated: 2024-05-23, ABI v14)
- [Go Grammar](https://github.com/tree-sitter/tree-sitter-go)
- [C# Grammar](https://github.com/tree-sitter/tree-sitter-c-sharp)
- [C Grammar](https://github.com/tree-sitter/tree-sitter-c)
- [C++ Grammar](https://github.com/tree-sitter/tree-sitter-cpp)

### Cognitive Complexity References

- [SonarSource Cognitive Complexity Spec](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) - Official specification
- [SonarQube Rules](https://rules.sonarsource.com/) - Language-specific rules and examples
