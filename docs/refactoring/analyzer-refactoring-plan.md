# Refaktoreringsplan: MetricMancer - Ongoing Architectural Improvements

**Document Version:** 2.0
**Last Updated:** 2025-10-17
**Status:** ✅ Phase 5 Complete - Identifying Next Priorities

---

## 📊 Executive Summary

The original `analyzer.py` refactoring (Phase 1-5) has been **partially completed**. The monolithic 331-line file has been split into a modular architecture with domain-based organization.

**Current Status:**
- ✅ Original `src/app/analyzer.py`: **C:90 → C:0** (now a simple delegator)
- ⚠️ New `src/app/core/analyzer.py`: **C:98** (complexity relocated, still too high)
- ✅ Phase 5 restructuring: Domain-based organization (`app/core/`, `app/kpi/`, `app/hierarchy/`)
- 🔴 **Critical issue**: Complexity was redistributed, not eliminated
- ⚠️ Multiple new hotspots identified requiring immediate attention

---

## 🎯 Current State Analysis

### ✅ Completed Refactoring (Phase 1-5)

The modular architecture is now in place:

```
src/app/
├── core/                          # Core analysis logic
│   ├── analyzer.py                C:98 (main orchestrator - needs attention)
│   └── file_processor.py          C:34
├── kpi/                           # KPI calculation
│   ├── kpi_calculator.py          C:45
│   ├── kpi_aggregator.py          C:50
│   └── file_analyzer.py           C:34
├── hierarchy/                     # Data model construction
│   ├── hierarchy_builder.py       C:20
│   └── data_converter.py          C:0
├── coordination/                  # Workflow coordination
│   ├── report_coordinator.py      C:53 (needs attention)
│   ├── hotspot_coordinator.py     C:7
│   └── review_coordinator.py      C:8
├── scanning/                      # File scanning
│   └── scanner.py                 C:20
└── infrastructure/                # Cross-cutting concerns
    └── timing_reporter.py         C:20
```

**Achievements:**
- ✅ Single Responsibility Principle applied
- ✅ Dependency Injection implemented
- ✅ Strategy Pattern for KPI calculation
- ✅ Factory Pattern for report generation
- ✅ Domain-based organization (follows ARCHITECTURE.md)
- ✅ 579 passing tests (100% pass rate)

---

## 🔥 New Critical Hotspots (Oct 2025)

Analysis of current codebase reveals **new** complexity hotspots that need attention:

| File | Complexity | Churn | Hotspot | Priority | Owner |
|------|-----------|-------|---------|----------|-------|
| **analysis/code_review_advisor.py** | **190** | 3 | 570 | 🔴 CRITICAL | Commander Prompt |
| **utilities/git_cache.py** | **142** | 5 | 710 | 🔴 CRITICAL | Commander Prompt |
| **report/cli/cli_report_format.py** | **112** | 8 | 896 | 🔴 CRITICAL | Thomas Lindqvist |
| **report/cli/cli_quick_wins_format.py** | **111** | 3 | 333 | 🟡 HIGH | Commander Prompt |
| **app/core/analyzer.py** | **98** | 2 | 196 | 🟡 HIGH | Thomas Lindqvist |
| **languages/parsers/json_yaml.py** | **94** | 2 | 188 | 🟡 HIGH | Commander Prompt |
| **report/cli/cli_summary_format.py** | **85** | 3 | 255 | 🟡 HIGH | Commander Prompt |
| **app/metric_mancer_app.py** | **50** | 15 | 750 | 🟡 HIGH | Commander Prompt |
| **app/coordination/report_coordinator.py** | **53** | 2 | 106 | 🟢 MEDIUM | Commander Prompt |

**Note:** Files with C:0 (like old `analyzer.py`) have been successfully refactored and are now simple delegation points.

---

## 📋 Prioritized Refactoring Roadmap

### Priority 1: Code Review Advisor (C:190)

**File:** `src/analysis/code_review_advisor.py`
**Current State:** 190 complexity, 570 hotspot score
**Risk:** CRITICAL - highest complexity in entire codebase

**Issues:**
- Monolithic file with too many responsibilities
- Complex conditional logic for risk assessment
- Multiple nested functions handling different aspects

**Recommended Actions:**
1. Extract risk assessment logic into separate strategies
2. Create dedicated classes for:
   - `RiskCategorizer` - categorizes files by risk level
   - `ReviewRecommendationGenerator` - generates specific recommendations
   - `ChecklistGenerator` - creates review checklists
   - `TimeEstimator` - calculates review time estimates
3. Apply Strategy Pattern for different risk assessment algorithms
4. Target: Reduce complexity to <40 across multiple modules

**Alignment with ARCHITECTURE.md:**
- ✅ Follow Strategy Pattern (already used in report generation)
- ✅ Apply Single Responsibility Principle
- ✅ Use Dependency Injection for testability

---

### Priority 2: Git Cache (C:142)

**File:** `src/utilities/git_cache.py`
**Current State:** 142 complexity, 710 hotspot score
**Risk:** CRITICAL - high complexity + moderate churn

**Issues:**
- Handles caching, git operations, and data processing
- Multiple cache types (ownership, churn, blame, tracked files)
- Complex cache invalidation logic

**Recommended Actions:**
1. Split into focused classes:
   - `GitCommandExecutor` - execute git commands
   - `OwnershipCache` - cache ownership data
   - `ChurnCache` - cache churn data
   - `BlameCache` - cache blame data
   - `GitCacheManager` - orchestrate cache operations
2. Extract cache pre-building logic to separate module
3. Apply Cache Pattern with clear interfaces
4. Target: Reduce complexity to <30 per module

**Alignment with ARCHITECTURE.md:**
- ✅ Single Responsibility (one cache type per class)
- ✅ Interface Segregation (specific cache interfaces)
- ✅ Dependency Injection (cache strategies)

---

### Priority 3: CLI Report Format (C:112)

**File:** `src/report/cli/cli_report_format.py`
**Current State:** 112 complexity, 896 hotspot score (highest!)
**Risk:** CRITICAL - high complexity + high churn

**Issues:**
- Monolithic report generation logic
- Complex tree rendering with many conditionals
- Mixes data collection, formatting, and output

**Recommended Actions:**
1. Extract components:
   - `TreeBuilder` - constructs tree structure
   - `NodeFormatter` - formats individual nodes
   - `ColorScheme` - handles colors/emojis
   - `OutputWriter` - writes to console
2. Apply Composite Pattern for tree structure
3. Use Builder Pattern for constructing complex output
4. Target: Reduce to <25 per module

**Alignment with ARCHITECTURE.md:**
- ✅ Builder Pattern (already used in report_data_collector)
- ✅ Separation of Concerns
- ✅ Open/Closed Principle (easy to add new node types)

---

### Priority 4: Core Analyzer (C:98)

**File:** `src/app/core/analyzer.py`
**Current State:** 98 complexity, 196 hotspot score
**Risk:** HIGH

**Issues:**
- Still too complex despite being part of Phase 5 refactoring
- Handles orchestration + KPI aggregation + hierarchy building
- Nested functions increase complexity

**Recommended Actions:**
1. Extract KPI aggregation to dedicated module (already started in `app/kpi/`)
2. Simplify orchestration logic
3. Delegate more responsibilities to coordinator modules
4. Target: Reduce to <40 (pure orchestration)

**Alignment with ARCHITECTURE.md:**
- ✅ Orchestrator pattern (delegate, don't implement)
- ✅ Dependency Injection
- ✅ Single Responsibility

---

### Priority 5: Other High-Complexity Files

**Quick Wins:**
- `report/cli/cli_quick_wins_format.py` (C:111) - Similar issues to cli_report_format
- `report/cli/cli_summary_format.py` (C:85) - Extract dashboard components
- `languages/parsers/json_yaml.py` (C:94) - Split JSON and YAML parsing
- `app/metric_mancer_app.py` (C:50) - Further delegation to coordinators

---

## 🏗️ Architecture Guidelines (from ARCHITECTURE.md)

All refactoring must follow these established patterns:

### 1. SOLID Principles
- **S**ingle Responsibility: One class, one reason to change
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Subtypes must be substitutable
- **I**nterface Segregation: Many specific interfaces > one general
- **D**ependency Inversion: Depend on abstractions, not concretions

### 2. Design Patterns in Use
- **Configuration Object Pattern** (`AppConfig`) - centralized configuration
- **Factory Pattern** (`ReportGeneratorFactory`) - object creation
- **Strategy Pattern** (`ReportInterface`, `KPIStrategy`) - interchangeable algorithms
- **Builder Pattern** (`ReportDataCollector`) - complex object construction
- **Composite Pattern** (planned for tree structures)

### 3. Component Organization
```
src/
├── config/          # Configuration (AppConfig)
├── app/             # Application layer (domain-organized)
│   ├── core/        # Core business logic
│   ├── kpi/         # KPI calculation domain
│   ├── hierarchy/   # Data model domain
│   ├── coordination/# Workflow coordination
│   ├── scanning/    # File scanning
│   └── infrastructure/ # Cross-cutting concerns
├── kpis/            # KPI implementations (complexity, churn, etc.)
├── languages/       # Language parsers
├── report/          # Report generation
│   ├── cli/         # CLI formats
│   ├── html/        # HTML format
│   └── json/        # JSON format
├── analysis/        # Higher-level analysis (hotspots, review)
└── utilities/       # Utilities (git, paths, debug)
```

### 4. Dependency Flow Rules
- ✅ Unidirectional: main.py → app → kpis/languages/report
- ✅ No circular dependencies
- ✅ Inject dependencies via constructors
- ✅ Utilities can be used by any layer

---

## 🧪 Testing Requirements

All refactoring must maintain:

- ✅ **100% test pass rate** (currently 579 passing tests)
- ✅ **Zero breaking changes** (backward compatibility)
- ✅ **TDD approach** (write tests first)
- ✅ **Test coverage >80%** for new code

**Test Organization:**
```
tests/
├── analysis/        # Analysis layer tests
├── app/             # Application layer tests
│   ├── core/
│   ├── kpi/
│   └── hierarchy/
├── config/          # Configuration tests
├── kpis/            # KPI tests
├── report/          # Report generator tests
└── utilities/       # Utility tests
```

---

## 📈 Success Metrics

### Overall Code Health

| Metric | Before (Sept 2025) | Current (Oct 2025) | Target (Dec 2025) |
|--------|-------------------|-------------------|-------------------|
| **Highest File Complexity** | 90 (analyzer.py) | 190 (code_review_advisor.py) | <40 |
| **Files with C>50** | 1 | 9 | <3 |
| **Critical Hotspots** | 1 | 4 | 0 |
| **Test Pass Rate** | 100% | 100% | 100% |
| **Total Tests** | 445 | 579 | >600 |

### Refactoring Impact

**Phase 1-5 (Partially Complete):**
- ⚠️ `src/app/analyzer.py`: C:90 → C:0 (delegated to `src/app/core/analyzer.py` with C:98)
- ⚠️ **Net complexity reduction: -8%** (C:90 → C:98, complexity actually increased slightly)
- ✅ Modular architecture established (better structure, but complexity not yet reduced)
- ✅ Domain-based organization
- ✅ 134 new tests added

**Phase 6-8 (Planned):**
- 🎯 `code_review_advisor.py`: C:190 → C:<40
- 🎯 `git_cache.py`: C:142 → C:<30
- 🎯 `cli_report_format.py`: C:112 → C:<25

---

## 🚀 Implementation Strategy

### General Approach

1. **Red-Green-Refactor (TDD)**
   - 🔴 Write failing tests for new module
   - 🟢 Implement minimum to pass tests
   - 🔵 Refactor for clarity/performance

2. **Incremental Extraction**
   - Extract one responsibility at a time
   - Maintain all existing tests passing
   - Add tests for new modules

3. **Branch Strategy**
   - Feature branches: `{issue}-refactor-{module-name}`
   - Keep PRs small (<500 lines)
   - One priority at a time

4. **Code Review**
   - Follow `output/self-analysis/review_strategy_branch.md`
   - Minimum 2 reviewers for critical files
   - Architecture review for major changes

---

## 🎓 Lessons Learned from Phase 1-5

### What Worked Well ✅

1. **Domain-based organization** - Clear separation of concerns
2. **TDD approach** - High confidence in changes (100% pass rate)
3. **Incremental refactoring** - No breaking changes
4. **Strategy Pattern** - Easy to add new KPIs
5. **Factory Pattern** - Simplified report generation

### Challenges Encountered ⚠️

1. **Import path consistency** - Required fixing `utilities.debug` → `src.utilities.debug`
2. **F-string syntax errors** - Multi-line f-strings caused CI failures
3. **Complexity relocation vs. reduction** - Phase 1-5 moved complexity from `app/analyzer.py` (C:90) to `app/core/analyzer.py` (C:98), actually **increasing** total complexity by 8 points
4. **New complexity hotspots** - Refactoring exposed existing hotspots (code_review_advisor:190, git_cache:142) that were previously hidden
5. **Coordination overhead** - Multiple small modules require more orchestration logic

### Improvements for Phase 6-8 🎯

1. **Pre-commit hooks** - Catch syntax errors earlier
2. **Complexity budgets** - Max C:40 per file enforced in CI
3. **Architecture reviews** - Review design before implementing
4. **Documentation** - Keep ARCHITECTURE.md updated
5. **Measure actual reduction** - Track total complexity before/after, not just file-level metrics
6. **Extract, don't relocate** - Focus on eliminating complexity, not just moving it to new files

---

## 📚 References

- **ARCHITECTURE.md** - Design patterns and principles
- **CLAUDE.md** - Development guide for AI assistants
- **SoftwareSpecificationAndDesign.md** - Requirements and analysis framework
- **output/self-analysis/complexity_report.json** - Current complexity metrics
- **output/self-analysis/review_strategy_branch.md** - Code review guidelines

---

## 🎯 Next Actions

### Immediate (This Sprint)

1. ✅ Update this refactoring plan with current state
2. 🎯 Create GitHub issues for Priority 1-3 hotspots
3. 🎯 Design architecture for code_review_advisor refactoring
4. 🎯 Write TDD tests for extracted modules

### Short-term (Next 2 Weeks)

1. 🎯 Implement Priority 1: Refactor code_review_advisor.py
2. 🎯 Implement Priority 2: Refactor git_cache.py
3. 🎯 Review and merge Phase 5 changes to main

### Long-term (Next Month)

1. 🎯 Implement Priority 3: Refactor CLI report formats
2. 🎯 Implement Priority 4: Simplify core analyzer
3. 🎯 Add complexity budgets to CI/CD
4. 🎯 Update architectural documentation

---

**Status:** 📋 Active Development
**Phase:** 6 (New Hotspot Remediation)
**Last Refactoring:** Phase 5 (Domain-based organization) - Completed Oct 2025
**Next Milestone:** Reduce code_review_advisor.py complexity from 190 → <40

---

**Maintained by:** MetricMancer Team
**Contributors:** Thomas Lindqvist, Commander Prompt (Claude)
**Last Updated:** 2025-10-17
