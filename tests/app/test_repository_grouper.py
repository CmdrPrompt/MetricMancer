"""
Unit tests for RepositoryGrouper class.

Following TDD (Test-Driven Development):
- RED: Write failing tests first
- GREEN: Implement minimal code to pass tests
- REFACTOR: Improve code quality
"""
import pytest

# Import will fail initially (RED phase)
from src.app.repository_grouper import RepositoryGrouper


class TestRepositoryGrouper:
    """Test suite for RepositoryGrouper class."""
    
    def test_repository_grouper_can_be_instantiated(self):
        """Test that RepositoryGrouper can be created."""
        grouper = RepositoryGrouper()
        assert grouper is not None
    
    def test_group_empty_list(self):
        """Test grouping an empty list of files."""
        grouper = RepositoryGrouper()
        files_by_root, scan_dirs_by_root = grouper.group_by_repository([])
        
        assert files_by_root == {}
        assert scan_dirs_by_root == {}
    
    def test_group_single_file_single_repo(self):
        """Test grouping a single file in a single repository."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/repo/src/file1.py', 'root': '/repo'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        assert len(files_by_root) == 1
        assert '/repo' in files_by_root
        assert len(files_by_root['/repo']) == 1
        assert files_by_root['/repo'][0] == files[0]
        
        assert len(scan_dirs_by_root) == 1
        assert '/repo' in scan_dirs_by_root
        assert '/repo' in scan_dirs_by_root['/repo']
    
    def test_group_multiple_files_single_repo(self):
        """Test grouping multiple files in the same repository."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/repo/src/file1.py', 'root': '/repo'},
            {'path': '/repo/src/file2.py', 'root': '/repo'},
            {'path': '/repo/tests/test1.py', 'root': '/repo'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        assert len(files_by_root) == 1
        assert '/repo' in files_by_root
        assert len(files_by_root['/repo']) == 3
        assert files_by_root['/repo'] == files
    
    def test_group_files_multiple_repos(self):
        """Test grouping files across multiple repositories."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/repo1/src/file1.py', 'root': '/repo1'},
            {'path': '/repo1/src/file2.py', 'root': '/repo1'},
            {'path': '/repo2/src/file3.py', 'root': '/repo2'},
            {'path': '/repo2/src/file4.py', 'root': '/repo2'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        assert len(files_by_root) == 2
        assert '/repo1' in files_by_root
        assert '/repo2' in files_by_root
        assert len(files_by_root['/repo1']) == 2
        assert len(files_by_root['/repo2']) == 2
    
    def test_group_handles_missing_root(self):
        """Test that files without 'root' key default to empty string."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/somewhere/file1.py'},  # No 'root' key
            {'path': '/somewhere/file2.py', 'root': ''}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        assert '' in files_by_root
        assert len(files_by_root['']) == 2
    
    def test_scan_dirs_includes_repo_root(self):
        """Test that scan_dirs includes the repository root."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/repo/src/file1.py', 'root': '/repo'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        assert '/repo' in scan_dirs_by_root
        assert isinstance(scan_dirs_by_root['/repo'], set)
        assert '/repo' in scan_dirs_by_root['/repo']
    
    def test_scan_dirs_uses_set_to_avoid_duplicates(self):
        """Test that scan_dirs uses a set to avoid duplicates."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/repo/src/file1.py', 'root': '/repo'},
            {'path': '/repo/src/file2.py', 'root': '/repo'},
            {'path': '/repo/tests/file3.py', 'root': '/repo'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        # Even with 3 files, scan_dirs should only have one entry (the root)
        assert len(scan_dirs_by_root['/repo']) == 1
        assert '/repo' in scan_dirs_by_root['/repo']
    
    def test_group_preserves_file_order_within_repo(self):
        """Test that files are preserved in their original order."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/repo/c.py', 'root': '/repo'},
            {'path': '/repo/a.py', 'root': '/repo'},
            {'path': '/repo/b.py', 'root': '/repo'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        # Should maintain insertion order
        assert files_by_root['/repo'][0]['path'] == '/repo/c.py'
        assert files_by_root['/repo'][1]['path'] == '/repo/a.py'
        assert files_by_root['/repo'][2]['path'] == '/repo/b.py'
    
    def test_group_with_different_repo_path_formats(self):
        """Test grouping with various repository path formats."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/abs/path/repo1/file.py', 'root': '/abs/path/repo1'},
            {'path': 'relative/repo2/file.py', 'root': 'relative/repo2'},
            {'path': '/c:/windows/repo3/file.py', 'root': '/c:/windows/repo3'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        assert len(files_by_root) == 3
        assert '/abs/path/repo1' in files_by_root
        assert 'relative/repo2' in files_by_root
        assert '/c:/windows/repo3' in files_by_root
    
    def test_group_returns_defaultdict_behavior(self):
        """Test that result behaves like expected dictionary."""
        grouper = RepositoryGrouper()
        files = [
            {'path': '/repo/file.py', 'root': '/repo'}
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        # Should be dict or dict-like
        assert isinstance(files_by_root, dict)
        assert isinstance(scan_dirs_by_root, dict)
    
    def test_group_with_additional_file_metadata(self):
        """Test that grouping preserves additional file metadata."""
        grouper = RepositoryGrouper()
        files = [
            {
                'path': '/repo/file.py',
                'root': '/repo',
                'ext': '.py',
                'size': 1024,
                'modified': '2025-10-16'
            }
        ]
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        grouped_file = files_by_root['/repo'][0]
        assert grouped_file['ext'] == '.py'
        assert grouped_file['size'] == 1024
        assert grouped_file['modified'] == '2025-10-16'
    
    def test_group_large_number_of_files(self):
        """Test grouping a large number of files."""
        grouper = RepositoryGrouper()
        
        # Create 1000 files across 10 repos
        files = []
        for repo_num in range(10):
            repo_root = f'/repo{repo_num}'
            for file_num in range(100):
                files.append({
                    'path': f'{repo_root}/file{file_num}.py',
                    'root': repo_root
                })
        
        files_by_root, scan_dirs_by_root = grouper.group_by_repository(files)
        
        assert len(files_by_root) == 10
        for repo_num in range(10):
            repo_root = f'/repo{repo_num}'
            assert len(files_by_root[repo_root]) == 100
