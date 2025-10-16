"""
Unit tests for FileReader class.

Following TDD (Test-Driven Development):
- RED: Write failing tests first
- GREEN: Implement minimal code to pass tests
- REFACTOR: Improve code quality
"""
import pytest
from pathlib import Path
import tempfile
import os

# Import will fail initially (RED phase)
from src.app.file_reader import FileReader


class TestFileReader:
    """Test suite for FileReader class."""
    
    def test_file_reader_can_be_instantiated(self):
        """Test that FileReader can be created."""
        reader = FileReader()
        assert reader is not None
    
    def test_read_valid_utf8_file(self):
        """Test reading a valid UTF-8 file returns content."""
        # Arrange: Create a temporary file with UTF-8 content
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                        delete=False, suffix='.txt') as f:
            test_content = "Hello, World!\nThis is a test file.\nWith UTF-8: åäö"
            f.write(test_content)
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert
            assert content is not None
            assert content == test_content
            assert "UTF-8: åäö" in content
        finally:
            # Cleanup
            os.unlink(temp_path)
    
    def test_read_nonexistent_file_returns_none(self):
        """Test reading a non-existent file returns None."""
        # Arrange
        nonexistent_path = Path("/tmp/this_file_does_not_exist_12345.txt")
        
        # Act
        reader = FileReader()
        content = reader.read_file(nonexistent_path)
        
        # Assert
        assert content is None
    
    def test_read_file_with_permission_error_returns_none(self):
        """Test reading a file without permissions returns None."""
        # Arrange: Create file and remove read permissions
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("secret content")
            temp_path = Path(f.name)
        
        try:
            # Remove all permissions
            os.chmod(temp_path, 0o000)
            
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert
            assert content is None
        finally:
            # Cleanup: restore permissions and delete
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)
    
    def test_read_file_with_encoding_errors_uses_ignore(self):
        """Test that encoding errors are ignored gracefully."""
        # Arrange: Create file with binary content
        with tempfile.NamedTemporaryFile(mode='wb', delete=False) as f:
            # Write some valid UTF-8 and some invalid bytes
            f.write(b"Valid text\n\xff\xfe\nMore text")
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert: Should not be None, should handle errors
            assert content is not None
            assert "Valid text" in content
            assert "More text" in content
        finally:
            # Cleanup
            os.unlink(temp_path)
    
    def test_read_empty_file_returns_empty_string(self):
        """Test reading an empty file returns empty string."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert
            assert content is not None
            assert content == ""
        finally:
            # Cleanup
            os.unlink(temp_path)
    
    def test_read_file_with_unicode_characters(self):
        """Test reading file with various Unicode characters."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                        delete=False) as f:
            unicode_content = "Emoji: 🎉 Chinese: 你好 Arabic: مرحبا"
            f.write(unicode_content)
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert
            assert content is not None
            assert "🎉" in content
            assert "你好" in content
            assert "مرحبا" in content
        finally:
            # Cleanup
            os.unlink(temp_path)
    
    def test_read_python_file_with_code(self):
        """Test reading a Python file with actual code."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                        delete=False, suffix='.py') as f:
            python_code = '''def hello_world():
    """A simple function."""
    print("Hello, World!")
    return 42
'''
            f.write(python_code)
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert
            assert content is not None
            assert "def hello_world():" in content
            assert "return 42" in content
        finally:
            # Cleanup
            os.unlink(temp_path)
    
    def test_read_file_accepts_path_object(self):
        """Test that read_file accepts Path objects."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert
            assert isinstance(temp_path, Path)
            assert content == "test content"
        finally:
            # Cleanup
            os.unlink(temp_path)
    
    def test_read_file_handles_directory_path(self):
        """Test that passing a directory path returns None."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            dir_path = Path(tmpdir)
            
            # Act
            reader = FileReader()
            content = reader.read_file(dir_path)
            
            # Assert
            assert content is None
    
    def test_multiple_reads_same_file(self):
        """Test that same file can be read multiple times."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("persistent content")
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content1 = reader.read_file(temp_path)
            content2 = reader.read_file(temp_path)
            
            # Assert
            assert content1 == content2
            assert content1 == "persistent content"
        finally:
            # Cleanup
            os.unlink(temp_path)
    
    def test_read_large_file(self):
        """Test reading a reasonably large file."""
        # Arrange: Create a file with 1000 lines
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', 
                                        delete=False) as f:
            for i in range(1000):
                f.write(f"Line {i}: Some content here\n")
            temp_path = Path(f.name)
        
        try:
            # Act
            reader = FileReader()
            content = reader.read_file(temp_path)
            
            # Assert
            assert content is not None
            assert content.count('\n') == 1000
            assert "Line 0:" in content
            assert "Line 999:" in content
        finally:
            # Cleanup
            os.unlink(temp_path)
