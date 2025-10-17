# Code Quality Makefile for MetricMancer

SHELL := /bin/bash

.PHONY: help format lint test licenses check clean analyze-quick analyze-summary analyze-review analyze-review-branch analyze-full

help:
	@echo "MetricMancer Code Quality Tools"
	@echo "================================"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  make format               - Auto-format code with autopep8"
	@echo "  make lint                 - Check code with flake8"
	@echo "  make test                 - Run all tests with pytest"
	@echo "  make licenses             - Check license compliance"
	@echo "  make check                - Run lint + test + licenses (CI workflow)"
	@echo "  make clean                - Clean temporary files"
	@echo ""
	@echo "Self-Analysis Commands (run MetricMancer on itself):"
	@echo "  make analyze-quick        - Quick wins analysis for immediate improvements"
	@echo "  make analyze-summary      - Summary report with key metrics"
	@echo "  make analyze-review       - Code review recommendations (full repo)"
	@echo "  make analyze-review-branch- Code review for changed files only (current branch)"
	@echo "  make analyze-full         - Complete analysis with all reports"
	@echo ""

format:
	@echo "🎨 Auto-formatting Python code with autopep8..."
	@source .venv/bin/activate && python -m autopep8 --in-place --recursive --max-line-length=120 src/ tests/
	@echo "✅ Formatting complete!"

lint:
	@echo "🔍 Checking code with flake8..."
	@source .venv/bin/activate && python -m flake8 src/ tests/
	@echo "✅ Linting complete!"

test:
	@echo "🧪 Running tests with pytest..."
	@source .venv/bin/activate && python -m pytest tests/ -v --tb=short
	@echo "✅ Tests complete!"

licenses:
	@echo "📋 Checking license compliance..."
	@source .venv/bin/activate && python check_licenses.py
	@echo "✅ License check complete!"

check: lint test licenses
	@echo "✅ All checks passed!"

clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache build dist
	@echo "✅ Cleanup complete!"

# Self-analysis targets - run MetricMancer on itself for code quality insights
analyze-quick:
	@echo "🎯 Running quick wins analysis on MetricMancer codebase..."
	@echo "   (Identifies low-effort, high-impact improvements)"
	@source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ \
		--quick-wins \
		--report-folder output/self-analysis \
		--churn-period 90 \
		--threshold-high 15
	@echo ""
	@echo "📊 Quick wins report generated!"
	@echo "   View: output/self-analysis/quick_wins_report.md"

analyze-summary:
	@echo "📊 Running summary analysis on MetricMancer codebase..."
	@echo "   (High-level overview of code quality metrics)"
	@source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ \
		--summary \
		--report-folder output/self-analysis \
		--churn-period 90 \
		--threshold-high 15
	@echo ""
	@echo "📈 Summary report generated!"
	@echo "   View CLI output above for key metrics"

analyze-review:
	@echo "🔍 Running code review analysis on MetricMancer codebase..."
	@echo "   (Generates actionable code review recommendations for full repo)"
	@source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ \
		--output-formats review-strategy \
		--report-folder output/self-analysis \
		--churn-period 90 \
		--threshold-high 15
	@echo ""
	@echo "✅ Code review recommendations generated!"
	@echo "   View: output/self-analysis/code_review_recommendations.md"

analyze-review-branch:
	@echo "🔍 Running code review analysis on CHANGED files only..."
	@echo "   (Analyzes only files modified in current branch vs main)"
	@CURRENT_BRANCH=$$(git branch --show-current); \
	echo "   Current branch: $$CURRENT_BRANCH"; \
	source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ tests/ \
		--output-formats review-strategy-branch \
		--report-folder output/self-analysis \
		--churn-period 90 \
		--threshold-high 15 \
		--review-branch-only \
		--review-base-branch main
	@echo ""
	@echo "✅ Branch-specific code review recommendations generated!"
	@echo "   View: output/self-analysis/review_strategy_branch.md"

analyze-full:
	@echo "🚀 Running complete analysis on MetricMancer codebase..."
	@echo "   (Generates all reports: HTML, JSON, CLI)"
	@source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ \
		--output-formats html,json,summary \
		--report-folder output/self-analysis \
		--churn-period 90 \
		--threshold-high 15
	@echo ""
	@echo "📦 Complete analysis generated!"
	@echo "   HTML Report: output/self-analysis/index.html"
	@echo "   JSON Report: output/self-analysis/report.json"
	@echo "   Summary:     View CLI output above"

