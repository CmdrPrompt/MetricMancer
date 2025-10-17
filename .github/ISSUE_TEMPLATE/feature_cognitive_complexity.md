---
name: Feature Request - Cognitive Complexity Metric
about: Add Cognitive Complexity as a new KPI metric
title: '[FEATURE] Add Cognitive Complexity metric to complement Cyclomatic Complexity'
labels: enhancement, good first issue, help wanted
assignees: ''
---

## 🎯 Feature Request: Cognitive Complexity Metric

### 📋 Summary

Add **Cognitive Complexity** as a new KPI metric to complement Cyclomatic Complexity, providing a more human-centric measure of code understandability based on the SonarSource algorithm.

### 🤔 Motivation

**Current limitation:**
- Cyclomatic Complexity (CC) measures the number of execution paths but doesn't capture how **difficult code is to understand**
- Flat code with many simple conditions can have high CC but is easy to understand
- Nested code with fewer paths can have lower CC but is much harder to understand

**Real-world example from our codebase:**

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
        if data.valid:          # +2 (1 + 1 for nesting)
            if data.processed:  # +3 (1 + 2 for nesting)
                return result
```

**Why this matters:**
- ✅ Aligns with Adam Tornhill's "Your Code as a Crime Scene" philosophy
- ✅ Better prioritization of refactoring efforts
- ✅ Feature parity with industry tools (SonarQube, CodeClimate)
- ✅ Helps identify truly problematic code for code reviews

### 💡 Proposed Solution

Implement Cognitive Complexity based on the [SonarSource specification](https://www.sonarsource.com/docs/CognitiveComplexity.pdf):

#### Key Algorithm Points:

1. **Basic increment (+1)**: `if`, `else`, `for`, `while`, `except`, ternary operators
2. **Nesting penalty**: Each level of nesting adds +1 to the increment
3. **Logical operators**: Sequences of `and`/`or` count as +1 (not per operator)
4. **Recursion**: +1 for recursive calls

#### Example Calculation:

```python
def example(x, y, z):
    if x:                    # +1 (base increment)
        if y:                # +2 (1 base + 1 nesting penalty)
            if z:            # +3 (1 base + 2 nesting penalty)
                return True
        
    for item in items:       # +1 (base increment)
        if item.valid:       # +2 (1 base + 1 nesting penalty)
            process(item)
    
    # Total Cognitive Complexity: 9
```

### 🏗️ Implementation Plan

#### Phase 1: Core Implementation (2-4 hours)
- [ ] Create `src/kpis/cognitive_complexity/cognitive_complexity_kpi.py`
- [ ] Implement SonarSource algorithm for Python AST
- [ ] Add unit tests for algorithm edge cases
- [ ] Document calculation methodology

#### Phase 2: Parser Integration (2-3 hours)
- [ ] Update `src/languages/parsers/python_parser.py` to calculate Cognitive Complexity
- [ ] Add `cognitive_complexity` field to function analysis results
- [ ] Support other language parsers (Java, JavaScript, etc.)
- [ ] Integration tests

#### Phase 3: Data Model Updates (1-2 hours)
- [ ] Add `cognitive_complexity` property to `ScanFile` class
- [ ] Update aggregation functions to handle new metric
- [ ] Add to JSON/HTML export schemas

#### Phase 4: Reporting (3-4 hours)
- [ ] Add Cognitive Complexity to CLI summary format
- [ ] Add column to HTML report tables
- [ ] Integrate into Quick Wins analysis
- [ ] Update Code Review Advisor to use Cognitive Complexity

#### Phase 5: Configuration & Documentation (1-2 hours)
- [ ] Add `--cognitive-threshold-high` and `--cognitive-threshold-medium` CLI flags
- [ ] Add `enable_cognitive_complexity` config option
- [ ] Update README with explanation and examples
- [ ] Update ARCHITECTURE.md with design decisions

**Total Estimated Time:** 9-15 hours

### 📊 Acceptance Criteria

- [ ] Cognitive Complexity calculated correctly per SonarSource spec
- [ ] All existing tests still pass
- [ ] New tests achieve >90% coverage for new code
- [ ] CLI reports show both Cyclomatic and Cognitive Complexity
- [ ] HTML reports display new metric in tables
- [ ] Quick Wins analysis incorporates Cognitive Complexity
- [ ] Documentation updated with examples
- [ ] Backward compatible (existing configs still work)

### 🎨 User Interface Examples

#### CLI Summary Output:
```bash
📊 COMPLEXITY ANALYSIS
═══════════════════════════════════════

Critical Files (Cognitive Complexity > 15):

1. src/analysis/code_review_advisor.py
   Cyclomatic Complexity:  210  ⚠️  High paths
   Cognitive Complexity:    47  🔴 Hard to understand
   Recommendation: Reduce nesting, extract methods

2. src/utilities/git_cache.py  
   Cyclomatic Complexity:  143  ⚠️  High paths
   Cognitive Complexity:    89  💀 Very hard to understand  
   Recommendation: Urgent refactoring needed
```

#### Quick Wins Analysis:
```bash
🎯 QUICK WINS - Top Refactoring Opportunities

1. Simplify: utilities/git_cache.py
   Impact:  █████████░ Very High (9/10)
   Effort:  █████░░░░░ Medium (5/10)
   Time:    2-4 hours
   
   Metrics:
   - Cyclomatic:  143 (High paths)
   - Cognitive:    89 🔴 (Very hard to understand)
   - Churn:        15/month (Unstable)
   
   Action: Reduce nesting depth and extract helper methods
```

### 📈 Thresholds (Based on SonarQube)

| Cognitive Complexity | Risk Level | Indicator | Recommendation |
|---------------------|------------|-----------|----------------|
| 0-5                 | ✅ Low     | Green     | Excellent      |
| 6-10                | 🟡 Medium  | Yellow    | Good           |
| 11-15               | 🟠 High    | Orange    | Consider refactoring |
| 16-25               | 🔴 Critical| Red       | Refactor soon  |
| 25+                 | 💀 Severe  | Dark Red  | Refactor immediately |

### 🔗 References

1. [SonarSource Cognitive Complexity White Paper](https://www.sonarsource.com/docs/CognitiveComplexity.pdf)
2. [G. Ann Campbell - Cognitive Complexity: A new way of measuring understandability](https://www.sonarsource.com/resources/cognitive-complexity/)
3. Adam Tornhill - "Software Design X-Rays" (Chapter 4: Complexity Trends)
4. [CodeClimate Cognitive Complexity Documentation](https://docs.codeclimate.com/docs/cognitive-complexity)

### 🚀 Future Enhancements (Out of Scope for v1)

- **Cognitive Hotspots**: `Cognitive Complexity × Churn` metric
- **Function-level reporting**: Detailed per-function cognitive analysis
- **Trend tracking**: Monitor cognitive complexity improvements over time
- **AI-assisted refactoring**: LLM suggestions for reducing cognitive load
- **IDE integration**: Real-time cognitive complexity in editor

### 💬 Additional Context

This feature was identified during refactoring of `code_review_advisor.py` where:
- Total Cyclomatic Complexity: 190 → 210 (+10%)
- But Cognitive Complexity: ~45 → ~8 (-82%!)

The refactoring improved code understandability significantly despite a slight increase in measured cyclomatic complexity, demonstrating the need for this complementary metric.

### 📝 Related Issues

- None yet (new feature)

### 🏷️ Labels

`enhancement`, `good first issue`, `help wanted`, `metrics`, `code-quality`

---

**Note:** Full technical specification available in `FEATURE_PROPOSAL_COGNITIVE_COMPLEXITY.md`
