# Future Enhancements for MetricMancer

## 🎯 Delta-Based Review Time Estimation

### Problem
Currently, the review strategy estimates time based on the **entire file's complexity**, even when only a small portion of the file has changed. This can lead to:
- Over-estimation of review time for large files with small changes
- Under-prioritization of small files with complex changes
- Less accurate resource planning

### Proposed Solution: Delta Complexity Analysis

Instead of measuring entire file complexity, analyze only the **changed portions**:

#### Implementation Approach

```python
def get_changed_function_complexity(file_path: str, base_branch: str = "main") -> Dict[str, Any]:
    """
    Analyze complexity of only the changed functions in a file.
    
    Returns:
        {
            'delta_complexity': int,        # Complexity of changed functions only
            'changed_functions': List[str],  # Names of changed functions
            'changed_lines': int,            # Number of lines changed
            'complexity_per_function': Dict[str, int]  # Function -> Complexity
        }
    """
    # Step 1: Get changed line ranges from git diff
    diff_output = subprocess.run(
        ['git', 'diff', '--unified=0', f'{base_branch}...HEAD', '--', file_path],
        capture_output=True, text=True
    ).stdout
    
    # Parse diff to get line ranges: [(start, end), ...]
    changed_ranges = parse_diff_ranges(diff_output)
    
    # Step 2: Parse current file with AST to find functions
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read(), filename=file_path)
    
    # Step 3: Map each function to its line range
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = {
                'start_line': node.lineno,
                'end_line': node.end_lineno,
                'complexity': calculate_complexity(node)
            }
    
    # Step 4: Identify which functions overlap with changed ranges
    affected_functions = []
    delta_complexity = 0
    
    for func_name, func_info in functions.items():
        for change_start, change_end in changed_ranges:
            if ranges_overlap(
                (func_info['start_line'], func_info['end_line']),
                (change_start, change_end)
            ):
                affected_functions.append(func_name)
                delta_complexity += func_info['complexity']
                break
    
    return {
        'delta_complexity': delta_complexity,
        'changed_functions': affected_functions,
        'changed_lines': sum(end - start + 1 for start, end in changed_ranges),
        'complexity_per_function': {
            name: functions[name]['complexity'] 
            for name in affected_functions
        }
    }


def parse_diff_ranges(diff_output: str) -> List[Tuple[int, int]]:
    """
    Parse git diff output to extract changed line ranges.
    
    Example diff header:
        @@ -42,7 +42,9 @@ def some_function():
        
    Returns: [(42, 50), ...] # (start_line, end_line)
    """
    import re
    ranges = []
    
    for line in diff_output.split('\n'):
        if line.startswith('@@'):
            # Extract the "+42,9" part (lines in new version)
            match = re.search(r'\+(\d+)(?:,(\d+))?', line)
            if match:
                start = int(match.group(1))
                count = int(match.group(2)) if match.group(2) else 1
                end = start + count - 1
                ranges.append((start, end))
    
    return ranges


def ranges_overlap(range1: Tuple[int, int], range2: Tuple[int, int]) -> bool:
    """Check if two line ranges overlap."""
    start1, end1 = range1
    start2, end2 = range2
    return not (end1 < start2 or end2 < start1)
```

#### Updated Review Time Estimation

```python
def _estimate_review_time_delta(
    self, 
    delta_complexity: int,      # Complexity of changed functions only
    changed_lines: int,          # Number of changed lines
    churn: float,
    risk_level: str
) -> int:
    """
    Estimate review time based on delta complexity (more accurate).
    """
    base_time = 5  # Lower base time since we're only reviewing changes
    
    # Add time based on delta complexity
    if delta_complexity > 30:
        base_time += 45
    elif delta_complexity > 15:
        base_time += 25
    elif delta_complexity > 5:
        base_time += 15
    
    # Add time based on changed lines
    if changed_lines > 200:
        base_time += 30
    elif changed_lines > 100:
        base_time += 20
    elif changed_lines > 50:
        base_time += 10
    
    # Add time based on churn (same as before)
    if churn > 15:
        base_time += 20
    elif churn > 10:
        base_time += 10
    
    # Add time based on risk level (same as before)
    if risk_level == "critical":
        base_time += 30
    elif risk_level == "high":
        base_time += 15
    
    return base_time
```

### Benefits

1. **More Accurate Estimates**: Review time reflects actual changes, not file size
2. **Better Prioritization**: Complex changes in simple files get proper attention
3. **Function-Level Insights**: Know exactly which functions changed
4. **Targeted Reviews**: Reviewers can focus on specific functions
5. **PR Context**: Show "You changed 3 functions with total complexity 42"

### Example Output

```
File: app/analyzer.py
   Risk Level: CRITICAL
   
   🔍 Changed Functions:
      - analyze_repository() [Complexity: 15, Lines: 45-89]
      - _process_files() [Complexity: 8, Lines: 120-145]
   
   Delta Complexity: 23 (vs. Full File: 90)
   Changed Lines: 67 (vs. Total: 450)
   Estimated Time: 65 minutes (vs. Full File: 125 minutes)
   
   Focus Areas: analyze_repository complexity, _process_files error handling
```

### Implementation Priority

This feature would be particularly valuable for:
- Large, mature codebases
- Files with high overall complexity
- Teams practicing incremental refactoring
- Pull request reviews (vs. full codebase reviews)

### Language Support Matrix

| **Language/File Type** | **Complexity Analysis** | **Delta Analysis** | **Review Strategy** |
|------------------------|-------------------------|-------------------|---------------------|
| Python | ✅ Full | ✅ Function-level | ✅ Complete |
| JavaScript/TypeScript | ✅ Full | ✅ Function-level | ✅ Complete |
| Java | ✅ Full | ✅ Method-level | ✅ Complete |
| C#/C/C++ | ✅ Full | ✅ Function-level | ✅ Complete |
| Go | ✅ Full | ✅ Function-level | ✅ Complete |
| Ada | ✅ Full | ✅ Procedure-level | ✅ Complete |
| Markdown/Docs | ❌ N/A | ⚠️ Line-based | ✅ Churn-based |
| JSON/YAML/Config | ❌ N/A | ⚠️ Structure-based | ✅ Impact-based |
| Other text files | ❌ N/A | ⚠️ Line-based | ✅ Churn-based |

**Legend:**
- ✅ Full support
- ⚠️ Partial support (alternative metrics used)
- ❌ Not applicable (but review strategy still works via churn/ownership)

### Related Features to Add

1. **Function-level ownership**: Track which developer owns which functions
2. **Historical delta analysis**: Track how function complexity changes over time
3. **Review coverage**: Ensure all changed functions are reviewed
4. **Complexity trends**: Show if changes increase or decrease complexity
5. **Config file impact analysis**: Assess impact of configuration changes (e.g., dependency updates)

### Technical Considerations

- **Performance**: AST parsing adds overhead (~50-100ms per file)
- **Language support**: Would work for all supported languages with parsers (Python, JS, TS, Java, C#, C, C++, Go, Ada)
- **Non-code files**: For files without complexity parsers (Markdown, JSON, YAML), delta analysis would focus on:
  - Changed line count only
  - Structural changes (e.g., added sections in docs)
  - Configuration impact (e.g., dependency changes in package.json)
- **Edge cases**: 
  - New functions (no baseline to compare)
  - Deleted functions (should count as reviewed)
  - Moved functions (detect refactoring)
  - Configuration files (assess impact, not complexity)
- **Git operations**: Requires git repository and comparison branch

### Configuration

Add to CLI:
```bash
# Enable delta-based complexity analysis
python -m src.main src --review-strategy --review-branch-only --delta-complexity

# Compare with full-file analysis
python -m src.main src --review-strategy --review-branch-only --show-both
```

### Proof of Concept

See `tests/utilities/test_delta_complexity.py` for examples and edge cases.

---

**Status**: 📋 Planned for v2.0  
**Effort**: Medium (2-3 days implementation + testing)  
**Value**: High (significantly improves review time accuracy)
