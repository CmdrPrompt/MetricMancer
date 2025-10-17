# Feature Proposal: Cognitive Complexity Metric

## Overview
Add Cognitive Complexity as a new KPI metric to complement Cyclomatic Complexity, providing a more human-centric measure of code understandability.

## Motivation
- **Current limitation**: Cyclomatic Complexity (CC) measures paths but not understandability
- **User pain point**: CC can be misleading - flat code with many simple ifs has high CC but low cognitive load
- **Adam Tornhill alignment**: Cognitive Complexity aligns with "Your Code as a Crime Scene" philosophy
- **Industry adoption**: Used by SonarQube, CodeClimate, and other major tools

## Use Cases

### Example 1: Flat vs Nested
```python
# LOW Cognitive Complexity (3), HIGH Cyclomatic (4)
def process(type):
    if type == "A": return handle_a()  # +1
    if type == "B": return handle_b()  # +1  
    if type == "C": return handle_c()  # +1
    return default()

# HIGH Cognitive Complexity (6), SAME Cyclomatic (4)
def process_nested(data):
    if data:                    # +1
        if data.valid:          # +2 (1 + 1 nesting)
            if data.processed:  # +3 (1 + 2 nesting)
                return result
```

### Example 2: Real MetricMancer Code
From our recent refactoring of `code_review_advisor.py`:

**Before** (High Cognitive Complexity ~45):
```python
def _generate_template(...):  # 70 lines, 3-4 nesting levels
    if risk_level == "critical":
        if ownership_type == "single_owner":
            # Nested logic...
```

**After** (Low Cognitive Complexity ~8):
```python
def _generate_template(...):  # 11 lines, flat structure
    template_parts.extend(self._get_template_header(...))
    template_parts.extend(self._get_template_ownership_context(...))
```

## Technical Design

### 1. New KPI Class: `CognitiveComplexityKPI`

**Location**: `src/kpis/cognitive_complexity/`

```python
from typing import Dict, Any, List
from ..base_kpi import BaseKPI

class CognitiveComplexityKPI(BaseKPI):
    """
    Measures cognitive complexity using SonarSource algorithm.
    
    Cognitive Complexity measures how difficult code is to understand,
    accounting for nesting depth and control flow structures.
    
    Based on: https://www.sonarsource.com/docs/CognitiveComplexity.pdf
    """
    
    def __init__(self, value: int = 0, functions: List[Dict[str, Any]] = None):
        super().__init__(
            value=value,
            name="Cognitive Complexity",
            unit="points",
            description="Measure of how difficult code is to understand"
        )
        self.functions = functions or []
    
    def calculate(self, file_path: str, ast_tree: Any) -> int:
        """Calculate cognitive complexity from AST."""
        return self._calculate_from_ast(ast_tree)
    
    def _calculate_from_ast(self, tree: Any) -> int:
        """Walk AST and sum cognitive complexity."""
        total = 0
        nesting_level = 0
        
        for node in ast.walk(tree):
            complexity, nesting_change = self._node_complexity(node, nesting_level)
            total += complexity
            nesting_level += nesting_change
        
        return total
    
    def _node_complexity(self, node: Any, nesting: int) -> tuple[int, int]:
        """
        Calculate complexity contribution of a single AST node.
        
        Returns: (complexity_points, nesting_change)
        """
        # If/elif/else
        if isinstance(node, ast.If):
            return (1 + nesting, 1)  # Base +1, plus nesting penalty
        
        # Loops (for/while)
        elif isinstance(node, (ast.For, ast.While)):
            return (1 + nesting, 1)
        
        # Exception handling
        elif isinstance(node, ast.ExceptHandler):
            return (1 + nesting, 1)
        
        # Ternary operator
        elif isinstance(node, ast.IfExp):
            return (1 + nesting, 0)  # No nesting increase
        
        # Boolean operators (and/or) - count sequence once
        elif isinstance(node, ast.BoolOp):
            return (1, 0)
        
        # Recursion detection
        elif isinstance(node, ast.Call):
            if self._is_recursive_call(node):
                return (1, 0)
        
        return (0, 0)
```

### 2. Parser Integration

**Update**: `src/languages/parsers/python_parser.py`

```python
class PythonComplexityParser:
    def analyze_functions(self, content: str) -> List[Dict[str, Any]]:
        """Analyze both cyclomatic AND cognitive complexity."""
        tree = ast.parse(content)
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append({
                    'name': node.name,
                    'cyclomatic_complexity': self._calc_cyclomatic(node),
                    'cognitive_complexity': self._calc_cognitive(node),  # NEW
                    'line_start': node.lineno,
                    'line_end': node.end_lineno
                })
        
        return functions
    
    def _calc_cognitive(self, node: ast.FunctionDef) -> int:
        """Calculate cognitive complexity for a function."""
        calculator = CognitiveComplexityCalculator()
        return calculator.calculate(node)
```

### 3. Data Model Updates

**Update**: `src/kpis/model.py`

```python
@dataclass
class ScanFile:
    """Represents a scanned file with all KPIs."""
    name: str
    path: str
    kpis: Dict[str, BaseKPI]
    functions: List[Function]
    
    @property
    def cognitive_complexity(self) -> int:
        """Get cognitive complexity value."""
        kpi = self.kpis.get('CognitiveComplexity')
        return kpi.value if kpi else 0
    
    @property  
    def cognitive_per_function(self) -> float:
        """Average cognitive complexity per function."""
        if not self.functions:
            return 0.0
        return self.cognitive_complexity / len(self.functions)
```

### 4. Report Integration

**Update**: `src/report/cli/cli_summary_format.py`

```python
def _format_file_stats(self, file: Any) -> str:
    """Format file statistics for display."""
    # Existing metrics
    complexity = file.kpis.get('Complexity', {}).get('value', 'N/A')
    churn = file.kpis.get('CodeChurn', {}).get('value', 'N/A')
    
    # NEW: Cognitive complexity
    cognitive = file.kpis.get('CognitiveComplexity', {}).get('value', 'N/A')
    
    return f"""
    📄 {file.name}
       Cyclomatic Complexity:  {complexity}
       Cognitive Complexity:   {cognitive}  🧠 NEW
       Churn:                  {churn}
       Hotspot:               {hotspot}
    """
```

**Update**: `src/report/html/templates/report.html`

```html
<!-- Add new column to complexity table -->
<table class="metrics-table">
    <thead>
        <tr>
            <th>File</th>
            <th>Cyclomatic (CC)</th>
            <th>Cognitive (CogC) 🧠</th>  <!-- NEW -->
            <th>Churn</th>
            <th>Hotspot</th>
        </tr>
    </thead>
    <tbody>
        {% for file in files %}
        <tr class="{{ 'high-cognitive' if file.cognitive_complexity > 15 else '' }}">
            <td>{{ file.name }}</td>
            <td>{{ file.cyclomatic_complexity }}</td>
            <td>{{ file.cognitive_complexity }}</td>  <!-- NEW -->
            <td>{{ file.churn }}</td>
            <td>{{ file.hotspot }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### 5. Quick Wins Integration

**Update**: `src/report/cli/cli_quick_wins_format.py`

```python
def _calculate_impact(self, file_info: Dict) -> int:
    """Calculate refactoring impact (0-10)."""
    impact = 0
    
    complexity = file_info.get('complexity', 0)
    cognitive = file_info.get('cognitive_complexity', 0)  # NEW
    churn = file_info.get('churn', 0)
    
    # High cognitive complexity = high impact
    if cognitive > 30:
        impact += 4  # Very high cognitive load
    elif cognitive > 15:
        impact += 3
    elif cognitive > 10:
        impact += 2
    
    # Combine with existing metrics...
    return min(impact, 10)

def _determine_action(self, file_info: Dict) -> str:
    """Determine recommended action."""
    cognitive = file_info.get('cognitive_complexity', 0)
    
    if cognitive > 30:
        return "Refactor urgently - very hard to understand"
    elif cognitive > 15:
        return "Simplify control flow and reduce nesting"
    # ...
```

## Configuration

**Update**: `src/config/app_config.py`

```python
@dataclass
class AppConfig:
    # Existing thresholds
    threshold_high: int = 15
    threshold_medium: int = 5
    
    # NEW: Cognitive complexity thresholds
    cognitive_threshold_high: int = 15
    cognitive_threshold_medium: int = 10
    
    # Enable/disable
    enable_cognitive_complexity: bool = True
```

**CLI flags**:
```bash
# Enable/disable
metricmancer src/ --enable-cognitive-complexity

# Set thresholds  
metricmancer src/ --cognitive-threshold-high 20 --cognitive-threshold-medium 10

# Filter by cognitive complexity
metricmancer src/ --filter-cognitive-high 15
```

## Metrics & Thresholds

Based on SonarQube recommendations:

| Cognitive Complexity | Risk Level | Action |
|---------------------|------------|---------|
| 0-5                 | ✅ Low     | Excellent |
| 6-10                | 🟡 Medium  | Good |
| 11-15               | 🟠 High    | Consider refactoring |
| 16-25               | 🔴 Critical| Refactor soon |
| 25+                 | 💀 Severe  | Refactor immediately |

## Implementation Plan

### Phase 1: Core Implementation (2-4 hours)
- [ ] Create `CognitiveComplexityKPI` class
- [ ] Implement SonarSource algorithm
- [ ] Add Python AST walker for cognitive complexity
- [ ] Unit tests for calculation algorithm

### Phase 2: Parser Integration (2-3 hours)
- [ ] Update Python parser to calculate both CC and CogC
- [ ] Update other language parsers (Java, JavaScript, etc.)
- [ ] Integration tests

### Phase 3: Data Model (1-2 hours)
- [ ] Add cognitive_complexity to ScanFile
- [ ] Update aggregation functions
- [ ] Update serialization (JSON export)

### Phase 4: Reporting (3-4 hours)
- [ ] Add CogC to CLI summary format
- [ ] Add CogC to HTML reports
- [ ] Add CogC to Quick Wins analysis
- [ ] Update review strategy advisor

### Phase 5: Documentation (1-2 hours)
- [ ] Update README with cognitive complexity explanation
- [ ] Add examples comparing CC vs CogC
- [ ] Update ARCHITECTURE.md

**Total Estimated Time**: 9-15 hours

## Testing Strategy

```python
# tests/kpis/test_cognitive_complexity.py

def test_flat_structure_low_cognitive():
    """Flat if statements should have low cognitive complexity."""
    code = '''
    def process(x):
        if x == 1: return "one"   # +1
        if x == 2: return "two"   # +1  
        if x == 3: return "three" # +1
        return "other"
    '''
    assert calculate_cognitive(code) == 3

def test_nested_structure_high_cognitive():
    """Nested structures should have high cognitive complexity."""
    code = '''
    def process(x, y):
        if x:                    # +1
            if y:                # +2 (1 + 1 nesting)
                if z:            # +3 (1 + 2 nesting)
                    return True
    '''
    assert calculate_cognitive(code) == 6

def test_boolean_operators_count_once():
    """Boolean operators in sequence should count as 1."""
    code = '''
    def check(a, b, c, d):
        if a and b and c and d:  # +1 (not +4!)
            return True
    '''
    assert calculate_cognitive(code) == 1
```

## Benefits

### For Developers:
- 🧠 **Better intuition**: Metric matches human perception of complexity
- 🎯 **Targeted refactoring**: Focus on truly hard-to-understand code
- 📊 **Dual perspective**: CC for paths, CogC for comprehension

### For Teams:
- 👥 **Code review efficiency**: Identify difficult code before review
- 📚 **Onboarding**: Help new developers avoid complex areas
- 🔍 **Technical debt**: Prioritize refactoring based on understandability

### For MetricMancer:
- ⭐ **Competitive advantage**: Feature parity with SonarQube/CodeClimate
- 🎨 **Adam Tornhill alignment**: Perfect fit with "Code as Crime Scene" philosophy
- 📈 **Better insights**: More nuanced complexity analysis

## Example Output

```bash
$ metricmancer src/ --summary

📊 COMPLEXITY ANALYSIS
══════════════════════════════════════════════

Critical Files (Cognitive Complexity > 15):

1. src/analysis/code_review_advisor.py
   Cyclomatic Complexity:  210  ⚠️  High paths
   Cognitive Complexity:    47  🔴 Hard to understand
   Recommendation: Reduce nesting and extract methods

2. src/utilities/git_cache.py  
   Cyclomatic Complexity:  143  ⚠️  High paths
   Cognitive Complexity:    89  💀 Very hard to understand  
   Recommendation: Urgent refactoring needed
   
✅ Quick Wins: Files with high CC but low CogC are good candidates
   for simple refactoring (extract methods without restructuring)
```

## References

1. [SonarSource Cognitive Complexity Paper](https://www.sonarsource.com/docs/CognitiveComplexity.pdf)
2. [CodeClimate Cognitive Complexity](https://docs.codeclimate.com/docs/cognitive-complexity)
3. Adam Tornhill - "Software Design X-Rays" (Chapter 4)
4. [G. Ann Campbell - "Cognitive Complexity: A new way of measuring understandability"](https://www.sonarsource.com/resources/cognitive-complexity/)

## Future Enhancements

- **Cognitive Hotspots**: `Cognitive Complexity × Churn` metric
- **Function-level reporting**: Show cognitive complexity per function
- **Trends over time**: Track cognitive complexity improvements
- **IDE integration**: Real-time cognitive complexity in editor
- **AI suggestions**: Use LLM to suggest refactoring strategies for high CogC code

---

**Status**: Proposal  
**Priority**: High  
**Effort**: Medium (9-15 hours)  
**Value**: High (competitive feature, better insights)
