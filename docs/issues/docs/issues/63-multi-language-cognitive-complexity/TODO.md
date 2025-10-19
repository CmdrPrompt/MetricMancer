# TODO List for Issue #63

## Phase 1: Infrastructure Setup ⏳

- [ ] Add dependencies to requirements.txt
  - [ ] `tree-sitter>=0.20.0`
  - [ ] `tree-sitter-languages>=1.10.0`
- [ ] Create abstract base class `CognitiveComplexityCalculatorBase`
- [ ] Refactor existing Python calculator to extend base class
- [ ] Create `tree_sitter_helper.py` utility module
- [ ] Update `CognitiveComplexityKPI.calculate()` to detect language
- [ ] Add unit tests for base infrastructure

## Phase 2: JavaScript/TypeScript Support 🎯

- [ ] Implement `JavaScriptCognitiveComplexityCalculator`
  - [ ] Map tree-sitter node types to cognitive rules
  - [ ] Handle if/else statements
  - [ ] Handle loops (for, while, do-while)
  - [ ] Handle switch statements
  - [ ] Handle ternary operators
  - [ ] Handle logical operators (&&, ||)
  - [ ] Handle try/catch
  - [ ] Handle arrow functions
  - [ ] Handle nesting increments
- [ ] Create comprehensive test suite
  - [ ] Simple control flow tests
  - [ ] Nested control flow tests
  - [ ] Real-world code tests (BlockAssistant files)
  - [ ] Edge cases (anonymous functions, etc.)
- [ ] Verify against SonarSource examples
- [ ] Update documentation

## Phase 3: Java Support 🎯

- [ ] Implement `JavaCognitiveComplexityCalculator`
- [ ] Map Java control structures
- [ ] Handle Java-specific constructs (enhanced for, etc.)
- [ ] Add Java test suite
- [ ] Update documentation

## Phase 4: Additional Languages (Optional) 🔮

- [ ] Go support
- [ ] C# support
- [ ] C++ support
- [ ] Rust support

## Phase 5: Integration & Polish ✨

- [ ] Update HTML report templates
- [ ] Update JSON report format
- [ ] Update CLI help text
- [ ] Update README.md with language support matrix
- [ ] Update CLAUDE.md with tree-sitter dependency
- [ ] Regression testing (ensure all 670+ tests still pass)
- [ ] Performance testing on large codebases
- [ ] Add example reports to documentation

## Acceptance Testing 🎭

- [ ] Analyze BlockAssistant - verify Cog values show up
- [ ] Analyze a Java project - verify results
- [ ] Analyze MetricMancer itself - verify Python still works
- [ ] Generate multi-format reports - verify all formats work
- [ ] Compare results with SonarQube for validation

## Documentation 📚

- [ ] README.md - add language support matrix
- [ ] CLAUDE.md - document tree-sitter dependency
- [ ] Add code examples for each language
- [ ] Update changelog
- [ ] Add migration guide (if any breaking changes)

---

**Priority:** Phase 1 + Phase 2 (JavaScript/TypeScript) first
**Estimated Time:** 3-4 days
**Can be done incrementally:** Yes - each language is independent
