# Feature: Delta-Based Review Time Estimation (Function-Level Analysis)

## 🎯 Overview

**Issue Type:** Feature Enhancement  
**Priority:** High  
**Estimated Effort:** 2-3 weeks  
**Target Version:** 3.2.0  
**Alignment:** Adam Tornhill's "Your Code as a Crime Scene" methodology

### Summary

Implement function-level delta analysis to provide precise review time estimates for code changes. Instead of analyzing entire files, focus on **only the functions that changed** between commits or branches, dramatically improving review efficiency and accuracy.

## 🔥 Problem Statement

### Current Limitations

1. **File-Level Granularity:** Current `--review-strategy-branch` analyzes entire files
   - Example: If 1 function changes in a 50-function file, we estimate reviewing all 50 functions
   - Result: Review time estimates are 60-80% inflated

2. **No Complexity Delta Tracking:** Can't see if changes increase or decrease complexity
   - Critical for identifying **complexity growth** (crime scene red flag)
   - Missing **refactoring impact** visibility

3. **Noisy Output:** Critical changes buried in lists of unchanged code
   - Reviewers waste time reading unchanged functions
   - Hard to prioritize high-risk changes

4. **No Historical Context:** Can't track complexity trends over time
   - Missing **temporal patterns** (core Crime Scene concept)
   - Can't identify **knowledge erosion** (ownership changes)

### User Impact

**Before Delta Analysis:**
```
Branch: feature/new-api
Files Changed: 59
Estimated Review Time: 36h 25m
Critical Files: 12
```
❌ Too broad - most code unchanged  
❌ Overwhelming for reviewers  
❌ Inaccurate time estimates  

**After Delta Analysis:**
```
Branch: feature/new-api
Functions Changed: 23 (of 847 total)
Estimated Review Time: 4h 15m (88% reduction)
Critical Changes: 5 functions with complexity increase
```
✅ Laser-focused on changes  
✅ Accurate estimates  
✅ Clear prioritization  

## 🎨 Proposed Solution

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  DeltaAnalyzer                           │
├─────────────────────────────────────────────────────────┤
│ + analyze_branch_delta(base, target) → DeltaDiff        │
│ + analyze_commit_range(from, to) → DeltaDiff            │
│ + analyze_working_tree() → DeltaDiff                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                 FunctionDiffParser                       │
├─────────────────────────────────────────────────────────┤
│ + parse_git_diff(diff_text) → List[FileChange]          │
│ + map_lines_to_functions(file, lines) → List[Function]  │
│ + calculate_complexity_delta(old, new) → int            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              DeltaReviewStrategyFormat                   │
├─────────────────────────────────────────────────────────┤
│ + format(delta_diff) → str                              │
│ + highlight_complexity_changes()                         │
│ + calculate_function_review_time()                      │
└─────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. DeltaDiff Data Model

```python
@dataclass
class FunctionChange:
    """Represents a single function change."""
    file_path: str
    function_name: str
    start_line: int
    end_line: int
    change_type: ChangeType  # ADDED, MODIFIED, DELETED
    complexity_before: Optional[int]
    complexity_after: Optional[int]
    complexity_delta: int
    churn: int  # Number of times this function has been modified
    hotspot_score: float  # complexity × churn
    last_author: str
    last_modified: datetime
    lines_changed: int
    review_time_minutes: int

@dataclass
class DeltaDiff:
    """Results of delta analysis."""
    base_commit: str
    target_commit: str
    added_functions: List[FunctionChange]
    modified_functions: List[FunctionChange]
    deleted_functions: List[FunctionChange]
    total_complexity_delta: int
    total_review_time_minutes: int
    critical_changes: List[FunctionChange]  # Top 10 by hotspot score
    refactorings: List[FunctionChange]  # Complexity decreased
```

#### 2. DeltaAnalyzer

```python
class DeltaAnalyzer:
    """Analyze complexity changes at function-level granularity."""
    
    def __init__(self, repo_path: str):
        self.repo = git.Repo(repo_path)
        self.parser = FunctionDiffParser()
        self.complexity_analyzer = ComplexityAnalyzer()
    
    def analyze_branch_delta(
        self, 
        base_branch: str = "main",
        target_branch: str = None  # None = current branch
    ) -> DeltaDiff:
        """
        Compare two branches at function level.
        
        Algorithm:
        1. Get git diff between branches
        2. Parse diff to identify changed files + line ranges
        3. For each changed file:
           a. Parse AST for both versions (base and target)
           b. Map changed lines to specific functions
           c. Calculate complexity for each function
           d. Compute complexity delta
        4. Calculate review time per function
        5. Rank by hotspot score (complexity × churn)
        """
        target = target_branch or self.repo.active_branch.name
        diff = self.repo.git.diff(f"{base_branch}...{target}", unified=0)
        
        changes = self._parse_diff_to_functions(diff, base_branch, target)
        delta = self._calculate_delta_metrics(changes)
        
        return delta
    
    def analyze_commit_range(
        self,
        from_commit: str,
        to_commit: str = "HEAD"
    ) -> DeltaDiff:
        """Analyze changes across commit range."""
        diff = self.repo.git.diff(f"{from_commit}..{to_commit}", unified=0)
        changes = self._parse_diff_to_functions(diff, from_commit, to_commit)
        return self._calculate_delta_metrics(changes)
    
    def analyze_working_tree(self) -> DeltaDiff:
        """Analyze uncommitted changes in working tree."""
        diff = self.repo.git.diff("HEAD", unified=0)
        unstaged = self.repo.git.diff(unified=0)
        
        all_changes = self._parse_diff_to_functions(
            diff + "\n" + unstaged, 
            "HEAD", 
            "working-tree"
        )
        return self._calculate_delta_metrics(all_changes)
```

#### 3. FunctionDiffParser

```python
class FunctionDiffParser:
    """Parse git diffs and map to function changes."""
    
    def parse_git_diff(self, diff_text: str) -> List[FileChange]:
        """
        Parse unified diff format to extract changed files and line ranges.
        
        Example diff:
        diff --git a/src/app/analyzer.py b/src/app/analyzer.py
        @@ -145,8 +145,15 @@ def analyze_file(self, path):
        +    if not path.exists():
        +        raise FileNotFoundError(path)
        """
        # Use unidiff library to parse diff
        # Returns list of (file_path, changed_line_ranges)
    
    def map_lines_to_functions(
        self,
        file_path: str,
        changed_lines: Set[int],
        base_version: str,
        target_version: str
    ) -> List[FunctionChange]:
        """
        Map changed line numbers to specific functions using AST.
        
        Steps:
        1. Parse both versions with AST
        2. Build function map: {line_range → function_def}
        3. For each changed line, find containing function
        4. Calculate complexity for affected functions in both versions
        5. Compute delta
        """
        base_ast = self._parse_version(file_path, base_version)
        target_ast = self._parse_version(file_path, target_version)
        
        base_functions = self._extract_functions(base_ast)
        target_functions = self._extract_functions(target_ast)
        
        changes = []
        for line in changed_lines:
            base_func = self._find_function_at_line(base_functions, line)
            target_func = self._find_function_at_line(target_functions, line)
            
            if base_func and target_func:
                change = self._create_function_change(
                    base_func, target_func, ChangeType.MODIFIED
                )
            elif target_func:
                change = self._create_function_change(
                    None, target_func, ChangeType.ADDED
                )
            else:
                change = self._create_function_change(
                    base_func, None, ChangeType.DELETED
                )
            
            changes.append(change)
        
        return changes
```

#### 4. DeltaReviewStrategyFormat

```python
class DeltaReviewStrategyFormat(ReportFormatStrategy):
    """Generate delta-focused review strategy reports."""
    
    def format(self, delta_diff: DeltaDiff, report_data: ReportData) -> str:
        """
        Generate markdown report highlighting function-level changes.
        
        Sections:
        1. Overview (total functions changed, complexity delta, time savings)
        2. Critical Changes (functions with highest hotspot scores)
        3. Complexity Increases (functions that got more complex)
        4. Refactorings (functions that got simpler)
        5. New Functions (added functions with high complexity)
        6. Ownership Changes (functions with new authors)
        """
        output = []
        
        # Header
        output.append(f"# Delta Review Strategy - {delta_diff.target_commit}")
        output.append("")
        
        # Overview
        output.extend(self._format_overview(delta_diff))
        
        # Critical Changes (Top 10 hotspots)
        output.extend(self._format_critical_changes(delta_diff))
        
        # Complexity Trends
        output.extend(self._format_complexity_trends(delta_diff))
        
        # Time Savings
        output.extend(self._format_time_comparison(delta_diff, report_data))
        
        return "\n".join(output)
    
    def _format_critical_changes(self, delta: DeltaDiff) -> List[str]:
        """Format critical function changes."""
        lines = ["## 🔥 Critical Changes (Complexity Hotspots)", ""]
        
        for change in delta.critical_changes[:10]:
            if change.complexity_delta > 0:
                icon = "🔴"
                risk = "CRITICAL"
            elif change.complexity_delta < 0:
                icon = "🟢"
                risk = "LOW (improved)"
            else:
                icon = "🟡"
                risk = "MODERATE"
            
            lines.append(f"### {change.file_path}")
            lines.append("")
            lines.append(f"#### {icon} {change.change_type.name}: `{change.function_name}()` "
                        f"(lines {change.start_line}-{change.end_line})")
            lines.append(f"- **Complexity Change**: {change.complexity_before} → "
                        f"{change.complexity_after} ({change.complexity_delta:+d}) {icon}")
            lines.append(f"- **Churn**: {change.churn} commits")
            lines.append(f"- **Hotspot Score**: {change.hotspot_score:.0f}")
            lines.append(f"- **Last Modified**: {change.last_modified} by {change.last_author}")
            lines.append(f"- **Review Time**: {change.review_time_minutes} minutes")
            lines.append(f"- **Risk**: {icon} {risk}")
            lines.append("")
            
            # Focus areas based on change type
            if change.complexity_delta > 5:
                lines.append("**Focus Areas:**")
                lines.append(f"- [ ] Review {change.complexity_delta} new branches added")
                lines.append("- [ ] Verify error handling for new edge cases")
                lines.append("- [ ] Check if function can be decomposed")
                lines.append("- [ ] Validate test coverage for new branches")
            elif change.complexity_delta < 0:
                lines.append("**Validation:**")
                lines.append("- [ ] Verify refactoring maintains behavior")
                lines.append("- [ ] Check test coverage still adequate")
            
            lines.append("")
        
        return lines
```

### CLI Integration

```bash
# Analyze current branch vs main
python -m src.main src --delta-review

# Analyze specific branch comparison
python -m src.main src --delta-review --base main --target feature/new-api

# Analyze commit range
python -m src.main src --delta-review --from abc123 --to HEAD

# Analyze uncommitted changes
python -m src.main src --delta-review --working-tree

# Combined with existing formats
python -m src.main src --output-formats delta-review,summary,html

# Delta-only mode (skip full analysis)
python -m src.main src --delta-only --base main
```

### Configuration

Add to `app_config.py`:

```python
@dataclass
class AppConfig:
    # ... existing fields ...
    
    # Delta analysis options
    enable_delta_analysis: bool = False
    delta_base_branch: str = "main"
    delta_target_branch: Optional[str] = None  # None = current branch
    delta_only_mode: bool = False  # Skip full analysis, only compute delta
    delta_min_complexity_change: int = 3  # Ignore small changes
    delta_show_refactorings: bool = True  # Show complexity improvements
```

## 📋 Implementation Plan

### Phase 1: Core Delta Analysis (Week 1)

**Goal:** Implement basic function-level diff parsing and complexity delta calculation.

**Tasks:**
1. ✅ Create `DeltaDiff` and `FunctionChange` data models
2. ✅ Implement `FunctionDiffParser.parse_git_diff()`
3. ✅ Implement `FunctionDiffParser.map_lines_to_functions()`
4. ✅ Add complexity calculation for function pairs
5. ✅ Write unit tests for diff parsing (30+ tests)
6. ✅ Integration test: compare known commits with expected function changes

**Dependencies:**
- `unidiff` library for parsing git diffs
- `gitpython` for git operations (already used)
- Existing `ComplexityAnalyzer` for calculating function complexity

**Acceptance Criteria:**
- [ ] Can parse git diff and identify changed files
- [ ] Can map changed lines to specific functions
- [ ] Can calculate complexity delta for modified functions
- [ ] 90%+ test coverage for new components
- [ ] Handles edge cases (deleted functions, moved code, renamed functions)

### Phase 2: DeltaAnalyzer Integration (Week 2)

**Goal:** Integrate delta analysis into existing review strategy workflow.

**Tasks:**
1. ✅ Implement `DeltaAnalyzer.analyze_branch_delta()`
2. ✅ Implement `DeltaAnalyzer.analyze_commit_range()`
3. ✅ Implement `DeltaAnalyzer.analyze_working_tree()`
4. ✅ Create `DeltaReviewStrategyFormat` output formatter
5. ✅ Add `--delta-review` CLI flag
6. ✅ Add `--delta-only` mode for fast delta-only analysis
7. ✅ Write integration tests with real git repositories
8. ✅ Performance optimization (cache AST parsing)

**Acceptance Criteria:**
- [ ] `--delta-review` generates function-level review strategy
- [ ] Output shows complexity delta for each function
- [ ] Review time estimates are function-based, not file-based
- [ ] Performance: < 5 seconds for typical branch (50 files, 200 functions)
- [ ] Works with all git workflows (branches, PRs, commits, working tree)

### Phase 3: Enhanced Features (Week 3)

**Goal:** Add advanced delta features and historical tracking.

**Tasks:**
1. ✅ Implement churn tracking (how many times function was modified)
2. ✅ Implement ownership change detection (author changes)
3. ✅ Add hotspot scoring (complexity × churn)
4. ✅ Implement refactoring detection (complexity decreases)
5. ✅ Add complexity trend visualization (ASCII charts)
6. ✅ Create `.metricmancer/history/` for storing historical data
7. ✅ Add `--compare-with-history` flag for trend analysis
8. ✅ Documentation and examples

**Acceptance Criteria:**
- [ ] Can track complexity trends over time
- [ ] Can identify knowledge erosion (ownership changes)
- [ ] Refactorings are highlighted separately
- [ ] Hotspot scores prioritize high-risk changes
- [ ] Documentation includes real-world examples
- [ ] Performance: < 10 seconds with historical comparison

## 🧪 Testing Strategy

### Unit Tests (50+ tests)

1. **FunctionDiffParser Tests:**
   - Parse simple git diff (single file, single function)
   - Parse complex diff (multiple files, multiple functions)
   - Handle edge cases (empty diffs, binary files, syntax errors)
   - Map lines to functions correctly
   - Handle deleted functions
   - Handle added functions
   - Handle renamed functions (heuristic matching)

2. **DeltaAnalyzer Tests:**
   - Analyze branch delta
   - Analyze commit range
   - Analyze working tree
   - Calculate complexity delta correctly
   - Handle merge commits
   - Handle cherry-picks

3. **DeltaReviewStrategyFormat Tests:**
   - Format overview section
   - Format critical changes section
   - Format complexity trends
   - Calculate time savings correctly
   - Highlight refactorings

### Integration Tests (20+ tests)

1. **Real Git Repository Tests:**
   - Create test repo with known changes
   - Verify function changes detected correctly
   - Verify complexity deltas match manual calculation
   - Test with multiple languages (Python, JavaScript)

2. **Performance Tests:**
   - Benchmark with large repositories (1000+ files)
   - Benchmark with large diffs (500+ changed functions)
   - Verify caching improves performance

### Manual Testing Checklist

- [ ] Test with MetricMancer's own repository
- [ ] Compare delta estimates with actual review times
- [ ] Verify output is readable and actionable
- [ ] Test with various git workflows (feature branches, hotfixes, releases)
- [ ] Test with edge cases (empty commits, large refactors, file moves)

## 📊 Success Metrics

### Quantitative

1. **Review Time Accuracy:**
   - Baseline (file-level): ±40% accuracy
   - Target (function-level): ±15% accuracy
   - Measure: Compare estimates with actual review times from team

2. **Scope Reduction:**
   - Target: 60-80% reduction in lines/functions to review
   - Measure: Compare full file analysis vs delta analysis

3. **Performance:**
   - Target: < 5 seconds for typical branch (50 files)
   - Target: < 10 seconds with historical comparison
   - Measure: Benchmark with real repositories

### Qualitative

1. **User Feedback:**
   - Survey: "Delta review is more actionable than file review" (>80% agree)
   - Survey: "Time estimates are accurate" (>70% agree)

2. **Adoption:**
   - Target: 50%+ of teams use `--delta-review` over `--review-strategy`
   - Measure: Telemetry (if enabled) or surveys

## 🚀 Crime Scene Methodology Alignment

| Principle | How Delta Analysis Implements It |
|-----------|----------------------------------|
| **Focus on Hotspots** | Only analyze changed functions, not entire codebase |
| **Temporal Patterns** | Track when functions change, by whom, and how often (churn) |
| **Change Coupling** | Foundation for detecting functions that change together |
| **Knowledge Loss** | Detect ownership changes in critical functions |
| **Complexity Growth** | Show complexity delta (increases = red flags) |
| **Prioritize by Risk** | Hotspot score = complexity × churn (highest risk first) |
| **Actionable Insights** | Function-level precision for targeted refactoring |

**Direct Book Quotes:**

> "The files that change most frequently are where the bugs hide."  
> → Delta analysis focuses on **changed functions** (most frequent changes)

> "Hotspots are the intersection of complexity and change frequency."  
> → Hotspot score = **complexity × churn**

> "Track who wrote the code to identify knowledge islands."  
> → Ownership change detection in **delta analysis**

## 📚 Dependencies

### New Libraries

```toml
[project]
dependencies = [
    # ... existing ...
    "unidiff>=0.7.5",  # Parse git diffs
]
```

### Existing Components

- ✅ `ComplexityAnalyzer` - Calculate function complexity
- ✅ `GitRepository` - Git operations (already used for churn)
- ✅ `ReportFormatStrategy` - Output formatting
- ✅ `AppConfig` - Configuration management

## 🔄 Backward Compatibility

- ✅ **Fully backward compatible** - new feature, existing functionality unchanged
- ✅ `--review-strategy` continues to work as file-level analysis
- ✅ `--delta-review` is opt-in, not default
- ✅ No breaking changes to existing APIs

## 📖 Documentation Updates

1. **README.md:**
   - Add delta analysis section
   - Show before/after comparison
   - Add usage examples

2. **ARCHITECTURE.md:**
   - Document delta analysis architecture
   - Show data flow diagrams

3. **CHANGELOG.md:**
   - Add v3.2.0 section with delta analysis feature

4. **New: docs/delta-analysis-guide.md:**
   - Comprehensive guide to delta analysis
   - Best practices for code review
   - Interpretation of hotspot scores

## 🎯 Acceptance Criteria

### Minimum Viable Product (MVP)

- [ ] Can analyze branch delta at function level
- [ ] Shows complexity change for each modified function
- [ ] Calculates review time per function (not per file)
- [ ] Generates markdown report with critical changes highlighted
- [ ] `--delta-review` CLI flag works
- [ ] 90%+ test coverage
- [ ] Performance: < 5 seconds for typical branch

### Nice-to-Have (Future Enhancements)

- [ ] Historical trend tracking
- [ ] Ownership change detection
- [ ] Refactoring recommendations
- [ ] Complexity trend visualization
- [ ] Integration with GitHub PR comments
- [ ] CI/CD integration (fail build if complexity increases too much)

## 🚦 Release Plan

1. **v3.2.0-alpha:** Core delta analysis (Phase 1 + 2)
2. **v3.2.0-beta:** Enhanced features (Phase 3)
3. **v3.2.0:** Stable release after user feedback

## 📝 Notes

- **Priority Justification:** This is the #1 priority because it directly implements Tornhill's core "crime scene" methodology - focusing on where changes happen, not the entire codebase.
- **Effort Estimate:** 2-3 weeks is realistic given existing infrastructure (git, AST parsing, complexity calculation already implemented).
- **Value Proposition:** 60-80% reduction in review scope + more accurate estimates = massive productivity gain for engineering teams.

## 🔗 Related Issues

- #53 - Multi-format generation (completed in v3.1.0) - provides foundation for delta format
- Future: #XX - Historical trend analysis (builds on delta analysis)
- Future: #XX - CI/CD integration (use delta analysis in pipelines)

---

**Created:** 2025-10-15  
**Status:** 📋 Planned for v3.2.0  
**Estimated Effort:** 2-3 weeks  
**Crime Scene Alignment:** ⭐⭐⭐⭐⭐ (15/15)
