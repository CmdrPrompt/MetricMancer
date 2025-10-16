"""
FileReader - Handles file I/O operations with error handling.

This class follows the Single Responsibility Principle (SRP) by focusing
solely on reading file content with proper error handling and encoding support.

Part of the Analyzer refactoring to reduce complexity from 121 to manageable levels.
"""
from pathlib import Path
from typing import Optional

from src.utilities.debug import debug_print


class FileReader:
    """
    Handles file I/O operations with error handling.
    
    Responsibilities:
    - Read file content with UTF-8 encoding
    - Handle encoding errors gracefully (ignore invalid bytes)
    - Handle file system errors (missing files, permissions, etc.)
    - Return None on any error for clean error handling
    
    This class is designed for testability and follows SOLID principles.
    """
    
    def read_file(self, file_path: Path) -> Optional[str]:
        """
        Read file content with UTF-8 encoding and error handling.
        
        Args:
            file_path: Path object pointing to the file to read
            
        Returns:
            str: File content if successful
            None: If any error occurs (file not found, permission denied, etc.)
            
        Examples:
            >>> reader = FileReader()
            >>> content = reader.read_file(Path("script.py"))
            >>> if content is not None:
            ...     print(f"Read {len(content)} characters")
        """
        try:
            # Attempt to open and read the file with UTF-8 encoding
            # 'errors=ignore' ensures encoding errors don't crash the program
            with file_path.open('r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return content
            
        except FileNotFoundError:
            # File doesn't exist
            debug_print(f"[WARN] File not found: {file_path}")
            return None
            
        except PermissionError:
            # No permission to read the file
            debug_print(f"[WARN] Permission denied: {file_path}")
            return None
            
        except IsADirectoryError:
            # Path points to a directory, not a file
            debug_print(f"[WARN] Path is a directory: {file_path}")
            return None
            
        except OSError as e:
            # Other OS-level errors (disk full, network issues, etc.)
            debug_print(f"[WARN] OS error reading {file_path}: {e}")
            return None
            
        except Exception as e:
            # Catch-all for any other unexpected errors
            debug_print(f"[WARN] Unexpected error reading {file_path}: {e}")
            return None
