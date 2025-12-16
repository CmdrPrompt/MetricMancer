#!/usr/bin/env python3
"""
Code quality helper script for MetricMancer.

This script provides easy commands for formatting, linting, and testing code.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n{description}")
    print("=" * len(description))
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            text=True,
            executable='/bin/bash',
            cwd=Path(__file__).parent
        )
        print(f"✅ {description} - Success!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        return False


def format_code():
    """Auto-format code with autopep8."""
    return run_command(
        "source .venv/bin/activate && python -m autopep8 --in-place --recursive "
        "--max-line-length=120 src/ tests/",
        "🎨 Auto-formatting Python code"
    )


def lint_code():
    """Check code with flake8."""
    return run_command(
        "source .venv/bin/activate && python -m flake8 src/ tests/",
        "🔍 Linting Python code with flake8"
    )


def format_markdown():
    """Auto-format Markdown files with mdformat."""
    return run_command(
        "source .venv/bin/activate && python -m mdformat *.md docs/*.md docs/**/*.md --wrap 120",
        "📝 Auto-formatting Markdown files"
    )


def lint_markdown():
    """Check Markdown files with mdformat."""
    return run_command(
        "source .venv/bin/activate && python -m mdformat --check *.md docs/*.md docs/**/*.md --wrap 120",
        "🔍 Checking Markdown files"
    )


def check_markdown():
    """Run Markdown formatting and linting."""
    print("\n" + "=" * 50)
    print("Running Markdown quality checks")
    print("=" * 50)

    format_ok = format_markdown()
    lint_ok = lint_markdown()

    print("\n" + "=" * 50)
    if format_ok and lint_ok:
        print("✅ All Markdown checks passed!")
        print("=" * 50)
        return True
    else:
        print("❌ Some Markdown checks failed!")
        print("=" * 50)
        return False


def run_tests():
    """Run all tests with pytest."""
    return run_command(
        "source .venv/bin/activate && python -m pytest tests/ -v --tb=short",
        "🧪 Running tests with pytest"
    )


def check_licenses():
    """Check license compliance."""
    return run_command(
        "source .venv/bin/activate && python scripts/check_licenses.py",
        "📋 Checking license compliance"
    )


def check_all():
    """Run linting, tests, and license checks."""
    print("\n" + "=" * 50)
    print("Running all code quality checks")
    print("=" * 50)

    lint_ok = lint_code()
    test_ok = run_tests()
    licenses_ok = check_licenses()

    print("\n" + "=" * 50)
    if lint_ok and test_ok and licenses_ok:
        print("✅ All checks passed!")
        print("=" * 50)
        return True
    else:
        print("❌ Some checks failed!")
        print("=" * 50)
        return False


def clean():
    """Clean temporary files."""
    commands = [
        'find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true',
        'find . -type f -name "*.pyc" -delete',
        'find . -type f -name "*.pyo" -delete',
        'find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true',
        'rm -rf .pytest_cache build dist'
    ]

    print("\n🧹 Cleaning temporary files...")
    for cmd in commands:
        subprocess.run(cmd, shell=True, check=False)
    print("✅ Cleanup complete!")


def analyze_quick():
    """Run quick wins analysis on MetricMancer itself."""
    print("\n🎯 Running quick wins analysis on MetricMancer codebase...")
    print("   (Identifies low-effort, high-impact improvements)")
    return run_command(
        "source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ "
        "--output-format quick-wins --report-folder output/self-analysis "
        "--churn-period 90 --threshold-high 15",
        "Quick wins analysis"
    )


def analyze_summary():
    """Run summary analysis on MetricMancer itself."""
    print("\n📊 Running summary analysis on MetricMancer codebase...")
    print("   (High-level overview of code quality metrics)")
    return run_command(
        "source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ "
        "--output-format summary --report-folder output/self-analysis "
        "--churn-period 90 --threshold-high 15",
        "Summary analysis"
    )


def analyze_review():
    """Run code review analysis on MetricMancer itself."""
    print("\n🔍 Running code review analysis on MetricMancer codebase...")
    print("   (Generates actionable code review recommendations for full repo)")
    return run_command(
        "source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ "
        "--output-formats review-strategy --report-folder output/self-analysis "
        "--churn-period 90 --threshold-high 15",
        "Code review analysis"
    )


def analyze_review_branch():
    """Run code review analysis on changed files only (current branch)."""
    print("\n🔍 Running code review analysis on CHANGED files only...")
    print("   (Analyzes only files modified in current branch vs main)")
    # Get current branch name
    try:
        import subprocess
        result = subprocess.run(['git', 'branch', '--show-current'],
                                capture_output=True, text=True, check=True)
        branch_name = result.stdout.strip()
        print(f"   Current branch: {branch_name}")
    except Exception:
        pass

    return run_command(
        "source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ tests/ "
        "--output-formats review-strategy-branch --report-folder output/self-analysis "
        "--churn-period 90 --threshold-high 15 --review-branch-only --review-base-branch main",
        "Branch code review analysis"
    )


def analyze_full():
    """Run complete analysis on MetricMancer itself."""
    print("\n🚀 Running complete analysis on MetricMancer codebase...")
    print("   (Generates all reports: HTML, JSON, CLI, Quick-wins, Code Review)")
    return run_command(
        "source .venv/bin/activate && PYTHONPATH=. python src/main.py src/ "
        "--output-formats html,json,summary,quick-wins --report-folder output/self-analysis "
        "--churn-period 90 --threshold-high 15 --include-review-tab",
        "Complete analysis"
    )


def show_help():
    """Show help message."""
    print("""
MetricMancer Code Quality Tools
================================

Usage: python code_quality.py <command>

Code Quality Commands:
  format          - Auto-format Python code with autopep8
  lint            - Check Python code with flake8
  format-md       - Auto-format Markdown files with mdformat
  lint-md         - Check Markdown files with mdformat
  check-md        - Run format-md + lint-md (Markdown workflow)
  test            - Run all tests with pytest
  licenses        - Check license compliance
  check           - Run lint + test + licenses (CI workflow)
  clean           - Clean temporary files

Self-Analysis Commands (run MetricMancer on itself):
  analyze-quick         - Quick wins analysis for immediate improvements
  analyze-summary       - Summary report with key metrics
  analyze-review        - Code review recommendations (full repo)
  analyze-review-branch - Code review for changed files only (current branch)
  analyze-full          - Complete analysis with all reports

General:
  help            - Show this help message

Examples:
  python code_quality.py format
  python code_quality.py check
  python code_quality.py format-md
  python code_quality.py check-md
  python code_quality.py analyze-quick
    """)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    commands = {
        'format': format_code,
        'lint': lint_code,
        'format-md': format_markdown,
        'lint-md': lint_markdown,
        'check-md': check_markdown,
        'test': run_tests,
        'licenses': check_licenses,
        'check': check_all,
        'clean': clean,
        'analyze-quick': analyze_quick,
        'analyze-summary': analyze_summary,
        'analyze-review': analyze_review,
        'analyze-review-branch': analyze_review_branch,
        'analyze-full': analyze_full,
        'help': show_help,
    }

    if command not in commands:
        print(f"❌ Unknown command: {command}")
        show_help()
        sys.exit(1)

    success = commands[command]()

    # Exit with appropriate code for check command
    if command == 'check' and not success:
        sys.exit(1)


if __name__ == '__main__':
    main()
