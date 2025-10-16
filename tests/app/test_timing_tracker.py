"""
Unit tests for TimingTracker class.

Following TDD (Test-Driven Development):
- RED: Write failing tests first
- GREEN: Implement minimal code to pass tests
- REFACTOR: Improve code quality
"""
import pytest
import time

# Import will fail initially (RED phase)
from src.app.timing_tracker import TimingTracker


class TestTimingTracker:
    """Test suite for TimingTracker class."""
    
    def test_timing_tracker_can_be_instantiated(self):
        """Test that TimingTracker can be created."""
        tracker = TimingTracker()
        assert tracker is not None
    
    def test_initial_timings_are_zero(self):
        """Test that all timing values start at zero."""
        tracker = TimingTracker()
        timings = tracker.get_timings()
        
        assert 'cache_prebuild' in timings
        assert 'complexity' in timings
        assert 'filechurn' in timings
        assert 'hotspot' in timings
        assert 'ownership' in timings
        assert 'sharedownership' in timings
        
        # All should be zero initially
        for key, value in timings.items():
            assert value == 0.0, f"{key} should be 0.0, got {value}"
    
    def test_track_context_manager_measures_time(self):
        """Test that track() context manager measures elapsed time."""
        tracker = TimingTracker()
        
        # Track a simple operation
        with tracker.track('complexity'):
            time.sleep(0.05)  # Sleep for 50ms
        
        timings = tracker.get_timings()
        assert timings['complexity'] >= 0.04  # Allow some tolerance
        assert timings['complexity'] < 0.2    # But not too much
    
    def test_track_accumulates_time_across_calls(self):
        """Test that multiple track() calls accumulate time."""
        tracker = TimingTracker()
        
        # First operation
        with tracker.track('complexity'):
            time.sleep(0.02)
        
        # Second operation
        with tracker.track('complexity'):
            time.sleep(0.02)
        
        timings = tracker.get_timings()
        # Should be approximately 0.04 seconds total
        assert timings['complexity'] >= 0.03
        assert timings['complexity'] < 0.1
    
    def test_track_different_operations_independently(self):
        """Test that different operations are tracked independently."""
        tracker = TimingTracker()
        
        with tracker.track('complexity'):
            time.sleep(0.02)
        
        with tracker.track('churn'):
            time.sleep(0.03)
        
        timings = tracker.get_timings()
        assert timings['complexity'] >= 0.01
        assert timings['complexity'] < 0.1
        assert timings['churn'] >= 0.02
        assert timings['churn'] < 0.1
    
    def test_get_timings_returns_copy(self):
        """Test that get_timings() returns a copy, not reference."""
        tracker = TimingTracker()
        
        with tracker.track('complexity'):
            time.sleep(0.01)
        
        timings1 = tracker.get_timings()
        timings1['complexity'] = 999.0  # Modify the copy
        
        timings2 = tracker.get_timings()
        # Original should be unchanged
        assert timings2['complexity'] < 10.0
        assert timings2['complexity'] != 999.0
    
    def test_track_handles_exceptions_gracefully(self):
        """Test that track() still records time even if exception occurs."""
        tracker = TimingTracker()
        
        try:
            with tracker.track('complexity'):
                time.sleep(0.01)
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected
        
        timings = tracker.get_timings()
        # Time should still be recorded
        assert timings['complexity'] >= 0.005
    
    def test_track_with_custom_operation_name(self):
        """Test tracking with a custom operation name."""
        tracker = TimingTracker()
        
        # Add a custom operation
        tracker.timings['custom_operation'] = 0.0
        
        with tracker.track('custom_operation'):
            time.sleep(0.01)
        
        timings = tracker.get_timings()
        assert 'custom_operation' in timings
        assert timings['custom_operation'] >= 0.005
    
    def test_track_zero_time_operation(self):
        """Test tracking an operation that takes negligible time."""
        tracker = TimingTracker()
        
        with tracker.track('complexity'):
            pass  # Do nothing
        
        timings = tracker.get_timings()
        # Should be very close to zero but not necessarily exact
        assert timings['complexity'] >= 0.0
        assert timings['complexity'] < 0.01
    
    def test_multiple_concurrent_operations(self):
        """Test tracking multiple operations in sequence."""
        tracker = TimingTracker()
        
        operations = ['complexity', 'filechurn', 'hotspot', 'ownership']
        
        for op in operations:
            with tracker.track(op):
                time.sleep(0.01)
        
        timings = tracker.get_timings()
        for op in operations:
            assert timings[op] >= 0.005
    
    def test_track_nested_operations_not_supported(self):
        """Test that nested tracking works but tracks independently."""
        tracker = TimingTracker()
        
        with tracker.track('complexity'):
            time.sleep(0.01)
            with tracker.track('filechurn'):
                time.sleep(0.01)
        
        timings = tracker.get_timings()
        # Both should have time recorded
        assert timings['complexity'] >= 0.01
        assert timings['filechurn'] >= 0.005
    
    def test_timing_precision(self):
        """Test that timing has reasonable precision."""
        tracker = TimingTracker()
        
        with tracker.track('complexity'):
            time.sleep(0.1)  # 100ms
        
        timings = tracker.get_timings()
        # Should be between 95ms and 150ms (allowing system variance)
        assert 0.09 <= timings['complexity'] <= 0.15
    
    def test_reset_functionality_if_implemented(self):
        """Test reset functionality if implemented."""
        tracker = TimingTracker()
        
        with tracker.track('complexity'):
            time.sleep(0.01)
        
        # If reset method exists
        if hasattr(tracker, 'reset'):
            tracker.reset()
            timings = tracker.get_timings()
            assert timings['complexity'] == 0.0
    
    def test_get_timing_for_specific_operation(self):
        """Test getting timing for a specific operation."""
        tracker = TimingTracker()
        
        with tracker.track('complexity'):
            time.sleep(0.02)
        
        with tracker.track('churn'):
            time.sleep(0.01)
        
        timings = tracker.get_timings()
        # Verify we can access specific timings
        assert timings['complexity'] > timings['churn']
