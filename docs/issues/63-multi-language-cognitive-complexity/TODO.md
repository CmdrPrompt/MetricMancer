# TODO List for Issue #63: Multi-Language Cognitive Complexity

## Phase 1: Infrastructure Setup ⏳

- [ ] Add dependencies to requirements.txt
  - [ ] `tree-sitter>=0.20.0`
  - [ ] `tree-sitter-languages>=1.10.0`
- [ ] Create abstract base class `CognitiveComplexityCalculatorBase`
- [ ] Refactor existing Python calculator to extend base class
- [ ] Create `tree_sitter_helper.py` utility module
- [ ] Update `CognitiveComplexityKPI.calculate()` to detect language
- [ ] Add unit tests for base infrastructure

## Phase 2: Java Support 🎯 (PRIORITY 1 - MOST IMPORTANT)

- [ ] Implement `JavaCognitiveComplexityCalculator`
  - [ ] Map tree-sitter node types to cognitive rules
  - [ ] Handle if/else statements
  - [ ] Handle loops (for, enhanced for, while, do-while)
  - [ ] Handle switch statements
  - [ ] Handle ternary operators (? :)
  - [ ] Handle logical operators (&&, ||)
  - [ ] Handle try/catch/finally
  - [ ] Handle try-with-resources
  - [ ] Handle lambda expressions
  - [ ] Handle streams (optional chaining)
  - [ ] Handle nesting increments
- [ ] Create comprehensive test suite
  - [ ] Simple control flow tests
  - [ ] Nested control flow tests
  - [ ] Real-world Java code tests (Spring Boot, etc.)
  - [ ] Edge cases (nested lambdas, etc.)
- [ ] Verify against SonarQube/SonarSource for Java
- [ ] Update documentation

## Phase 3: Ada Support 🎯 (PRIORITY 2)

- [ ] Implement `AdaCognitiveComplexityCalculator`
  - [ ] Map Ada control structures
  - [ ] Handle if/elsif/else statements
  - [ ] Handle loops (loop, while, for)
  - [ ] Handle case statements
  - [ ] Handle exception handlers
  - [ ] Handle tasks and protected objects
  - [ ] Handle packages and generics
  - [ ] Handle nesting increments
- [ ] Create Ada test suite
  - [ ] Simple control flow tests
  - [ ] Real-world Ada code tests
  - [ ] Ada-specific constructs (tasks, etc.)
- [ ] Update documentation

## Phase 4: Go Support 🎯 (PRIORITY 3)

- [ ] Implement `GoCognitiveComplexityCalculator`
  - [ ] Map Go control structures
  - [ ] Handle if/else statements
  - [ ] Handle for loops (Go's only loop type)
  - [ ] Handle switch statements
  - [ ] Handle select statements (channel operations)
  - [ ] Handle defer statements
  - [ ] Handle goroutines
  - [ ] Handle channels
  - [ ] Handle nesting increments
- [ ] Create Go test suite
  - [ ] Simple control flow tests
  - [ ] Concurrency patterns (goroutines, channels)
  - [ ] Real-world Go code tests
- [ ] Update documentation

## Phase 5: JavaScript/TypeScript Support 📱

- [ ] Implement `JavaScriptCognitiveComplexityCalculator`
  - [ ] Map JS control structures
  - [ ] Handle if/else statements
  - [ ] Handle loops (for, for-in, for-of, while, do-while)
  - [ ] Handle switch statements
  - [ ] Handle ternary operators
  - [ ] Handle logical operators (&&, ||, ??)
  - [ ] Handle try/catch
  - [ ] Handle arrow functions
  - [ ] Handle async/await
  - [ ] Handle nesting increments
- [ ] Test with BlockAssistant project
- [ ] Verify against SonarSource examples
- [ ] Update documentation

## Phase 6: C# Support 💼

- [ ] Implement `CSharpCognitiveComplexityCalculator`
  - [ ] Map C# control structures
  - [ ] Handle LINQ expressions
  - [ ] Handle async/await
  - [ ] Handle pattern matching
  - [ ] Handle null-coalescing operators
- [ ] Create C# test suite
- [ ] Update documentation

## Phase 7: C/C++ Support 🔧

- [ ] Implement `CCognitiveComplexityCalculator`
  - [ ] Map C control structures
  - [ ] Handle pointers and memory operations
- [ ] Implement `CppCognitiveComplexityCalculator`
  - [ ] Extend C calculator
  - [ ] Handle templates
  - [ ] Handle operator overloading
  - [ ] Handle RAII patterns
- [ ] Create test suites
- [ ] Update documentation

## Phase 8: Shell Script Support 🐚

- [ ] Implement `ShellCognitiveComplexityCalculator`
  - [ ] Handle if/elif/else
  - [ ] Handle loops (for, while, until)
  - [ ] Handle case statements
  - [ ] Handle pipes and redirections (if applicable)
- [ ] Create shell script test suite
- [ ] Update documentation

## Integration & Polish ✨

- [ ] Update HTML report templates to show cognitive complexity for all languages
- [ ] Update JSON report format
- [ ] Update CLI help text with language support matrix
- [ ] Update README.md with complete language support table
- [ ] Update CLAUDE.md with tree-sitter dependency notes
- [ ] Regression testing (ensure all 670+ tests still pass)
- [ ] Performance testing on large multi-language codebases
- [ ] Add example reports for each language to documentation

## Acceptance Testing 🎭

- [ ] Test Java project - verify Cog values
- [ ] Test Ada project - verify Cog values
- [ ] Test Go project - verify Cog values
- [ ] Test BlockAssistant (JS/JSX) - verify Cog values
- [ ] Test MetricMancer itself (Python) - verify no regression
- [ ] Generate multi-format reports - verify all formats work
- [ ] Compare results with SonarQube for validation

## Documentation 📚

- [ ] README.md - add complete language support matrix
- [ ] CLAUDE.md - document tree-sitter setup
- [ ] Add code examples for each language
- [ ] Update changelog
- [ ] Create language-specific analysis examples

---

## Language Priority Summary

1. **Java** - Enterprise, most important
2. **Ada** - Specialized, high priority
3. **Go** - Modern systems programming
4. **JavaScript/TypeScript** - Web development
5. **C#** - .NET ecosystem
6. **C/C++** - Systems/legacy
7. **Shell** - DevOps/automation

**Note:** JSON/YAML don't need cognitive complexity (data formats)

---

**Estimated Total Effort:** 5-7 days (can be done incrementally)
- Phase 1: 1 day
- Phase 2 (Java): 1 day
- Phase 3 (Ada): 0.5 day
- Phase 4 (Go): 0.5 day
- Phase 5-8: 2 days
- Testing & Documentation: 1 day
