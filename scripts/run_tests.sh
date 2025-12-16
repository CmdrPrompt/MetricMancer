#!/bin/bash
# Test runner script for MetricMancer
# This script runs all tests (both unittest and pytest style)

echo "🧪 Running MetricMancer Test Suite..."
echo ""

# Run pytest with verbose output
python -m pytest tests/ -v --tb=short

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All tests passed! 🎉"
else
    echo ""
    echo "❌ Some tests failed!"
    exit 1
fi