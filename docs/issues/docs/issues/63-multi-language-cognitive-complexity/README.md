# Issue #63: Multi-Language Cognitive Complexity Support

**Status:** 📋 Planned  
**Priority:** Medium  
**Effort:** Large (3-5 days)  
**Created:** 2025-10-19

## Problem Statement

Currently, cognitive complexity is **only calculated for Python files**. When analyzing JavaScript, TypeScript, Java, or other languages, cognitive complexity shows as `Cog: ?` in reports.

### Current Behavior:
- ✅ **Python:** Cognitive complexity calculated correctly
- ❌ **JavaScript/JSX:** Shows `Cog: ?`
- ❌ **TypeScript/TSX:** Shows `Cog: ?`  
- ❌ **Java, Go, C#, C++:** Shows `Cog: ?`

### Impact:
Cognitive complexity (a key metric for code understandability) is missing for non-Python projects.

## Proposed Solution: Tree-sitter Integration

Use [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - a universal parser supporting 50+ languages.

### Why Tree-sitter?

- ✅ One solution for all languages
- ✅ Python bindings available
- ✅ Used by GitHub, Atom, Neovim
- ✅ Supports: JavaScript, TypeScript, Java, Go, C#, C++, Rust, etc.

## Implementation Plan

### Phase 1: Infrastructure
1. Add dependencies: `tree-sitter`, `tree-sitter-languages`
2. Create abstract base `CognitiveComplexityCalculator`
3. Refactor Python calculator to extend base

### Phase 2: JavaScript/TypeScript
1. Implement `JavaScriptCognitiveComplexityCalculator`
2. Map tree-sitter nodes to cognitive rules
3. Comprehensive testing

### Phase 3: Additional Languages
1. Java calculator
2. Go calculator (optional)
3. C#, C++ calculators (optional)

## Success Metrics

**Before:**
```
BlockAssistant: applyBlockDiceResult.js: C: 23, Cog: ?
```

**After:**
```
BlockAssistant: applyBlockDiceResult.js: C: 23, Cog: 18
```

## References

- [SonarSource Cognitive Complexity Spec](https://www.sonarsource.com/docs/CognitiveComplexity.pdf)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [py-tree-sitter](https://github.com/tree-sitter/py-tree-sitter)

## Related Issues

- #62 - Cognitive Complexity for Python (✅ Completed)

---

See `IMPLEMENTATION_GUIDE.md` for detailed technical guide.  
See `TODO.md` for task checklist.
