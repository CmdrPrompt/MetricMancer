# PyPI Publishing Guide for MetricMancer

This document provides a comprehensive guide for publishing MetricMancer to the Python Package Index (PyPI).

## Table of Contents

01. [What is PyPI?](#what-is-pypi)
02. [Prerequisites](#prerequisites)
03. [Pre-Publishing Checklist](#pre-publishing-checklist)
04. [Required Code Changes](#required-code-changes)
05. [PyPI Account Setup](#pypi-account-setup)
06. [Building the Package](#building-the-package)
07. [Testing on TestPyPI](#testing-on-testpypi)
08. [Publishing to PyPI](#publishing-to-pypi)
09. [Post-Publishing](#post-publishing)
10. [Troubleshooting](#troubleshooting)

______________________________________________________________________

## What is PyPI?

**PyPI (Python Package Index)** is the official package repository for Python, similar to npm for JavaScript or Maven
for Java.

### Benefits of Publishing to PyPI

**For Users:**

- ✅ Simple installation: `pip install metricmancer` instead of cloning the repo
- ✅ Automatic dependency management
- ✅ Version pinning: `pip install metricmancer==3.2.0`
- ✅ Integration with virtual environments and requirements.txt
- ✅ Works with all standard Python tooling (poetry, pipenv, etc.)

**For the Project:**

- ✅ Increased visibility and discoverability
- ✅ Professional image and credibility
- ✅ ~500,000+ packages, millions of daily downloads
- ✅ Integration with tools like GitHub Dependabot
- ✅ Easier for CI/CD pipelines to install

### Comparison

**Without PyPI (current):**

```bash
git clone https://github.com/CmdrPrompt/MetricMancer
cd MetricMancer
pip install -r requirements.txt
python -m src.main src/ --output-format html
```

**With PyPI:**

```bash
pip install metricmancer
metricmancer src/ --output-format html
```

______________________________________________________________________

## Prerequisites

### 1. Software Requirements

```bash
# Install build tools
pip install --upgrade build twine

# Verify installation
python -m build --version
twine --version
```

### 2. PyPI Accounts

- **TestPyPI**: https://test.pypi.org/account/register/ (for testing)
- **PyPI**: https://pypi.org/account/register/ (production)

**Note**: Both require separate account registrations.

### 3. Two-Factor Authentication (2FA)

- PyPI **requires** 2FA for all accounts (since 2023)
- Use authenticator app (Google Authenticator, Authy, etc.)
- Set up during account creation

### 4. API Tokens

API tokens are more secure than passwords for automated uploads.

**Create tokens:**

1. Log in to PyPI/TestPyPI
2. Go to Account Settings → API Tokens
3. Click "Add API token"
4. Scope: "Entire account" (for first upload) or specific project (after first upload)
5. Copy token immediately (won't be shown again)

**Store tokens securely:**

```bash
# Create ~/.pypirc (Linux/Mac)
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
EOF

# Set secure permissions
chmod 600 ~/.pypirc
```

______________________________________________________________________

## Pre-Publishing Checklist

Before making code changes, verify these items:

- [ ] All tests pass: `python -m pytest tests/ -v`
- [ ] Code is linted: `python -m flake8 src/ tests/`
- [ ] License file exists: `LICENSE`
- [ ] README.md is complete and accurate
- [ ] CHANGELOG.md is up to date with release notes
- [ ] Version number is correct in `pyproject.toml`
- [ ] All changes are committed to git
- [ ] Working on main branch (or release branch merged to main)

______________________________________________________________________

## Required Code Changes

### 1. Add CLI Entry Point to pyproject.toml

**File**: `pyproject.toml`

**Add this section** (after `[project.urls]`):

```toml
[project.scripts]
metricmancer = "src.main:main"
```

This allows users to run `metricmancer` directly instead of `python -m src.main`.

### 2. Refactor src/main.py to Support Entry Point

**Current structure:**

```python
# src/main.py
if __name__ == "__main__":
    # all logic here
```

**Required structure:**

```python
# src/main.py

def main():
    """Main entry point for MetricMancer CLI."""
    # Move all logic from if __name__ == "__main__" here
    args = parse_args().parse_args()
    config = AppConfig.from_cli_args(args)
    # ... rest of main logic
    return 0  # or appropriate exit code

if __name__ == "__main__":
    sys.exit(main())
```

**Why?** The entry point `src.main:main` expects a callable function named `main()`.

### 3. Separate Dev Dependencies from Runtime Dependencies

**File**: `pyproject.toml`

**Current** (lines 11-25):

```toml
dependencies = [
  "jinja2",
  "pytest",          # DEV ONLY
  "pytest-cov",      # DEV ONLY
  "coverage",        # DEV ONLY
  "tqdm",
  "PyYAML",
  "autopep8",        # DEV ONLY
  "flake8",          # DEV ONLY
  "pip-licenses",
  "unidiff>=0.7.5",
  "tree-sitter>=0.25.0",
  "tree-sitter-language-pack>=0.10.0"
]
```

**Updated**:

```toml
dependencies = [
  "jinja2",
  "tqdm",
  "PyYAML",
  "pip-licenses",
  "unidiff>=0.7.5",
  "tree-sitter>=0.25.0",
  "tree-sitter-language-pack>=0.10.0"
]

[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-cov>=4.0.0",
  "coverage>=7.0.0",
  "autopep8>=2.0.0",
  "flake8>=6.0.0",
  "build>=0.10.0",
  "twine>=4.0.0"
]
```

**Install dev dependencies:**

```bash
# For development
pip install -e ".[dev]"

# For production users
pip install metricmancer
```

### 4. Create MANIFEST.in for Static Files

**File**: `MANIFEST.in` (create in project root)

```text
# Include documentation
include README.md
include LICENSE
include CHANGELOG.md

# Include HTML templates
recursive-include src/report/templates *.html

# Include package data
recursive-include src *.py

# Exclude test files and build artifacts
recursive-exclude tests *
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
recursive-exclude * .DS_Store
exclude .gitignore
exclude .coverage
exclude .coveragerc
```

**Why?** Ensures Jinja2 templates and other static files are included in the distribution.

### 5. Add __init__.py to src/ (if missing)

**File**: `src/__init__.py`

```python
"""MetricMancer - Software Analytics Tool.

Multi-language software analytics tool for code quality, maintainability,
and technical risk analysis.
"""

__version__ = "3.2.0"
__author__ = "Thomas Lindqvist"
__license__ = "MIT"

# Import main components for easier access
from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig

__all__ = ["MetricMancerApp", "AppConfig", "__version__"]
```

### 6. Update setuptools Configuration

**File**: `pyproject.toml`

**Current** (lines 36-40):

```toml
[tool.setuptools]
packages = ["src"]

[tool.setuptools.package-dir]
"" = "."
```

**Updated**:

```toml
[tool.setuptools]
packages = { find = { where = ["."], include = ["src*"] } }
include-package-data = true

[tool.setuptools.package-data]
"src.report.templates" = ["*.html"]
```

______________________________________________________________________

## PyPI Account Setup

### 1. Create PyPI Account

**TestPyPI** (for practice):

1. Go to https://test.pypi.org/account/register/
2. Fill in username, email, password
3. Verify email
4. Enable 2FA with authenticator app

**PyPI** (production):

1. Go to https://pypi.org/account/register/
2. Fill in username, email, password (use same as TestPyPI for consistency)
3. Verify email
4. Enable 2FA with authenticator app

### 2. Create API Tokens

**TestPyPI Token:**

1. Log in to https://test.pypi.org/
2. Account Settings → API Tokens → Add API token
3. Token name: "MetricMancer-Test"
4. Scope: "Entire account" (for first upload)
5. Copy token starting with `pypi-...`

**PyPI Token:**

1. Log in to https://pypi.org/
2. Account Settings → API Tokens → Add API token
3. Token name: "MetricMancer-Production"
4. Scope: "Entire account" (for first upload)
5. Copy token starting with `pypi-...`

### 3. Configure ~/.pypirc

```bash
# Create configuration file
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR-PRODUCTION-TOKEN-HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR-TEST-TOKEN-HERE
EOF

# Secure the file
chmod 600 ~/.pypirc
```

**Security note**: Never commit `.pypirc` to git. Add to `.gitignore` if not already there.

______________________________________________________________________

## Building the Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf dist/ build/ src/*.egg-info

# Or use make if available
make clean
```

### 2. Build Source and Wheel Distributions

```bash
# Build both source distribution (.tar.gz) and wheel (.whl)
python -m build

# Expected output:
# dist/
#   metricmancer-3.2.0.tar.gz       # Source distribution
#   metricmancer-3.2.0-py3-none-any.whl  # Wheel (binary) distribution
```

### 3. Verify Build Artifacts

```bash
# List built files
ls -lh dist/

# Check wheel contents
unzip -l dist/metricmancer-3.2.0-py3-none-any.whl | less

# Verify metadata
tar -tzf dist/metricmancer-3.2.0.tar.gz | grep -E '(PKG-INFO|setup.py|pyproject.toml)'
```

### 4. Validate Package with Twine

```bash
# Check for common errors
twine check dist/*

# Expected output:
# Checking dist/metricmancer-3.2.0-py3-none-any.whl: PASSED
# Checking dist/metricmancer-3.2.0.tar.gz: PASSED
```

**Common errors and fixes:**

- `long_description_content_type` missing: Add to pyproject.toml
- Missing README: Ensure README.md exists
- Invalid RST/Markdown: Validate README syntax

______________________________________________________________________

## Testing on TestPyPI

**ALWAYS test on TestPyPI before publishing to production PyPI.**

### 1. Upload to TestPyPI

```bash
# Upload using twine
python -m twine upload --repository testpypi dist/*

# You'll see:
# Uploading distributions to https://test.pypi.org/legacy/
# Uploading metricmancer-3.2.0-py3-none-any.whl
# Uploading metricmancer-3.2.0.tar.gz
# View at: https://test.pypi.org/project/metricmancer/3.2.0/
```

### 2. Verify TestPyPI Upload

1. Visit https://test.pypi.org/project/metricmancer/
2. Check version number (3.2.0)
3. Verify description renders correctly
4. Check dependencies list
5. Verify project URLs (Homepage, Repository, Issues)

### 3. Test Installation from TestPyPI

```bash
# Create fresh virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple \
            metricmancer==3.2.0

# Note: --extra-index-url needed because TestPyPI doesn't have all dependencies
```

### 4. Test Installed Package

```bash
# Test CLI entry point
metricmancer --version
metricmancer --help

# Test actual functionality
mkdir test-project
echo "def hello(): pass" > test-project/example.py
metricmancer test-project/ --output-format summary

# Test as Python module
python -c "from src.config.app_config import AppConfig; print('Import successful')"

# Deactivate and clean up
deactivate
rm -rf test-env test-project
```

### 5. Common TestPyPI Issues

**Issue**: Dependencies not found

```
ERROR: Could not find a version that satisfies the requirement <package>
```

**Fix**: Use `--extra-index-url https://pypi.org/simple` to fetch deps from main PyPI

**Issue**: Entry point doesn't work

```
metricmancer: command not found
```

**Fix**: Verify `[project.scripts]` in pyproject.toml and `main()` function exists

**Issue**: Templates not found

```
jinja2.exceptions.TemplateNotFound: report.html
```

**Fix**: Check MANIFEST.in includes templates and setuptools config has package_data

______________________________________________________________________

## Publishing to PyPI

**STOP**: Only proceed if TestPyPI testing was 100% successful.

### 1. Final Pre-Publish Checklist

- [ ] TestPyPI upload successful
- [ ] TestPyPI installation works
- [ ] CLI entry point works (`metricmancer --help`)
- [ ] Core functionality tested on TestPyPI version
- [ ] No errors in `twine check dist/*`
- [ ] All tests pass locally
- [ ] Git tag created for version (e.g., `v3.2.0`)
- [ ] Version number won't conflict with existing PyPI versions

**Check existing versions:**

```bash
pip index versions metricmancer
# or visit https://pypi.org/project/metricmancer/#history
```

### 2. Upload to Production PyPI

```bash
# Upload to PyPI (IRREVERSIBLE - be certain!)
python -m twine upload dist/*

# Output:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading metricmancer-3.2.0-py3-none-any.whl
# Uploading metricmancer-3.2.0.tar.gz
# View at: https://pypi.org/project/metricmancer/3.2.0/
```

**⚠️ WARNING**: You **CANNOT** delete or re-upload the same version. Once uploaded, version 3.2.0 is permanent. You can
only:

- Mark version as "yanked" (discouraged for new installs but still available)
- Upload a new version (e.g., 3.2.1)

### 3. Verify Production Upload

1. Visit https://pypi.org/project/metricmancer/
2. Verify version, description, metadata
3. Check that README renders correctly
4. Verify badges (if any) display properly

### 4. Test Production Installation

```bash
# Create fresh virtual environment
python -m venv prod-test-env
source prod-test-env/bin/activate

# Install from PyPI
pip install metricmancer==3.2.0

# Test functionality
metricmancer --version
metricmancer --help

# Clean up
deactivate
rm -rf prod-test-env
```

______________________________________________________________________

## Post-Publishing

### 1. Update GitHub Release Notes

Add PyPI installation instructions to GitHub release:

````markdown
## Installation

### Via PyPI (Recommended)
```bash
pip install metricmancer==3.2.0
````

### Via GitHub

```bash
git clone https://github.com/CmdrPrompt/MetricMancer
cd MetricMancer
pip install -r requirements.txt
```

````

### 2. Update README.md

Add PyPI badge and installation section:

**Badges** (top of README):
```markdown
[![PyPI version](https://badge.fury.io/py/metricmancer.svg)](https://badge.fury.io/py/metricmancer)
[![PyPI downloads](https://img.shields.io/pypi/dm/metricmancer.svg)](https://pypi.org/project/metricmancer/)
[![Python versions](https://img.shields.io/pypi/pyversions/metricmancer.svg)](https://pypi.org/project/metricmancer/)
````

**Installation section**:

````markdown
## Installation

### From PyPI (Recommended)
```bash
pip install metricmancer
````

### From Source

```bash
git clone https://github.com/CmdrPrompt/MetricMancer
cd MetricMancer
pip install -e ".[dev]"
```

```

### 3. Announce the Release

Consider announcing on:
- GitHub Discussions or Releases page
- Python communities (Reddit: r/Python, r/learnpython)
- Twitter/X with hashtag #Python
- LinkedIn if professionally relevant
- Project website or blog

**Template announcement:**
```

MetricMancer 3.2.0 is now available on PyPI! 🎉

Install with: pip install metricmancer

New features:

- Multi-language cognitive complexity (Python, Java, Go, JS, TS, C)
- Tree-sitter-based analysis
- Enhanced HTML/JSON reports

https://pypi.org/project/metricmancer/ https://github.com/CmdrPrompt/MetricMancer

````

### 4. Monitor Package Health

**PyPI Statistics:**
- View download stats: https://pypistats.org/packages/metricmancer
- Monitor for security issues: https://pypi.org/project/metricmancer/

**Set up monitoring:**
- GitHub Dependabot: Auto-create PRs for dependency updates
- PyUp.io: Monitor dependency security
- Snyk: Vulnerability scanning

### 5. Create Project-Specific API Token

After first successful upload, create a more secure project-scoped token:

1. Log in to PyPI
2. Go to your project: https://pypi.org/manage/project/metricmancer/settings/
3. Create new API token
4. Scope: "Project: metricmancer"
5. Update `~/.pypirc` with new token

**Why?** Project-scoped tokens can only upload to metricmancer, not other packages.

---

## Troubleshooting

### Build Issues

**Error**: `ModuleNotFoundError: No module named 'build'`
```bash
pip install --upgrade build
````

**Error**: `error: Multiple top-level packages discovered`

```toml
# Fix in pyproject.toml
[tool.setuptools]
packages = { find = { where = ["."], include = ["src*"] } }
```

**Error**: `FileNotFoundError: [Errno 2] No such file or directory: 'README.md'`

```bash
# Ensure README.md exists in project root
ls -la README.md
```

### Upload Issues

**Error**: `403 Forbidden: Invalid or non-existent authentication information`

```bash
# Check ~/.pypirc has correct token
# Token should start with "pypi-"
cat ~/.pypirc
```

**Error**: `400 Bad Request: File already exists`

```bash
# Cannot re-upload same version
# Increment version in pyproject.toml (e.g., 3.2.0 → 3.2.1)
# Rebuild: python -m build
# Upload new version
```

**Error**: `400 Bad Request: The description failed to render`

```bash
# Validate README.md Markdown
# Use online validator: https://markdownlint.github.io/
# Or: pip install readme-renderer && python -m readme_renderer README.md
```

### Installation Issues

**Error**: `metricmancer: command not found` (after pip install)

```bash
# Check if entry point was created
pip show -f metricmancer | grep metricmancer

# Verify [project.scripts] in pyproject.toml
# Reinstall: pip uninstall metricmancer && pip install metricmancer
```

**Error**: `No module named 'src'`

```python
# Fix imports in code to use absolute imports
# Wrong: from .config import AppConfig
# Right: from src.config.app_config import AppConfig
```

**Error**: `jinja2.exceptions.TemplateNotFound: report.html`

```bash
# Check MANIFEST.in includes templates
# Verify wheel contains templates:
unzip -l dist/metricmancer-*.whl | grep templates
```

### Version Conflicts

**Error**: `ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/...`

```bash
# Check dependency version conflicts
pip install metricmancer --verbose

# Try with --use-deprecated=legacy-resolver
pip install metricmancer --use-deprecated=legacy-resolver
```

### PyPI Account Issues

**Error**: `403 Forbidden: The credential associated with user 'X' isn't allowed to upload`

```bash
# Ensure you're owner/maintainer of the package
# For first upload, ensure package name isn't already taken
# Check: https://pypi.org/project/metricmancer/
```

**Error**: `Two-factor authentication required`

```bash
# Enable 2FA in PyPI account settings
# Use authenticator app (Google Authenticator, Authy, etc.)
```

______________________________________________________________________

## Quick Reference: Complete Publishing Workflow

```bash
# 1. Prepare code (see Required Code Changes section)
#    - Add [project.scripts] to pyproject.toml
#    - Refactor main() function
#    - Separate dev dependencies
#    - Create MANIFEST.in

# 2. Update version
# Edit pyproject.toml: version = "3.2.0"

# 3. Run tests
python -m pytest tests/ -v

# 4. Clean and build
rm -rf dist/ build/ src/*.egg-info
python -m build

# 5. Validate
twine check dist/*

# 6. Upload to TestPyPI
twine upload --repository testpypi dist/*

# 7. Test installation
python -m venv test-env
source test-env/bin/activate
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple metricmancer
metricmancer --help
deactivate
rm -rf test-env

# 8. Upload to PyPI (PRODUCTION)
twine upload dist/*

# 9. Verify and test
pip install metricmancer==3.2.0
metricmancer --version

# 10. Update README, create GitHub release, announce
```

______________________________________________________________________

## Additional Resources

**Official Documentation:**

- PyPI User Guide: https://packaging.python.org/en/latest/guides/
- setuptools Documentation: https://setuptools.pypa.io/en/latest/
- PEP 621 (pyproject.toml): https://peps.python.org/pep-0621/
- Twine Documentation: https://twine.readthedocs.io/

**Tools:**

- TestPyPI: https://test.pypi.org/
- PyPI: https://pypi.org/
- PyPI Stats: https://pypistats.org/
- README Renderer: https://github.com/pypa/readme_renderer

**Community:**

- Python Packaging Discourse: https://discuss.python.org/c/packaging/14
- PyPA GitHub: https://github.com/pypa/
- Stack Overflow: Tag `python-packaging`

______________________________________________________________________

## Appendix: Code Changes Summary

### File: pyproject.toml

**Add:**

```toml
[project.scripts]
metricmancer = "src.main:main"

[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-cov>=4.0.0",
  "coverage>=7.0.0",
  "autopep8>=2.0.0",
  "flake8>=6.0.0",
  "build>=0.10.0",
  "twine>=4.0.0"
]
```

**Update:**

```toml
dependencies = [
  "jinja2",
  "tqdm",
  "PyYAML",
  "pip-licenses",
  "unidiff>=0.7.5",
  "tree-sitter>=0.25.0",
  "tree-sitter-language-pack>=0.10.0"
]

[tool.setuptools]
packages = { find = { where = ["."], include = ["src*"] } }
include-package-data = true

[tool.setuptools.package-data]
"src.report.templates" = ["*.html"]
```

### File: src/main.py

**Refactor:**

```python
def main():
    """Main entry point for MetricMancer CLI."""
    # All main logic here
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

### File: MANIFEST.in (new file)

```text
include README.md
include LICENSE
include CHANGELOG.md
recursive-include src/report/templates *.html
recursive-include src *.py
recursive-exclude tests *
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

### File: src/__init__.py (new file)

```python
"""MetricMancer - Software Analytics Tool."""

__version__ = "3.2.0"
__author__ = "Thomas Lindqvist"
__license__ = "MIT"

from src.app.metric_mancer_app import MetricMancerApp
from src.config.app_config import AppConfig

__all__ = ["MetricMancerApp", "AppConfig", "__version__"]
```

______________________________________________________________________

**Document Version**: 1.0 **Last Updated**: 2025-10-31 **Author**: Thomas Lindqvist **License**: MIT
