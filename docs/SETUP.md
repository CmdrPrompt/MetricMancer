# MetricMancer Development Environment Setup

This guide ensures correct dependency installation across all environments: local development, GitHub Codespaces, and CI/CD pipelines.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Dependency Management](#dependency-management)
3. [Environment-Specific Setup](#environment-specific-setup)
4. [Troubleshooting](#troubleshooting)
5. [Verification](#verification)

---

## Quick Start

### Prerequisites
- **Python 3.10+** (see `.python-version` in repo root)
- **Git** installed and configured
- **Virtual environment** recommended

### One-Command Setup

```bash
# Create virtual environment
python3.10 -m venv .venv

# Install all dependencies (runtime + dev tools)
source .venv/bin/activate
make install

# Verify installation
python -m pytest tests/ -v
```

---

## Dependency Management

MetricMancer uses **`pyproject.toml`** as the single source of truth for dependencies (PEP 621 standard).

### Dependency Categories

#### 1. Runtime Dependencies (Core)
Required for MetricMancer to run. Installed with `pip install metricmancer`:

```toml
[project]
dependencies = [
  "jinja2>=3.1.0",           # HTML report templates
  "pydriller>=2.0",          # Git history analysis
  "tqdm>=4.65.0",            # Progress bars
  "PyYAML>=6.0",             # YAML config parsing
  "pip-licenses>=4.0",       # License compliance
  "unidiff>=0.7.5",          # Diff parsing
  "tree-sitter>=0.25.0",     # Syntax tree parsing (v3.2.0+)
  "tree-sitter-language-pack>=0.10.0"  # Language grammars (v3.2.0+)
]
```

**⚠️ IMPORTANT**: As of v3.2.0, we use `tree-sitter-language-pack` (NOT `tree-sitter-languages`).
- Old package: `tree-sitter-languages` (deprecated, abandoned)
- New package: `tree-sitter-language-pack` (maintained, official)
- See [CHANGELOG.md](../CHANGELOG.md) line 38-39 for migration details

#### 2. Development Dependencies (Optional)
Testing, linting, formatting tools. Installed with `pip install -e ".[dev]"`:

```toml
[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",           # Test framework
  "pytest-cov>=4.0.0",       # Coverage reporting
  "coverage>=7.0.0",         # Coverage analysis
  "autopep8>=2.0.0",         # Code formatting
  "flake8>=6.0.0"            # Linting
]
```

#### 3. Build Dependencies (Optional)
PyPI publishing tools. Installed with `pip install -e ".[build]"`:

```toml
build = [
  "build>=1.0.0",            # Build system
  "twine>=4.0.0"             # PyPI upload
]
```

### Why No `requirements.txt`?

Modern Python projects use `pyproject.toml` (PEP 517/621):
- ✅ Single source of truth
- ✅ Separates runtime vs. dev dependencies
- ✅ Works with all build tools (pip, poetry, pipenv)
- ✅ Supports optional dependency groups
- ✅ PyPI standard since 2021

**For compatibility**, you can still generate one:
```bash
pip freeze > requirements.txt  # If needed for legacy tools
```

---

## Environment-Specific Setup

### 1. Local Development (macOS/Linux/Windows)

```bash
# Clone repository
git clone https://github.com/CmdrPrompt/MetricMancer.git
cd MetricMancer

# Create virtual environment (Python 3.10+)
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows

# Install all dependencies using Makefile
make install

# OR install manually:
pip install --upgrade pip
pip install -e .               # Runtime dependencies
pip install -e ".[dev]"        # + Development dependencies
pip install -e ".[build]"      # + Build dependencies (optional)
```

**Verify Installation:**
```bash
# Check Python version
python --version  # Should be 3.10+

# Check tree-sitter packages
pip show tree-sitter tree-sitter-language-pack

# Run tests
python -m pytest tests/ -v
```

### 2. GitHub Codespaces

Codespaces uses the GitHub-hosted environment with pre-installed Python.

**Setup:**
```bash
# Codespaces auto-activates Python, but verify version
python --version  # Should be 3.10+

# Install dependencies
make install

# OR manual install:
pip install --upgrade pip
pip install -e ".[dev]"
```

**Codespaces Auto-Setup (Future Enhancement):**
Create `.devcontainer/devcontainer.json`:
```json
{
  "name": "MetricMancer Dev",
  "image": "mcr.microsoft.com/devcontainers/python:3.10",
  "postCreateCommand": "pip install --upgrade pip && pip install -e '.[dev]'",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.vscode-pylance"
      ]
    }
  }
}
```

### 3. CI/CD (GitHub Actions)

Current workflow: `.github/workflows/python-app.yml`

**Key Points:**
- ✅ Uses Python 3.10
- ✅ Installs via `pip install -e .` (includes runtime deps from `pyproject.toml`)
- ✅ Automatically includes `tree-sitter-language-pack>=0.10.0`

**Current Configuration:**
```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.10'

- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e .  # Installs from pyproject.toml
```

**Best Practice (Add Dev Dependencies for Testing):**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e ".[dev]"  # Includes pytest, coverage, etc.
```

### 4. PyPI Installation (End Users)

After publishing to PyPI:

```bash
# Production installation (runtime dependencies only)
pip install metricmancer

# Run MetricMancer
metricmancer src/ --output-format html
```

Users get:
- ✅ All runtime dependencies automatically
- ✅ No test/dev tools (smaller install)
- ✅ CLI command `metricmancer` (no need for `python -m src.main`)

---

## Troubleshooting

### Problem 1: Tree-Sitter Import Error

**Symptom:**
```python
ModuleNotFoundError: No module named 'tree_sitter_language_pack'
```

**Cause:** Old `tree-sitter-languages` package installed instead of `tree-sitter-language-pack`.

**Solution:**
```bash
source .venv/bin/activate
pip uninstall tree-sitter-languages -y
pip install tree-sitter-language-pack>=0.10.0
python -m pytest tests/ -v  # Verify fix
```

**Prevention:** Always use `make install` - it automatically removes conflicting packages.

### Problem 2: Tests Fail (121 failures)

**Symptom:**
```
======================= 121 failed, 718 passed in 3.72s ========================
```

**Cause:** Missing or incorrect tree-sitter dependencies.

**Solution:**
```bash
# Check installed versions
pip list | grep tree-sitter

# Should show:
# tree-sitter           0.25.0 (or higher)
# tree-sitter-language-pack  0.10.0 (or higher)

# NOT:
# tree-sitter-languages  1.10.2  ❌ WRONG!

# Fix:
make install  # Automatically fixes dependencies
```

### Problem 3: Python Version Mismatch

**Symptom:**
```
ERROR: Package 'metricmancer' requires a different Python: 3.8.0 not in '>=3.10'
```

**Solution:**
```bash
# Check Python version
python --version

# Use Python 3.10+ (see .python-version file)
python3.10 -m venv .venv
source .venv/bin/activate
make install
```

### Problem 4: Dependency Conflicts

**Symptom:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**Solution:**
```bash
# Clean virtual environment
rm -rf .venv

# Recreate from scratch
python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"

# Verify no conflicts
pip check
```

### Problem 5: Makefile Commands Fail

**Symptom:**
```bash
make install
# Error: /bin/sh: source: not found
```

**Cause:** Using `sh` instead of `bash`.

**Solution:**
```bash
# Verify Makefile uses bash (line 3)
grep SHELL Makefile
# Should show: SHELL := /bin/bash

# OR run commands manually:
.venv/bin/python -m pip install -e ".[dev]"
```

---

## Verification

### Step 1: Check Python Version
```bash
python --version
# Expected: Python 3.10.x or higher
```

### Step 2: Check Tree-Sitter Packages
```bash
pip show tree-sitter tree-sitter-language-pack
# Expected output:
# Name: tree-sitter
# Version: 0.25.0 (or higher)
# ---
# Name: tree-sitter-language-pack
# Version: 0.10.0 (or higher)
```

### Step 3: Run All Tests
```bash
python -m pytest tests/ -v --tb=short
# Expected: 839 passed, 0 failed
```

### Step 4: Check PEP8 Compliance
```bash
python -m flake8 src/ tests/
# Expected: 0 errors
```

### Step 5: Run MetricMancer on Itself
```bash
python -m src.main src/ --output-format summary
# Expected: Generates report without errors
```

### Automated Verification Script

```bash
#!/bin/bash
# verify_setup.sh - Automated environment verification

echo "🔍 MetricMancer Environment Verification"
echo "========================================"
echo ""

echo "1. Checking Python version..."
python --version || { echo "❌ Python not found"; exit 1; }
echo ""

echo "2. Checking virtual environment..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected (recommended)"
fi
echo ""

echo "3. Checking tree-sitter packages..."
pip show tree-sitter tree-sitter-language-pack > /dev/null 2>&1 && \
    echo "✅ Tree-sitter packages installed" || \
    echo "❌ Tree-sitter packages missing"
echo ""

echo "4. Running tests..."
python -m pytest tests/ -v --tb=short -x || { echo "❌ Tests failed"; exit 1; }
echo ""

echo "5. Checking code quality..."
python -m flake8 src/ tests/ || { echo "❌ PEP8 violations found"; exit 1; }
echo ""

echo "✅ All verifications passed!"
```

**Usage:**
```bash
chmod +x verify_setup.sh
./verify_setup.sh
```

---

## Summary: Installation Command Reference

| Environment | Command | Installs |
|-------------|---------|----------|
| **Local Dev** | `make install` | Runtime + Dev deps |
| **Codespaces** | `make install` | Runtime + Dev deps |
| **CI/CD** | `pip install -e ".[dev]"` | Runtime + Dev deps |
| **PyPI Users** | `pip install metricmancer` | Runtime only |
| **Build Tools** | `pip install -e ".[build]"` | + Build deps |

**Key Points:**
- ✅ `pyproject.toml` is the single source of truth
- ✅ Use `make install` for foolproof setup (auto-removes conflicts)
- ✅ Always use `tree-sitter-language-pack` (NOT `tree-sitter-languages`)
- ✅ Python 3.10+ required (see `.python-version`)
- ✅ Virtual environments recommended

---

## Next Steps

After setup:
1. Read [CONTRIBUTING.md](../CONTRIBUTING.md) for development workflow
2. Read [ARCHITECTURE.md](../ARCHITECTURE.md) for code structure
3. Run `make help` to see all available commands
4. Run `make analyze-quick` to analyze MetricMancer itself

For PyPI publishing, see [PYPI_PUBLISHING_GUIDE.md](PYPI_PUBLISHING_GUIDE.md).
