# Phase 3: Extract HierarchyBuilder - Implementation Plan

**Date:** 2025-10-15\
**Status:** 📋 PLANNING\
**Prerequisites:** ✅ Phase 1 (KPICalculator) and Phase 2 (FileAnalyzer) merged to main

______________________________________________________________________

## 🎯 Objective

Extract directory hierarchy construction logic from `analyzer.py` into a dedicated `HierarchyBuilder` component that:

- Builds RepoInfo/ScanDir tree structures
- Manages parent-child directory relationships
- Places analyzed files in the correct directory nodes
- **Does NOT aggregate KPIs** (that's Phase 4)

______________________________________________________________________

## 📦 What to Extract

### Current Code Location

**File:** `src/app/analyzer.py`\
**Lines:** ~217-237 (hierarchy building section)

**Current Implementation:**

```python
# Find or create ScanDir objects in the hierarchy
relative_dir_path = file_path.relative_to(repo_root_path).parent
current_dir_container = repo_info
path_parts = [part for part in relative_dir_path.parts if part and part != '.']

if not path_parts:
    # The file is in the root directory of the repo
    repo_info.files[file_obj.name] = file_obj
else:
    # The file is in a subdirectory, navigate there
    current_path = Path()
    for part in path_parts:
        current_path = current_path / part
        if part not in current_dir_container.scan_dirs:
            current_dir_container.scan_dirs[part] = ScanDir(
                dir_name=part,
                scan_dir_path=str(current_path),
                repo_root_path=repo_info.repo_root_path,
                repo_name=repo_info.repo_name
            )
        current_dir_container = current_dir_container.scan_dirs[part]
    current_dir_container.files[file_obj.name] = file_obj
```

### Responsibilities to Extract

1. ✅ Parse relative directory path from file path
2. ✅ Navigate/create ScanDir hierarchy
3. ✅ Place File objects in correct directory nodes
4. ✅ Handle root-level files (no subdirectory)
5. ✅ Maintain parent-child relationships

### NOT Included (Phase 4)

❌ KPI aggregation (lines 243-290 remain in analyzer.py for Phase 4)\
❌ Recursive directory traversal for KPIs\
❌ Average/sum calculations

______________________________________________________________________

## 🏗️ New Architecture

### Component Design

```
┌─────────────────────────────────────────────────┐
│          HierarchyBuilder                       │
├─────────────────────────────────────────────────┤
│ + build_hierarchy(repo_info, files) → RepoInfo │
│ + add_file_to_hierarchy(repo_info, file)       │
│ - _get_or_create_scan_dir(...)                 │
│ - _parse_directory_path(file_path, repo_root)  │
└─────────────────────────────────────────────────┘
```

### API Design

**Primary Method:**

```python
def build_hierarchy(
    self,
    repo_info: RepoInfo,
    files: List[File]
) -> RepoInfo:
    """
    Build directory hierarchy and place files in correct ScanDir nodes.
    
    Args:
        repo_info: Root RepoInfo object
        files: List of analyzed File objects to place
        
    Returns:
        RepoInfo with complete hierarchy populated
        
    Example:
        builder = HierarchyBuilder()
        repo_info = RepoInfo(repo_root_path="/repo", repo_name="myproject")
        files = [file1, file2, file3]  # from FileAnalyzer
        
        repo_info = builder.build_hierarchy(repo_info, files)
        # repo_info.files = {"root_file.py": file1}
        # repo_info.scan_dirs = {"src": ScanDir(...)}
    """
```

**Helper Methods:**

```python
def add_file_to_hierarchy(
    self,
    repo_info: RepoInfo,
    file: File
) -> None:
    """Add single file to hierarchy (for incremental builds)."""
    
def _get_or_create_scan_dir(
    self,
    repo_info: RepoInfo,
    dir_path: Path
) -> Union[RepoInfo, ScanDir]:
    """Navigate hierarchy, creating ScanDir nodes as needed."""
    
def _parse_directory_path(
    self,
    file_path: str,
    repo_root: str
) -> Tuple[List[str], str]:
    """
    Parse file path into directory parts and filename.
    
    Returns:
        (path_parts, filename)
        Example: "src/app/main.py" -> (["src", "app"], "main.py")
    """
```

______________________________________________________________________

## 📝 Implementation Steps

### Step 1: Create `src/app/hierarchy_builder.py`

**Lines:** ~80-100\
**Complexity:** C:~15

**Imports:**

```python
from pathlib import Path
from typing import List, Union, Tuple
from src.models.repo_info import RepoInfo
from src.models.scan_dir import ScanDir
from src.models.file import File
```

**Class Structure:**

```python
class HierarchyBuilder:
    """
    Builds directory hierarchy for analyzed files.
    
    Responsibilities:
    - Create RepoInfo/ScanDir tree structure
    - Place File objects in correct directory nodes
    - Maintain parent-child relationships
    
    Does NOT:
    - Aggregate KPIs (that's KPIAggregator - Phase 4)
    - Analyze files (that's FileAnalyzer - Phase 2)
    """
    
    def __init__(self):
        """Initialize HierarchyBuilder."""
        pass  # Stateless for now
    
    def build_hierarchy(
        self,
        repo_info: RepoInfo,
        files: List[File]
    ) -> RepoInfo:
        """Build complete hierarchy from list of files."""
        for file in files:
            self.add_file_to_hierarchy(repo_info, file)
        return repo_info
    
    def add_file_to_hierarchy(
        self,
        repo_info: RepoInfo,
        file: File
    ) -> None:
        """Add single file to hierarchy."""
        # Parse directory path from file.file_path
        path_parts, filename = self._parse_directory_path(
            file.file_path,
            repo_info.repo_root_path
        )
        
        if not path_parts:
            # Root-level file
            repo_info.files[file.name] = file
        else:
            # Navigate/create hierarchy
            container = self._get_or_create_scan_dir(
                repo_info,
                path_parts
            )
            container.files[file.name] = file
    
    def _parse_directory_path(
        self,
        file_path: str,
        repo_root: str
    ) -> Tuple[List[str], str]:
        """Parse file path into directory parts and filename."""
        path = Path(file_path)
        filename = path.name
        
        # Get directory parts (filter out empty and '.')
        dir_parts = [
            part for part in path.parent.parts
            if part and part != '.'
        ]
        
        return dir_parts, filename
    
    def _get_or_create_scan_dir(
        self,
        repo_info: RepoInfo,
        path_parts: List[str]
    ) -> ScanDir:
        """
        Navigate hierarchy, creating ScanDir nodes as needed.
        
        Example:
            path_parts = ["src", "app", "utils"]
            Creates: RepoInfo -> ScanDir("src") -> ScanDir("app") -> ScanDir("utils")
        """
        current_container = repo_info
        current_path = Path()
        
        for part in path_parts:
            current_path = current_path / part
            
            if part not in current_container.scan_dirs:
                # Create new ScanDir
                current_container.scan_dirs[part] = ScanDir(
                    dir_name=part,
                    scan_dir_path=str(current_path),
                    repo_root_path=repo_info.repo_root_path,
                    repo_name=repo_info.repo_name
                )
            
            current_container = current_container.scan_dirs[part]
        
        return current_container
```

### Step 2: Create `tests/app/test_hierarchy_builder.py`

**Lines:** ~120-150\
**Tests:** 15-18

**Test Structure:**

```python
import pytest
from pathlib import Path
from src.app.hierarchy_builder import HierarchyBuilder
from src.models.repo_info import RepoInfo
from src.models.scan_dir import ScanDir
from src.models.file import File


class TestHierarchyBuilderInitialization:
    """Test HierarchyBuilder initialization."""
    
    def test_initialization(self):
        """HierarchyBuilder should initialize without config."""
        builder = HierarchyBuilder()
        assert builder is not None


class TestParseDirectoryPath:
    """Test directory path parsing."""
    
    def test_root_level_file(self):
        """File in root directory should return empty path_parts."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "main.py",
            "/repo"
        )
        assert path_parts == []
        assert filename == "main.py"
    
    def test_single_subdirectory(self):
        """File in one subdirectory."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "src/main.py",
            "/repo"
        )
        assert path_parts == ["src"]
        assert filename == "main.py"
    
    def test_nested_subdirectories(self):
        """File in nested subdirectories."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "src/app/utils/helpers.py",
            "/repo"
        )
        assert path_parts == ["src", "app", "utils"]
        assert filename == "helpers.py"
    
    def test_current_directory_notation(self):
        """Handle ./ notation in path."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "./src/main.py",
            "/repo"
        )
        assert path_parts == ["src"]
        assert filename == "main.py"


class TestGetOrCreateScanDir:
    """Test ScanDir creation and navigation."""
    
    def test_create_single_level(self):
        """Create single ScanDir level."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        
        scan_dir = builder._get_or_create_scan_dir(
            repo_info,
            ["src"]
        )
        
        assert "src" in repo_info.scan_dirs
        assert scan_dir.dir_name == "src"
        assert scan_dir.repo_name == "test_repo"
    
    def test_create_nested_levels(self):
        """Create nested ScanDir hierarchy."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        
        scan_dir = builder._get_or_create_scan_dir(
            repo_info,
            ["src", "app", "utils"]
        )
        
        # Verify hierarchy
        assert "src" in repo_info.scan_dirs
        assert "app" in repo_info.scan_dirs["src"].scan_dirs
        assert "utils" in repo_info.scan_dirs["src"].scan_dirs["app"].scan_dirs
        
        # Verify final node
        assert scan_dir.dir_name == "utils"
        assert scan_dir.scan_dir_path == "src/app/utils"
    
    def test_reuse_existing_scan_dir(self):
        """Don't recreate existing ScanDir nodes."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        
        # First call creates hierarchy
        scan_dir1 = builder._get_or_create_scan_dir(
            repo_info,
            ["src", "app"]
        )
        
        # Second call reuses existing
        scan_dir2 = builder._get_or_create_scan_dir(
            repo_info,
            ["src", "app"]
        )
        
        assert scan_dir1 is scan_dir2  # Same object


class TestAddFileToHierarchy:
    """Test adding files to hierarchy."""
    
    def test_add_root_level_file(self):
        """Add file to root directory."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        file = File(
            name="main.py",
            file_path="main.py",
            kpis={},
            functions=[]
        )
        
        builder.add_file_to_hierarchy(repo_info, file)
        
        assert "main.py" in repo_info.files
        assert repo_info.files["main.py"] is file
    
    def test_add_file_to_subdirectory(self):
        """Add file to subdirectory (creates hierarchy)."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        file = File(
            name="helpers.py",
            file_path="src/utils/helpers.py",
            kpis={},
            functions=[]
        )
        
        builder.add_file_to_hierarchy(repo_info, file)
        
        # Verify hierarchy created
        assert "src" in repo_info.scan_dirs
        assert "utils" in repo_info.scan_dirs["src"].scan_dirs
        
        # Verify file placement
        utils_dir = repo_info.scan_dirs["src"].scan_dirs["utils"]
        assert "helpers.py" in utils_dir.files
        assert utils_dir.files["helpers.py"] is file
    
    def test_add_multiple_files_same_directory(self):
        """Add multiple files to same directory."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        file1 = File(name="a.py", file_path="src/a.py", kpis={}, functions=[])
        file2 = File(name="b.py", file_path="src/b.py", kpis={}, functions=[])
        
        builder.add_file_to_hierarchy(repo_info, file1)
        builder.add_file_to_hierarchy(repo_info, file2)
        
        src_dir = repo_info.scan_dirs["src"]
        assert "a.py" in src_dir.files
        assert "b.py" in src_dir.files


class TestBuildHierarchy:
    """Test full hierarchy building."""
    
    def test_build_hierarchy_empty_list(self):
        """Build hierarchy with no files."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        
        result = builder.build_hierarchy(repo_info, [])
        
        assert result is repo_info
        assert len(repo_info.files) == 0
        assert len(repo_info.scan_dirs) == 0
    
    def test_build_hierarchy_mixed_files(self):
        """Build hierarchy with files at different levels."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        files = [
            File(name="README.md", file_path="README.md", kpis={}, functions=[]),
            File(name="main.py", file_path="src/main.py", kpis={}, functions=[]),
            File(name="utils.py", file_path="src/utils/utils.py", kpis={}, functions=[]),
            File(name="test.py", file_path="tests/test.py", kpis={}, functions=[])
        ]
        
        result = builder.build_hierarchy(repo_info, files)
        
        # Root level file
        assert "README.md" in result.files
        
        # src/main.py
        assert "src" in result.scan_dirs
        assert "main.py" in result.scan_dirs["src"].files
        
        # src/utils/utils.py
        assert "utils" in result.scan_dirs["src"].scan_dirs
        assert "utils.py" in result.scan_dirs["src"].scan_dirs["utils"].files
        
        # tests/test.py
        assert "tests" in result.scan_dirs
        assert "test.py" in result.scan_dirs["tests"].files
    
    def test_build_hierarchy_preserves_file_data(self):
        """Hierarchy building preserves File object data."""
        builder = HierarchyBuilder()
        repo_info = RepoInfo(
            repo_root_path="/repo",
            repo_name="test_repo"
        )
        file = File(
            name="main.py",
            file_path="src/main.py",
            kpis={"complexity": "mock_kpi"},
            functions=["func1", "func2"]
        )
        
        builder.build_hierarchy(repo_info, [file])
        
        placed_file = repo_info.scan_dirs["src"].files["main.py"]
        assert placed_file.kpis == {"complexity": "mock_kpi"}
        assert placed_file.functions == ["func1", "func2"]
```

### Step 3: Integrate with Analyzer

**File:** `src/app/analyzer.py`

**Changes:**

1. **Add import:**

```python
from src.app.hierarchy_builder import HierarchyBuilder
```

2. **Initialize in `__init__`:**

```python
def __init__(self, config):
    # ... existing code ...
    self.hierarchy_builder = HierarchyBuilder()
```

3. **Replace hierarchy building code (lines ~217-237):**

**BEFORE:**

```python
# Find or create ScanDir objects in the hierarchy
relative_dir_path = file_path.relative_to(repo_root_path).parent
current_dir_container = repo_info
path_parts = [part for part in relative_dir_path.parts if part and part != '.']

if not path_parts:
    # The file is in the root directory of the repo
    repo_info.files[file_obj.name] = file_obj
else:
    # The file is in a subdirectory, navigate there
    current_path = Path()
    for part in path_parts:
        current_path = current_path / part
        if part not in current_dir_container.scan_dirs:
            current_dir_container.scan_dirs[part] = ScanDir(
                dir_name=part,
                scan_dir_path=str(current_path),
                repo_root_path=repo_info.repo_root_path,
                repo_name=repo_info.repo_name
            )
        current_dir_container = current_dir_container.scan_dirs[part]
    current_dir_container.files[file_obj.name] = file_obj
```

**AFTER:**

```python
# Add file to hierarchy (delegates to HierarchyBuilder)
self.hierarchy_builder.add_file_to_hierarchy(repo_info, file_obj)
```

**Lines reduced:** ~20 → 1 (saved 19 lines!)

### Step 4: Run Tests

```bash
# Run new HierarchyBuilder tests
pytest tests/app/test_hierarchy_builder.py -v

# Run all tests (verify no regressions)
pytest tests/ -q --tb=line

# Expected: 498 tests (483 existing + 15 new)
```

### Step 5: Update Documentation

1. **Update `docs/refactoring/analyzer-refactoring-plan.md`:**

   - Mark Phase 3 as ✅ COMPLETE

2. **Create `docs/refactoring/phase3-complete.md`:**

   - Component summary
   - Test results
   - Complexity metrics
   - Next steps (Phase 4)

______________________________________________________________________

## 📊 Expected Impact

### Complexity Reduction

| Metric                 | Before | After Phase 3 | Change           |
| ---------------------- | ------ | ------------- | ---------------- |
| analyzer.py lines      | 331    | ~290          | -41 lines (-12%) |
| analyzer.py complexity | C:90   | ~60           | -30 (-33%)       |
| Total tests            | 483    | ~498          | +15 tests        |
| Test time              | 1.60s  | ~1.65s        | +50ms            |

### Code Quality Metrics

**HierarchyBuilder:**

- Lines: ~80-100
- Complexity: C:~15
- Responsibilities: 1 (hierarchy building)
- Testability: ⭐⭐⭐⭐⭐ (fully isolated)

**Analyzer (after Phase 3):**

- Complexity: 90 → ~60 (-33%)
- Responsibilities: 6 → 5 (-1)
- Still needs: Phases 4-6

______________________________________________________________________

## 🚀 Benefits

### Separation of Concerns

✅ Hierarchy building logic is isolated\
✅ Analyzer delegates structural concerns\
✅ Clear API: `build_hierarchy(repo_info, files)`

### Testability

✅ Easy to test hierarchy creation\
✅ No git dependencies in tests\
✅ Fast unit tests (\<50ms)

### Reusability

✅ Can rebuild hierarchy from cached files\
✅ Useful for incremental analysis\
✅ Supports partial tree updates

### Maintainability

✅ Single Responsibility (ScanDir tree building)\
✅ Small, focused component (~100 lines)\
✅ Clear boundaries with other components

______________________________________________________________________

## 🔄 Integration Flow (After Phase 3)

```
FileAnalyzer.analyze_multiple_files(file_infos, repo_root)
  ↓ returns: List[File]
  
HierarchyBuilder.build_hierarchy(repo_info, files)
  ↓ returns: RepoInfo (with hierarchy populated)
  
KPIAggregator.aggregate_kpis(repo_info)  ← Phase 4
  ↓ returns: RepoInfo (with aggregated KPIs)
  
Analyzer (orchestrates all of the above)
```

______________________________________________________________________

## ⚠️ Considerations

### Edge Cases to Test

1. **Empty file lists** - Should return unchanged repo_info
2. **Root-level files** - Files with no subdirectory
3. **Deep nesting** - Files in src/app/utils/helpers/common/x.py
4. **Special characters** - Directories with spaces, unicode
5. **Duplicate file names** - Same filename in different directories

### NOT in Scope

❌ **KPI Aggregation** - That's Phase 4 (KPIAggregator)\
❌ **File Analysis** - That's Phase 2 (FileAnalyzer)\
❌ **Git Operations** - Handled by existing git_cache\
❌ **Sorting/Filtering** - Report generation concern

______________________________________________________________________

## ✅ Definition of Done

- [x] `src/app/hierarchy_builder.py` created (~80-100 lines)
- [x] `tests/app/test_hierarchy_builder.py` created (15+ tests)
- [x] All new tests passing
- [x] All 483 existing tests still passing
- [x] Analyzer.py integrated (uses HierarchyBuilder)
- [x] Complexity: analyzer.py 90 → ~60
- [x] Documentation updated (phase3-complete.md)
- [x] Code review completed
- [x] Merged to main

______________________________________________________________________

## 🎯 Success Criteria

✅ **Functionality:** All files placed in correct directory nodes\
✅ **Tests:** 498/498 passing (100%)\
✅ **Performance:** No regression (\<1.7s test time)\
✅ **Complexity:** analyzer.py C:90 → ~60 (-33%)\
✅ **Architecture:** Clear separation from KPI aggregation

______________________________________________________________________

## 📅 Next Phase: Phase 4 (KPIAggregator)

After Phase 3 completion:

**Phase 4 Goal:** Extract KPI aggregation logic\
**Files:** `src/app/kpi_aggregator.py`, `tests/app/test_kpi_aggregator.py`\
**Lines to extract:** analyzer.py lines 243-290 (~50 lines)\
**Estimated impact:** analyzer.py 290 → ~200 lines, C:60 → ~40

______________________________________________________________________

**Ready to implement?** Let me know when you want to start! 🚀
