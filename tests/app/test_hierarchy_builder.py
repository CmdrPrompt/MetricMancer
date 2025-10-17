"""
Tests for HierarchyBuilder - Directory hierarchy construction.

This test module verifies that the HierarchyBuilder correctly constructs
RepoInfo/ScanDir tree structures by placing File objects in the correct
directory nodes based on their file paths.
"""

import pytest
from pathlib import Path

from src.app.hierarchy.hierarchy_builder import HierarchyBuilder
from src.kpis.model import RepoInfo, ScanDir, File
from src.kpis.complexity import ComplexityKPI


def _create_test_repo_info(repo_name="test_repo", repo_root="/repo"):
    """Helper to create a properly initialized RepoInfo for tests."""
    return RepoInfo(
        dir_name=repo_name,
        scan_dir_path=".",
        repo_root_path=repo_root,
        repo_name=repo_name
    )


class TestHierarchyBuilderInitialization:
    """Test HierarchyBuilder initialization."""

    def test_initialization(self):
        """HierarchyBuilder should initialize without configuration."""
        builder = HierarchyBuilder()
        assert builder is not None
        assert isinstance(builder, HierarchyBuilder)


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
        """File in one subdirectory should return single path part."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "src/main.py",
            "/repo"
        )
        assert path_parts == ["src"]
        assert filename == "main.py"

    def test_nested_subdirectories(self):
        """File in nested subdirectories should return all path parts."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "src/app/utils/helpers.py",
            "/repo"
        )
        assert path_parts == ["src", "app", "utils"]
        assert filename == "helpers.py"

    def test_current_directory_notation(self):
        """Handle ./ notation in path (should filter out '.')."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "./src/main.py",
            "/repo"
        )
        assert path_parts == ["src"]
        assert filename == "main.py"
        assert "." not in path_parts

    def test_deep_nesting(self):
        """Handle deeply nested directory structures."""
        builder = HierarchyBuilder()
        path_parts, filename = builder._parse_directory_path(
            "a/b/c/d/e/f/file.py",
            "/repo"
        )
        assert path_parts == ["a", "b", "c", "d", "e", "f"]
        assert filename == "file.py"
        assert len(path_parts) == 6


class TestGetOrCreateScanDir:
    """Test ScanDir creation and navigation."""

    def test_create_single_level(self):
        """Create single ScanDir level."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()

        scan_dir = builder._get_or_create_scan_dir(
            repo_info,
            ["src"]
        )

        # Verify ScanDir was created in repo_info
        assert "src" in repo_info.scan_dirs
        assert scan_dir.dir_name == "src"
        assert scan_dir.scan_dir_path == "src"
        assert scan_dir.repo_name == "test_repo"
        assert scan_dir.repo_root_path == "/repo"

    def test_create_nested_levels(self):
        """Create nested ScanDir hierarchy."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()

        scan_dir = builder._get_or_create_scan_dir(
            repo_info,
            ["src", "app", "utils"]
        )

        # Verify full hierarchy was created
        assert "src" in repo_info.scan_dirs
        assert "app" in repo_info.scan_dirs["src"].scan_dirs
        assert "utils" in repo_info.scan_dirs["src"].scan_dirs["app"].scan_dirs

        # Verify final node properties
        assert scan_dir.dir_name == "utils"
        assert scan_dir.scan_dir_path == "src/app/utils"
        assert scan_dir.repo_name == "test_repo"

    def test_reuse_existing_scan_dir(self):
        """Don't recreate existing ScanDir nodes - reuse them."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()

        # First call creates hierarchy
        scan_dir1 = builder._get_or_create_scan_dir(
            repo_info,
            ["src", "app"]
        )

        # Second call should reuse existing nodes
        scan_dir2 = builder._get_or_create_scan_dir(
            repo_info,
            ["src", "app"]
        )

        # Should be the exact same object
        assert scan_dir1 is scan_dir2

        # Verify only one "src" directory exists
        assert len(repo_info.scan_dirs) == 1
        assert len(repo_info.scan_dirs["src"].scan_dirs) == 1

    def test_partial_path_reuse(self):
        """Reuse partial paths when creating deeper hierarchies."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()

        # Create src/app
        scan_dir1 = builder._get_or_create_scan_dir(repo_info, ["src", "app"])

        # Create src/app/utils (should reuse src/app)
        scan_dir2 = builder._get_or_create_scan_dir(repo_info, ["src", "app", "utils"])

        # Verify src and app were reused
        assert repo_info.scan_dirs["src"].scan_dirs["app"] is scan_dir1

        # Verify utils was created under app
        assert "utils" in scan_dir1.scan_dirs
        assert scan_dir2.dir_name == "utils"


class TestAddFileToHierarchy:
    """Test adding files to hierarchy."""

    def test_add_root_level_file(self):
        """Add file to root directory (no subdirectories)."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        file = File(
            name="main.py",
            file_path="main.py",
            kpis={},
            functions=[]
        )

        builder.add_file_to_hierarchy(repo_info, file)

        # File should be in repo_info.files (root level)
        assert "main.py" in repo_info.files
        assert repo_info.files["main.py"] is file

        # No subdirectories should be created
        assert len(repo_info.scan_dirs) == 0

    def test_add_file_to_subdirectory(self):
        """Add file to subdirectory (creates hierarchy if needed)."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        file = File(
            name="helpers.py",
            file_path="src/utils/helpers.py",
            kpis={},
            functions=[]
        )

        builder.add_file_to_hierarchy(repo_info, file)

        # Verify hierarchy was created
        assert "src" in repo_info.scan_dirs
        assert "utils" in repo_info.scan_dirs["src"].scan_dirs

        # Verify file placement
        utils_dir = repo_info.scan_dirs["src"].scan_dirs["utils"]
        assert "helpers.py" in utils_dir.files
        assert utils_dir.files["helpers.py"] is file

    def test_add_multiple_files_same_directory(self):
        """Add multiple files to the same directory."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        file1 = File(name="a.py", file_path="src/a.py", kpis={}, functions=[])
        file2 = File(name="b.py", file_path="src/b.py", kpis={}, functions=[])
        file3 = File(name="c.py", file_path="src/c.py", kpis={}, functions=[])

        builder.add_file_to_hierarchy(repo_info, file1)
        builder.add_file_to_hierarchy(repo_info, file2)
        builder.add_file_to_hierarchy(repo_info, file3)

        # All files should be in src directory
        src_dir = repo_info.scan_dirs["src"]
        assert "a.py" in src_dir.files
        assert "b.py" in src_dir.files
        assert "c.py" in src_dir.files
        assert len(src_dir.files) == 3

    def test_add_files_different_directories(self):
        """Add files to different directories at same level."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        file1 = File(name="main.py", file_path="src/main.py", kpis={}, functions=[])
        file2 = File(name="test.py", file_path="tests/test.py", kpis={}, functions=[])
        file3 = File(name="doc.md", file_path="docs/doc.md", kpis={}, functions=[])

        builder.add_file_to_hierarchy(repo_info, file1)
        builder.add_file_to_hierarchy(repo_info, file2)
        builder.add_file_to_hierarchy(repo_info, file3)

        # Verify separate directory trees
        assert "src" in repo_info.scan_dirs
        assert "tests" in repo_info.scan_dirs
        assert "docs" in repo_info.scan_dirs

        assert "main.py" in repo_info.scan_dirs["src"].files
        assert "test.py" in repo_info.scan_dirs["tests"].files
        assert "doc.md" in repo_info.scan_dirs["docs"].files

    def test_file_with_kpis_preserved(self):
        """File KPIs should be preserved when added to hierarchy."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        complexity_kpi = ComplexityKPI(value=15)
        file = File(
            name="main.py",
            file_path="src/main.py",
            kpis={"complexity": complexity_kpi},
            functions=[]
        )

        builder.add_file_to_hierarchy(repo_info, file)

        # Retrieve file and verify KPIs preserved
        placed_file = repo_info.scan_dirs["src"].files["main.py"]
        assert "complexity" in placed_file.kpis
        assert placed_file.kpis["complexity"] is complexity_kpi
        assert placed_file.kpis["complexity"].value == 15


class TestBuildHierarchy:
    """Test full hierarchy building from file lists."""

    def test_build_hierarchy_empty_list(self):
        """Build hierarchy with no files should return unchanged repo_info."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()

        result = builder.build_hierarchy(repo_info, [])

        # Should return same repo_info
        assert result is repo_info

        # No files or directories
        assert len(repo_info.files) == 0
        assert len(repo_info.scan_dirs) == 0

    def test_build_hierarchy_single_file(self):
        """Build hierarchy with single file."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        files = [
            File(name="main.py", file_path="src/main.py", kpis={}, functions=[])
        ]

        result = builder.build_hierarchy(repo_info, files)

        assert result is repo_info
        assert "src" in result.scan_dirs
        assert "main.py" in result.scan_dirs["src"].files

    def test_build_hierarchy_mixed_levels(self):
        """Build hierarchy with files at different directory levels."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
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
        """Hierarchy building should preserve all File object data."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        complexity_kpi = ComplexityKPI(value=42)
        file = File(
            name="main.py",
            file_path="src/main.py",
            kpis={"complexity": complexity_kpi},
            functions=[]  # Empty list for testing
        )

        result = builder.build_hierarchy(repo_info, [file])

        # Retrieve placed file
        placed_file = result.scan_dirs["src"].files["main.py"]

        # Verify all data preserved
        assert placed_file.name == "main.py"
        assert placed_file.file_path == "src/main.py"
        assert placed_file.kpis["complexity"] is complexity_kpi
        assert placed_file.kpis["complexity"].value == 42
        assert isinstance(placed_file.functions, list)

    def test_build_hierarchy_complex_structure(self):
        """Build complex multi-level directory structure."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        files = [
            # Root
            File(name="setup.py", file_path="setup.py", kpis={}, functions=[]),
            # src/
            File(name="__init__.py", file_path="src/__init__.py", kpis={}, functions=[]),
            File(name="main.py", file_path="src/main.py", kpis={}, functions=[]),
            # src/app/
            File(name="app.py", file_path="src/app/app.py", kpis={}, functions=[]),
            # src/app/utils/
            File(name="helpers.py", file_path="src/app/utils/helpers.py", kpis={}, functions=[]),
            # tests/
            File(name="test_main.py", file_path="tests/test_main.py", kpis={}, functions=[]),
            # tests/app/
            File(name="test_app.py", file_path="tests/app/test_app.py", kpis={}, functions=[]),
        ]

        result = builder.build_hierarchy(repo_info, files)

        # Root level
        assert "setup.py" in result.files

        # src/ structure
        assert "src" in result.scan_dirs
        assert "__init__.py" in result.scan_dirs["src"].files
        assert "main.py" in result.scan_dirs["src"].files

        # src/app/ structure
        assert "app" in result.scan_dirs["src"].scan_dirs
        assert "app.py" in result.scan_dirs["src"].scan_dirs["app"].files

        # src/app/utils/ structure
        assert "utils" in result.scan_dirs["src"].scan_dirs["app"].scan_dirs
        utils_dir = result.scan_dirs["src"].scan_dirs["app"].scan_dirs["utils"]
        assert "helpers.py" in utils_dir.files

        # tests/ structure
        assert "tests" in result.scan_dirs
        assert "test_main.py" in result.scan_dirs["tests"].files

        # tests/app/ structure
        assert "app" in result.scan_dirs["tests"].scan_dirs
        assert "test_app.py" in result.scan_dirs["tests"].scan_dirs["app"].files


class TestHierarchyBuilderEdgeCases:
    """Test edge cases and error conditions."""

    def test_duplicate_file_names_different_directories(self):
        """Same filename in different directories should work correctly."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        files = [
            File(name="__init__.py", file_path="src/__init__.py", kpis={}, functions=[]),
            File(name="__init__.py", file_path="tests/__init__.py", kpis={}, functions=[]),
            File(name="__init__.py", file_path="src/app/__init__.py", kpis={}, functions=[])
        ]

        result = builder.build_hierarchy(repo_info, files)

        # All three __init__.py files should exist in different locations
        assert "__init__.py" in result.scan_dirs["src"].files
        assert "__init__.py" in result.scan_dirs["tests"].files
        assert "__init__.py" in result.scan_dirs["src"].scan_dirs["app"].files

    def test_very_deep_nesting(self):
        """Handle very deeply nested directory structures."""
        builder = HierarchyBuilder()
        repo_info = _create_test_repo_info()
        deep_path = "a/b/c/d/e/f/g/h/i/j/file.py"
        file = File(
            name="file.py",
            file_path=deep_path,
            kpis={},
            functions=[]
        )

        result = builder.build_hierarchy(repo_info, [file])

        # Navigate through all levels
        current = result.scan_dirs["a"]
        for dir_name in ["b", "c", "d", "e", "f", "g", "h", "i", "j"]:
            assert dir_name in current.scan_dirs
            current = current.scan_dirs[dir_name]

        # File should be at the deepest level
        assert "file.py" in current.files
