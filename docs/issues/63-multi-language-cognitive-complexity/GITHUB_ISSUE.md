# Multi-Language Support for Cognitive Complexity

## 📋 Summary

Add cognitive complexity calculation for JavaScript, TypeScript, Java, and other languages using Tree-sitter.

Currently, cognitive complexity only works for Python files. For all other languages, reports show `Cog: ?`.

## 🎯 Motivation

When analyzing the BlockAssistant JavaScript/React project, we get:

**Current:**
```
applyBlockDiceResult.js: C: 23, Cog: ?  ❌
getAssists.js: C: 20, Cog: ?            ❌
```

**Expected:**
```
applyBlockDiceResult.js: C: 23, Cog: 18  ✅
getAssists.js: C: 20, Cog: 15            ✅
```

Cognitive complexity is a valuable metric for code understandability, especially for complex JavaScript codebases.

## 💡 Proposed Solution

Integrate [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) - a universal parser that supports 50+ languages.

### Implementation Plan

**Phase 1:** JavaScript/TypeScript support (highest priority)
**Phase 2:** Java support
**Phase 3:** Go, C#, C++ support (optional)

### Technical Approach

1. Add dependencies: `tree-sitter`, `tree-sitter-languages`
2. Create language-specific calculators extending base class
3. Map tree-sitter node types to cognitive complexity rules
4. Update `CognitiveComplexityKPI` to detect language and use appropriate calculator

## 📊 Success Criteria

- [ ] JavaScript/JSX files show cognitive complexity values
- [ ] TypeScript/TSX files show cognitive complexity values
- [ ] Python files still work correctly (no regression)
- [ ] All existing tests pass
- [ ] New tests for JavaScript/TypeScript added
- [ ] Documentation updated

## 🔗 References

- Full design doc: `docs/issues/63-multi-language-cognitive-complexity/README.md`
- Implementation guide: `docs/issues/63-multi-language-cognitive-complexity/IMPLEMENTATION_GUIDE.md`
- [SonarSource Cognitive Complexity Spec](https://www.sonarsource.com/docs/CognitiveComplexity.pdf)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)

## 🏷️ Labels

`enhancement`, `cognitive-complexity`, `multi-language`, `tree-sitter`

## 📅 Estimated Effort

**3-5 days** (can be done incrementally)

---

*This issue was created after successfully analyzing the BlockAssistant JavaScript/React project and discovering the cognitive complexity limitation.*
