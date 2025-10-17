"""Core analysis modules.

This module contains the main analysis engine components:
- Analyzer: Main analysis coordinator
- FileProcessor: File-level processing (Phase 5 extraction)
"""

from src.app.core.analyzer import Analyzer
from src.app.core.file_processor import FileProcessor

__all__ = ['Analyzer', 'FileProcessor']
