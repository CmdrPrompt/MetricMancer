# Cognitive Complexity User Guide

**Version:** 3.2.0
**Language Support:** Python only (multi-language support planned)

## Table of Contents

1. [What is Cognitive Complexity?](#what-is-cognitive-complexity)
2. [Why Use Cognitive Complexity?](#why-use-cognitive-complexity)
3. [Understanding the Algorithm](#understanding-the-algorithm)
4. [Interpreting Results](#interpreting-results)
5. [Best Practices for Refactoring](#best-practices-for-refactoring)
6. [Viewing Cognitive Complexity](#viewing-cognitive-complexity)
7. [Cognitive vs Cyclomatic Complexity](#cognitive-vs-cyclomatic-complexity)
8. [FAQ](#faq)

## What is Cognitive Complexity?

Cognitive Complexity is a metric that measures **how difficult code is to understand** from a human perspective. Unlike Cyclomatic Complexity which counts the number of execution paths, Cognitive Complexity accounts for:

- **Nesting depth** - Deeply nested code is harder to understand
- **Control flow breaks** - Each `if`, `for`, `while` adds complexity
- **Structural patterns** - Flat code is easier than nested code

Cognitive Complexity was developed by SonarSource and is used in industry tools like SonarQube and CodeClimate.

**Example:**

```python
# Cyclomatic: 4, Cognitive: 3 (Easy to understand)
def process_flat(action):
    if action == "start": return start()
    if action == "stop": return stop()
    if action == "reset": return reset()
    return default()

# Cyclomatic: 4, Cognitive: 6 (Hard to understand!)
def process_nested(data):
    if data:                    # +1
        if data.is_valid:       # +2 (1 + 1 for nesting)
            if data.processed:  # +3 (1 + 2 for nesting)
                return process(data)
```

Both functions have the same Cyclomatic Complexity (4), but the nested version has double the Cognitive Complexity because it's much harder to understand.

## Why Use Cognitive Complexity?

### Problems with Cyclomatic Complexity Alone

Cyclomatic Complexity is excellent for:
- ✅ **Test coverage planning** - Tells you how many test cases you need
- ✅ **Path counting** - Measures execution path complexity

But it has limitations:
- ❌ **Doesn't reflect understandability** - Flat and nested code scored the same
- ❌ **False positives** - Simple `switch` statements get high scores
- ❌ **Misleading priorities** - Might flag easy-to-read code as complex

### Benefits of Cognitive Complexity

Cognitive Complexity excels at:
- ✅ **Refactoring prioritization** - Identifies truly hard-to-understand code
- ✅ **Code review focus** - Helps reviewers find the most challenging sections
- ✅ **Developer onboarding** - Shows new team members which code to avoid initially
- ✅ **Technical debt assessment** - Quantifies cognitive load objectively

### When to Use Which Metric

| Task | Use Cyclomatic | Use Cognitive | Use Both |
|------|----------------|---------------|----------|
| Plan test coverage | ✅ | ❌ | - |
| Prioritize refactoring | ❌ | ✅ | - |
| Code review planning | - | ✅ | - |
| Assess maintainability | - | - | ✅ |
| Onboarding assessment | - | ✅ | - |
| Complete health check | - | - | ✅ |

## Understanding the Algorithm

Cognitive Complexity follows these rules (per SonarSource specification):

### 1. Basic Increments (+1)

These structures add +1 complexity:
- `if`, `elif`, `else`
- `for`, `while` loops
- `except` blocks (exception handling)
- Ternary operators (`x if condition else y`)
- Recursion (function calling itself)

### 2. Nesting Penalty

**This is the key difference from Cyclomatic Complexity!**

Each level of nesting adds +1 to the increment:

```python
# Level 0 (no nesting)
if condition:        # +1 (0 nesting)
    do_something()

# Level 1 (nested once)
if outer:            # +1 (0 nesting)
    if inner:        # +2 (1 base + 1 nesting)
        do_something()

# Level 2 (nested twice)
if a:                # +1 (0 nesting)
    if b:            # +2 (1 base + 1 nesting)
        if c:        # +3 (1 base + 2 nesting)
            result()
```

**Total for deeply nested example: 1 + 2 + 3 = 6**

### 3. Boolean Operator Sequences

Sequences of `and`/`or` operators count as **+1 once**, not per operator:

```python
# Cognitive: +2 (not +4)
if a and b and c or d:  # +1 for if, +1 for boolean sequence
    do_something()
```

### 4. Recursion

Recursive calls add +1:

```python
def factorial(n):
    if n <= 1:          # +1
        return 1
    return n * factorial(n - 1)  # +1 (recursion)
# Total: 2
```

## Interpreting Results

### Recommended Thresholds

Based on SonarSource research and industry best practices:

| Cognitive Complexity | Risk Level | Indicator | Action |
|---------------------|------------|-----------|---------|
| **0-5** | ✅ Low | Green | Excellent maintainability. No action needed. |
| **6-10** | 🟡 Medium | Yellow | Good. Monitor for growth. Consider refactoring if increasing. |
| **11-15** | 🟠 High | Orange | Consider refactoring. Breaking into smaller functions would help. |
| **16-25** | 🔴 Critical | Red | Refactor soon. Code is difficult to understand and maintain. |
| **25+** | 💀 Severe | Dark Red | **Refactor immediately**. High risk of bugs and maintenance issues. |

### Real-World Interpretation

**Example: MetricMancer Code Review Advisor**

*Before refactoring:*
- Cyclomatic Complexity: 190
- Cognitive Complexity: 47 (🔴 Critical)
- Status: Hard to understand, high maintenance risk

*After refactoring:*
- Cyclomatic Complexity: 210 (+10%)
- Cognitive Complexity: 8 (🟡 Medium, -82%!)
- Status: Easy to understand, low maintenance risk

**Insight**: Cyclomatic went up slightly (more execution paths), but Cognitive dropped dramatically (much easier to understand). This is a successful refactoring!

## Best Practices for Refactoring

### Strategy 1: Extract Nested Logic

**Before (Cognitive: 9):**
```python
def process_order(order):
    if order:                           # +1
        if order.is_valid():            # +2
            if order.has_stock():       # +3
                if order.ship():        # +4 (hard to follow!)
                    return "Success"
```

**After (Cognitive: 4):**
```python
def process_order(order):
    if not order:                       # +1
        return None
    if not order.is_valid():            # +1
        return None
    if not order.has_stock():           # +1
        return None
    if order.ship():                    # +1
        return "Success"
```

**Technique**: Use guard clauses (early returns) to reduce nesting.

### Strategy 2: Extract Helper Functions

**Before (Cognitive: 12):**
```python
def analyze_user(user):
    if user:                            # +1
        if user.is_active:              # +2
            for order in user.orders:   # +3
                if order.total > 100:   # +4
                    # Complex processing...
```

**After (Cognitive: 2 + 4 = 6 total):**
```python
def analyze_user(user):
    if not user or not user.is_active:  # +2 (reduced!)
        return None
    return process_high_value_orders(user.orders)

def process_high_value_orders(orders):
    for order in orders:                # +1
        if order.total > 100:           # +2
            # Complex processing...
```

**Technique**: Extract nested logic into separate, well-named functions.

### Strategy 3: Use Data Structures

**Before (Cognitive: 10):**
```python
def get_discount(customer_type):
    if customer_type == "gold":         # +1
        if season == "holiday":         # +2
            return 0.30
        else:                           # +1
            return 0.20
    elif customer_type == "silver":     # +1
        # ... more nesting
```

**After (Cognitive: 1):**
```python
DISCOUNTS = {
    ("gold", "holiday"): 0.30,
    ("gold", "regular"): 0.20,
    ("silver", "holiday"): 0.15,
    # ...
}

def get_discount(customer_type):
    key = (customer_type, season)
    if key in DISCOUNTS:                # +1
        return DISCOUNTS[key]
```

**Technique**: Replace nested conditions with data structures (dicts, enums).

## Viewing Cognitive Complexity

### CLI Summary Report

```bash
python -m src.main src/ --output-format summary
```

Output shows both complexities:

```
📊 COMPLEXITY ANALYSIS
═══════════════════════════════════════

Critical Files (Cognitive Complexity > 15):

1. src/analysis/code_review_advisor.py
   Cyclomatic:  210  ⚠️  (Many paths)
   Cognitive:    47  🔴 (Hard to understand)
   Functions: 15 complex, 8 critical
   Recommendation: Reduce nesting, extract methods

2. src/utilities/git_cache.py
   Cyclomatic:  143  ⚠️  (Many paths)
   Cognitive:    89  💀 (Very hard to understand!)
   Functions: 22 complex, 12 critical
   Recommendation: Urgent refactoring needed
```

### HTML Reports

Interactive HTML reports with sortable tables:

```bash
python -m src.main src/ --output-format html
```

Features:
- **Sortable columns**: Click column headers to sort by Cognitive/Cyclomatic
- **Color coding**: Visual indicators for risk levels
- **Tabbed interface**: Overview, Quick Wins, Files, Functions
- **Function-level detail**: Drill down to specific functions

### JSON Export

For custom tooling and dashboards:

```bash
python -m src.main src/ --output-format json
```

JSON structure:

```json
{
  "files": [
    {
      "name": "analyzer.py",
      "cyclomatic_complexity": 15,
      "cognitive_complexity": 8,
      "functions": [
        {
          "name": "analyze",
          "cyclomatic_complexity": 6,
          "cognitive_complexity": 3
        }
      ]
    }
  ]
}
```

### Quick Wins Report

Prioritized refactoring recommendations:

```bash
python -m src.main src/ --output-format quick-wins
```

Quick Wins uses Cognitive Complexity to calculate refactoring ROI:

```
🎯 QUICK WINS - Top Refactoring Opportunities

1. Simplify: analysis/code_review_advisor.py
   Impact:  █████████░ Very High (9/10)
   Effort:  █████░░░░░ Medium (5/10)
   ROI:     1.8x (High impact, medium effort)

   Metrics:
   - Cognitive:    47 🔴 (Very hard to understand)
   - Cyclomatic:  210 ⚠️  (Many paths)
   - Churn:        15/month (Unstable)

   Action: Extract nested conditionals into helper methods
   Time:   4-6 hours
```

## Cognitive vs Cyclomatic Complexity

### Complementary Metrics

Think of them as measuring different aspects:

| Aspect | Cyclomatic | Cognitive |
|--------|-----------|-----------|
| **What it measures** | Number of execution paths | Mental effort to understand |
| **Best for** | Test coverage planning | Refactoring prioritization |
| **Algorithm** | Counts decision points | Counts + nesting penalty |
| **Flat code** | High score | Low score ✅ |
| **Nested code** | Same score | High score ⚠️ |
| **Goal** | Keep low for testability | Keep low for maintainability |

### Example Comparison

```python
# Scenario 1: Guard Clauses (GOOD)
def validate_flat(user):
    if not user: return False           # Cyc: +1, Cog: +1
    if not user.email: return False     # Cyc: +1, Cog: +1
    if not user.age >= 18: return False # Cyc: +1, Cog: +1
    if not user.verified: return False  # Cyc: +1, Cog: +1
    return True
# Total: Cyclomatic=4, Cognitive=4

# Scenario 2: Nested Conditions (BAD)
def validate_nested(user):
    if user:                            # Cyc: +1, Cog: +1
        if user.email:                  # Cyc: +1, Cog: +2
            if user.age >= 18:          # Cyc: +1, Cog: +3
                if user.verified:       # Cyc: +1, Cog: +4
                    return True
    return False
# Total: Cyclomatic=4, Cognitive=10
```

**Insight**: Same Cyclomatic (4), but Cognitive is 2.5× higher for nested version!

### When They Disagree

**High Cyclomatic, Low Cognitive:**
- Many simple conditions (guard clauses, switch statements)
- ✅ **Good code** - Easy to understand despite many paths
- 🎯 **Action**: Focus on test coverage, no urgent refactoring

**Low Cyclomatic, High Cognitive:**
- Deep nesting with few branches
- ⚠️ **Problematic code** - Hard to understand despite few paths
- 🎯 **Action**: Refactor to reduce nesting (extract functions, guard clauses)

**High Both:**
- Complex nested logic with many branches
- 🔴 **High risk** - Hard to test AND understand
- 🎯 **Action**: Urgent refactoring needed (highest priority)

## FAQ

### Q: My code has high Cyclomatic but low Cognitive. Is this okay?

**A:** Generally yes! This often indicates well-structured code with many simple cases (like guard clauses or switch statements). It's easy to understand but needs good test coverage. Focus on testing rather than refactoring.

### Q: Why does my Cognitive Complexity go up after refactoring?

**A:** This can happen if you convert flat code to nested code. Always aim to keep nesting shallow:
- ✅ Use early returns (guard clauses)
- ✅ Extract nested blocks to separate functions
- ❌ Avoid adding nesting levels

### Q: What's a good target for Cognitive Complexity?

**A:** Industry recommendations:
- **Functions**: Keep below 10 (ideally below 5)
- **Files**: Aggregate should be below 100
- **Modules**: Monitor trend, aim for decreasing over time

### Q: Can I configure Cognitive Complexity thresholds?

**A:** Not yet. Current implementation uses SonarSource's recommended thresholds. Custom thresholds are planned for a future release. Track the related issue for updates.

### Q: Does Cognitive Complexity work for all languages?

**A:** Currently **Python only**. Multi-language support (JavaScript, TypeScript, Java, C#, Go, etc.) is planned using tree-sitter parsers. See related GitHub issue for the multi-language implementation roadmap.

### Q: How does MetricMancer calculate Cognitive Complexity?

**A:** MetricMancer uses Python's AST (Abstract Syntax Tree) module to parse code and implements the SonarSource Cognitive Complexity algorithm. See [ARCHITECTURE.md](../ARCHITECTURE.md) for technical details.

### Q: Should I optimize for Cyclomatic or Cognitive first?

**A:** **Cognitive first** for maintainability! High Cognitive Complexity causes more day-to-day problems (bugs, slow development, hard reviews). Address Cyclomatic if test coverage is insufficient.

### Q: Can Cognitive Complexity detect all code smells?

**A:** No. Cognitive Complexity detects **structural complexity** but won't catch:
- Poor naming
- Duplicated code
- Long parameter lists
- Missing abstractions

Use it alongside code reviews and other quality metrics.

### Q: How often should I measure Cognitive Complexity?

**A:** Recommended schedule:
- **Every PR**: Check changed files in code reviews
- **Weekly/Sprint**: Track trends in CI/CD dashboards
- **Monthly**: Full codebase analysis to identify emerging hotspots
- **Quarterly**: Deep dive into highest-complexity areas

### Q: My team disagrees on complexity scores. How do I build consensus?

**A:** Tips for team adoption:
1. **Start with examples**: Show side-by-side flat vs nested code
2. **Use Quick Wins**: Focus on high-ROI refactorings first
3. **Set team thresholds**: Agree on acceptable ranges together
4. **Track trends**: Celebrate decreasing complexity over time
5. **Make it visible**: Include in code review checklists

### Q: Can I export Cognitive Complexity to our dashboard?

**A:** Yes! Use JSON output format:

```bash
python -m src.main src/ --output-format json --report-filename metrics.json
```

The JSON is compatible with dashboards like Grafana, Kibana, or custom tools.

## References

- [SonarSource Cognitive Complexity White Paper](https://www.sonarsource.com/docs/CognitiveComplexity.pdf) - Original specification
- [G. Ann Campbell - Cognitive Complexity: A new way of measuring understandability](https://www.sonarsource.com/resources/cognitive-complexity/) - Research paper
- Adam Tornhill - "Software Design X-Rays" (Chapter 4: Complexity Trends) - Book reference
- [MetricMancer ARCHITECTURE.md](../ARCHITECTURE.md) - Implementation details

## Support

For issues or questions:
- GitHub Issues: https://github.com/CmdrPrompt/MetricMancer/issues
- Documentation: See README.md and ARCHITECTURE.md
- Related Issue: Multi-language support roadmap

---

**MetricMancer v3.2.0** - Making code complexity visible and actionable.
