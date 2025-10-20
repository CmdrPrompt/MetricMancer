# Issue #63: Multi-Language Cognitive Complexity Support

**Status:** 📋 Planned
**Priority:** Medium
**Effort:** Large (3-5 days)
**Created:** 2025-10-19

## Problem Statement

Currently, cognitive complexity is **only calculated for Python files**. When analyzing JavaScript, TypeScript, Java, or other languages, cognitive complexity shows as `Cog: ?` in reports.

This is because the current implementation uses Python's `ast` module which only parses Python code.

### Current Behavior:
- ✅ **Python:** Cognitive complexity calculated correctly
- ❌ **JavaScript/JSX:** Shows `Cog: ?`
- ❌ **TypeScript/TSX:** Shows `Cog: ?`
- ❌ **Java:** Shows `Cog: ?`
- ❌ **Go, C#, C++:** Shows `Cog: ?`

### Impact:
- Users analyzing multi-language codebases get incomplete metrics
- Cognitive complexity (a key metric for code understandability) is missing for non-Python projects
- Reports are less useful for JavaScript/TypeScript projects (very common)

## Proposed Solution: Tree-sitter Integration

Use [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - a universal parser generator that supports 50+ languages.

### Why Tree-sitter?

**Advantages:**
- ✅ **Universal:** One solution for all languages
- ✅ **Python bindings:** `tree-sitter` and `tree-sitter-languages` packages
- ✅ **Language support:** JavaScript, TypeScript, Java, Go, C#, C++, Rust, Ruby, etc.
- ✅ **Battle-tested:** Used by GitHub, Atom editor, Neovim
- ✅ **Fast:** Incremental parsing, efficient
- ✅ **Consistent API:** Same interface across all languages
- ✅ **Active:** Well-maintained with strong community

**Alternatives Considered:**
- ❌ **Language-specific parsers** (esprima for JS, javalang for Java, etc.)
  - Too many dependencies to manage
  - Different APIs for each language
  - More complex integration
- ❌ **Regex-based approximation**
  - Inaccurate
  - Doesn't follow SonarSource specification
  - Misses nesting context

## Technical Design

### Architecture

```
src/kpis/cognitive_complexity/
├── cognitive_complexity_kpi.py       # Main KPI class (updated)
├── calculator_base.py                # NEW: Abstract base calculator
├── calculator_python.py              # Current Python implementation (refactored)
├── calculator_javascript.py          # NEW: JavaScript/TypeScript calculator
├── calculator_java.py                # NEW: Java calculator
├── calculator_go.py                  # NEW: Go calculator
└── tree_sitter_helper.py             # NEW: Tree-sitter utilities
```

### Implementation Plan

#### Phase 1: Infrastructure Setup
1. Add dependencies to `requirements.txt`:
   ```
   tree-sitter>=0.20.0
   tree-sitter-languages>=1.10.0
   ```
2. Create abstract base class `CognitiveComplexityCalculator` with interface:
   ```python
   class CognitiveComplexityCalculator(ABC):
       @abstractmethod
       def calculate_for_function(self, node) -> int:
           pass

       @abstractmethod
       def get_functions(self, tree) -> List[FunctionNode]:
           pass
   ```
3. Refactor existing Python calculator to extend base class
4. Create tree-sitter helper utilities

#### Phase 2: Java Support (Priority 1 - Most Important)
1. Implement `JavaCognitiveComplexityCalculator`
2. Map tree-sitter node types to cognitive complexity rules
3. Handle Java-specific constructs (enhanced for, streams, try-with-resources, etc.)
4. Write comprehensive tests
5. Validate against SonarQube for Java projects

#### Phase 3: Ada Support (Priority 2)
1. Implement `AdaCognitiveComplexityCalculator`
2. Map Ada control structures (if/elsif/else, loop/while/for, case)
3. Handle Ada-specific constructs (tasks, protected objects, packages)
4. Write comprehensive tests

#### Phase 4: Go Support (Priority 3)
1. Implement `GoCognitiveComplexityCalculator`
2. Map Go control structures (if, for, select, switch)
3. Handle Go-specific constructs (goroutines, defer, channels)
4. Write comprehensive tests

#### Phase 5: Remaining Languages (All Currently Supported)
**In priority order based on MetricMancer's current language support:**
1. **JavaScript/JSX** - Web development
2. **TypeScript/TSX** - Modern web development
3. **C#** - Enterprise .NET projects
4. **C** - System programming
5. **C++** - System/game development
6. **Shell scripts (.sh, .bash)** - DevOps/automation
7. **IDL** - Interface definitions

**Note:** JSON/YAML likely don't need cognitive complexity (data formats, not code)

### Code Example

```python
# tree_sitter_helper.py
from tree_sitter_languages import get_parser

def parse_file(file_content: str, language: str):
    """Parse source code using tree-sitter."""
    parser = get_parser(language)
    tree = parser.parse(bytes(file_content, 'utf8'))
    return tree

# calculator_javascript.py
class JavaScriptCognitiveComplexityCalculator(CognitiveComplexityCalculator):

    INCREMENTS = {
        'if_statement': 1,
        'else_clause': 1,
        'for_statement': 1,
        'while_statement': 1,
        # ... etc
    }

    def calculate_for_function(self, function_node) -> int:
        """Calculate cognitive complexity for a JavaScript function."""
        complexity = 0
        nesting_level = 0

        def traverse(node, nesting):
            nonlocal complexity

            if node.type in self.INCREMENTS:
                complexity += 1 + nesting

            # Handle nesting
            new_nesting = nesting
            if node.type in self.NESTING_INCREMENTS:
                new_nesting += 1

            for child in node.children:
                traverse(child, new_nesting)

        traverse(function_node, 0)
        return complexity
```

### Testing Strategy

1. **Unit tests** for each language calculator
2. **Integration tests** with real-world code samples
3. **Regression tests** to ensure Python implementation still works
4. **Test files** from actual projects (e.g., React, Vue, Spring Boot)
5. **Comparison tests** against SonarQube/SonarSource results

### Breaking Changes

**None** - This is a pure enhancement:
- Existing Python support continues to work
- API remains the same
- New languages just return values instead of `None`

### Documentation Updates

1. Update `README.md` - add supported languages for cognitive complexity
2. Update `CLAUDE.md` - document tree-sitter dependency
3. Add language-specific examples to docs
4. Update HTML report to show cognitive complexity for all languages

## Acceptance Criteria

- [ ] Tree-sitter dependencies installed and working
- [ ] JavaScript/TypeScript cognitive complexity calculated correctly
- [ ] Java cognitive complexity calculated correctly
- [ ] Python cognitive complexity still works (regression test)
- [ ] All 670+ tests still pass
- [ ] New tests for JavaScript/TypeScript/Java added (>90% coverage)
- [ ] Documentation updated
- [ ] HTML reports show cognitive complexity for all supported languages
- [ ] BlockAssistant example shows `Cog: 7` instead of `Cog: ?`

## Success Metrics

**Before:**
```
BlockAssistant Analysis:
- applyBlockDiceResult.js: C: 23, Cog: ?
- getAssists.js: C: 20, Cog: ?
```

**After:**
```
BlockAssistant Analysis:
- applyBlockDiceResult.js: C: 23, Cog: 18
- getAssists.js: C: 20, Cog: 15
```

## References

- [SonarSource Cognitive Complexity Spec](https://www.sonarsource.com/docs/CognitiveComplexity.pdf)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Tree-sitter Python Bindings](https://github.com/tree-sitter/py-tree-sitter)
- [Tree-sitter Languages Package](https://github.com/grantjenks/py-tree-sitter-languages)

## Related Issues

- #62 - Cognitive Complexity for Python (Completed)
- Future: #64 - Performance optimization for large codebases

## Notes

- Tree-sitter is an **optional** enhancement - the tool works fine without it
- Consider making tree-sitter an optional dependency (extra: `pip install metricmancer[full]`)
- Can be implemented incrementally (JavaScript first, then others)
- Each language calculator is independent - easy to add new languages

---

**Estimated Effort Breakdown:**
- Phase 1 (Infrastructure): 1 day
- Phase 2 (JavaScript/TypeScript): 1-2 days
- Phase 3 (Java): 0.5 day
- Phase 3 (Go): 0.5 day
- Testing & Documentation: 1 day

**Total: 4-5 days**
