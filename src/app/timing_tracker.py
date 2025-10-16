"""
TimingTracker - Tracks execution time for different operations.

This class follows the Single Responsibility Principle (SRP) by focusing
solely on timing measurements. It separates timing concerns from business logic,
making code cleaner and more testable.

Part of the Analyzer refactoring to reduce complexity from 121 to manageable levels.
"""
from contextlib import contextmanager
import time
from typing import Dict


class TimingTracker:
    """
    Tracks execution time for different operations.
    
    Responsibilities:
    - Maintain timing information for various operations
    - Provide context manager for easy timing
    - Accumulate time across multiple calls to same operation
    - Return copy of timings to prevent external modifications
    
    This class separates timing concerns from business logic,
    following the Single Responsibility Principle.
    
    Example:
        >>> tracker = TimingTracker()
        >>> with tracker.track('complexity'):
        ...     # Do some work
        ...     analyze_complexity()
        >>> timings = tracker.get_timings()
        >>> print(f"Complexity took {timings['complexity']:.2f}s")
    """
    
    def __init__(self):
        """
        Initialize TimingTracker with default operations.
        
        Default operations tracked:
        - cache_prebuild: Git cache pre-building
        - complexity: Complexity analysis
        - filechurn: File churn calculation
        - hotspot: Hotspot analysis
        - ownership: Code ownership calculation
        - sharedownership: Shared ownership calculation
        """
        self.timings: Dict[str, float] = {
            'cache_prebuild': 0.0,
            'complexity': 0.0,
            'filechurn': 0.0,
            'hotspot': 0.0,
            'ownership': 0.0,
            'sharedownership': 0.0
        }
    
    @contextmanager
    def track(self, operation: str):
        """
        Context manager for timing operations.
        
        Automatically measures elapsed time and adds it to the
        specified operation's total. Works even if an exception occurs.
        
        Args:
            operation: Name of the operation to track
            
        Yields:
            None
            
        Example:
            >>> tracker = TimingTracker()
            >>> with tracker.track('complexity'):
            ...     time.sleep(0.1)
            >>> assert tracker.timings['complexity'] >= 0.1
        """
        start = time.perf_counter()
        try:
            yield
        finally:
            # Always record time, even if exception occurred
            elapsed = time.perf_counter() - start
            
            # Initialize operation if it doesn't exist
            if operation not in self.timings:
                self.timings[operation] = 0.0
            
            # Accumulate time
            self.timings[operation] += elapsed
    
    def get_timings(self) -> Dict[str, float]:
        """
        Return copy of timing dictionary.
        
        Returns a copy to prevent external code from modifying
        the internal timing state.
        
        Returns:
            dict: Copy of timing information with operation names as keys
                  and elapsed time in seconds as values
                  
        Example:
            >>> tracker = TimingTracker()
            >>> with tracker.track('test'):
            ...     pass
            >>> timings = tracker.get_timings()
            >>> timings['test'] = 999  # Modifying copy
            >>> tracker.get_timings()['test']  # Original unchanged
            0.0...
        """
        return self.timings.copy()
    
    def reset(self):
        """
        Reset all timings to zero.
        
        Useful for re-using the same tracker instance across
        multiple analysis runs.
        
        Example:
            >>> tracker = TimingTracker()
            >>> with tracker.track('test'):
            ...     pass
            >>> tracker.reset()
            >>> tracker.get_timings()['test']
            0.0
        """
        for key in self.timings:
            self.timings[key] = 0.0
