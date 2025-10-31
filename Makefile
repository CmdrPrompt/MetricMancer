# Code Quality Makefile for MetricMancer

SHELL := /bin/bash

.PHONY: help install format lint test coverage licenses serve check clean analyze-quick analyze-summary analyze-review analyze-review-branch analyze-delta-review analyze-full

help:
	@echo "MetricMancer Code Quality Tools"
	@echo "================================"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make install              - Install all dependencies in venv"
	@echo ""
	@echo "Code Quality Commands:"
	@echo "  make format               - Auto-format code with autopep8"
	@echo "  make lint                 - Check code with flake8"
	@echo "  make test                 - Run all tests with pytest"
	@echo "  make coverage             - Run tests with coverage report (HTML + terminal)"
	@echo "  make licenses             - Check license compliance"
	@echo "  make serve                - Start Python HTTP server for testing web pages"
	@echo "  make check                - Run lint + test + licenses (CI workflow)"
	@echo "  make clean                - Clean temporary files"
	@echo ""
	@echo "Self-Analysis Commands (run MetricMancer on itself):"
	@echo "  make analyze-quick        - Quick wins analysis for immediate improvements"
	@echo "  make analyze-summary      - Summary report with key metrics"
	@echo "  make analyze-review       - Code review recommendations (full repo)"
	@echo "  make analyze-review-branch- Code review for changed files only (current branch)"
	@echo "  make analyze-delta-review - Delta review for function-level changes (current branch)"
	@echo "  make analyze-full         - Complete analysis with all reports"
	@echo ""

install:
	@echo "📦 Installing MetricMancer dependencies..."
	@if [ ! -d ".venv" ]; then \
		echo "❌ Error: Virtual environment .venv not found!"; \
		echo "   Create it first with: python -m venv .venv"; \
		exit 1; \
	fi
	@echo "   Upgrading pip..."
	@source .venv/bin/activate && python -m pip install --upgrade pip
	@echo "   Installing package in editable mode with all dependencies..."
	@source .venv/bin/activate && pip install -e .
	@echo ""
	@echo "   Verifying dependency integrity..."
	@source .venv/bin/activate && pip check
	@echo ""
	@echo "✅ Installation complete!"
	@echo ""
	@echo "📋 Critical packages installed:"
	@source .venv/bin/activate && pip list | grep -iE "(jinja2|pytest|pydriller|tqdm|pyyaml|autopep8|flake8|pip-licenses|coverage|unidiff|tree-sitter|language-pack)"

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

coverage:
	@echo "📊 Running tests with coverage analysis..."
	@source .venv/bin/activate && python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo ""
	@echo "✅ Coverage analysis complete!"
	@echo "   HTML Report: htmlcov/index.html"
	@echo "   Open with:   open htmlcov/index.html"

licenses:
	@echo "📋 Checking license compliance..."
	@source .venv/bin/activate && python check_licenses.py
	@echo "✅ License check complete!"

serve:
	@echo "🌐 Starting Python HTTP server for testing generated web pages..."
	@echo "   Server will be available at: http://localhost:8080"
	@echo "   Serving files from: $(shell pwd)"
	@echo "   Press Ctrl+C to stop the server"
	@echo ""
	@source .venv/bin/activate && python -m http.server 8080
	@echo "✅ Server stopped!"

check: lint test licenses
	@echo "✅ All checks passed!"

clean:
	@echo "🧹 Cleaning temporary files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .pytest_cache build dist htmlcov coverage_html .coverage coverage.xml
	# Remove all files in output/ except .gitkeep
	@if [ -d output ]; then find output -mindepth 1 -not -name ".gitkeep" -delete; fi
	@echo "✅ Cleanup complete!"

# Self-analysis targets - run MetricMancer on itself for code quality insights
analyze-quick:
	@echo "🎯 Running quick wins analysis on MetricMancer codebase..."
	@echo "   (Identifies low-effort, high-impact improvements)"
	@source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ \
		--output-formats quick-wins \
		--report-folder output/self-analysis \
		--churn-period 7 \
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
	@echo "   View: output/self-analysis/review_strategy.md"

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

analyze-delta-review:
	@echo "🔬 Running delta review analysis on FUNCTION-LEVEL changes..."
	@echo "   (Shows exactly which functions changed, with complexity deltas)"
	@CURRENT_BRANCH=$$(git branch --show-current); \
	echo "   Current branch: $$CURRENT_BRANCH"; \
	echo "   Comparing against: main"; \
	source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ \
		--delta-review \
		--delta-base-branch main \
		--delta-output delta_review.md \
		--report-folder output/self-analysis
	@echo ""
	@echo "✅ Delta review report generated!"
	@echo "   View: output/self-analysis/delta_review.md"

analyze-full:
	@echo "🚀 Running complete analysis on MetricMancer codebase..."
	@echo "   (Generates comprehensive HTML report with tabbed interface + JSON + CLI)"
	@source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ \
		--output-formats html,json,summary \
		--report-folder output/self-analysis \
		--report-filename metricmancer_analysis.html \
		--churn-period 10 \
		--threshold-high 15 \
		--include-review-tab
	@echo ""
	@echo "📦 Complete analysis generated!"
	@echo "   📊 HTML Report: output/self-analysis/metricmancer_analysis.html"
	@echo "      - Overview tab with repository statistics"
	@echo "      - File Tree tab with complexity metrics (C, Cog, Churn, Hotspot)"
	@echo "      - Quick Wins tab for actionable improvements"
	@echo "      - Code Review tab with intelligent review recommendations"
	@echo "   📄 JSON Report: output/self-analysis/report.json"
	@echo "   📋 Summary:     View CLI output above"
	@echo ""
	@echo "💡 Open HTML report in browser:"
	@echo "   open output/self-analysis/metricmancer_analysis.html"

