# Testing with Python 3.10 (CI/CD Compatibility)

## Overview

GitHub Actions CI/CD uses Python 3.10.18, while your local development environment may use a newer version (e.g., Python
3.12). To ensure compatibility before merging, always test with Python 3.10.

## Setup Python 3.10 Virtual Environment

### One-Time Setup

```bash
# Install Python 3.10 (Ubuntu/Debian with deadsnakes PPA)
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.10 python3.10-venv python3.10-distutils

# Verify installation
python3.10 --version  # Should show Python 3.10.x
```

### Create Python 3.10 Virtual Environment

```bash
# Create venv
python3.10 -m venv .venv-py310

# Activate venv
source .venv-py310/bin/activate

# Verify Python version
python --version  # Should show Python 3.10.x

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install MetricMancer with all dependencies
pip install -e .
```

## Running Tests

### Before Merging to Main

**ALWAYS** run tests in Python 3.10 environment before creating a PR:

```bash
# Activate Python 3.10 venv
source .venv-py310/bin/activate

# Run all tests
python -m pytest tests/ -v --tb=short

# Run linting
python -m flake8 src/ tests/ --count --max-line-length=120

# Run specific test file
python -m pytest tests/path/to/test_file.py -v
```

### Expected Results

```
839 passed, 80 warnings in ~3-4 seconds
0 flake8 errors
```

## Common Compatibility Issues

### 1. Multi-line F-Strings

**Problem:** Multi-line f-strings with implicit line continuations work in Python 3.12+ but fail in Python 3.10.

**❌ Breaks in Python 3.10:**

```python
print(
    f"Value: {var} {
        'High' if x > 5 else 'Low'}"
)
```

**✅ Works in Python 3.10:**

```python
label = 'High' if x > 5 else 'Low'
print(f"Value: {var} {label}")
```

### 2. Match Statements

**Problem:** `match/case` syntax introduced in Python 3.10, but avoid if supporting older versions.

### 3. Type Hints

**Problem:** Some newer type hint features (e.g., `X | Y` union syntax) require Python 3.10+.

**✅ Safe:**

```python
from typing import Union
def func(x: Union[int, str]) -> None:
    pass
```

**⚠️ Python 3.10+ only:**

```python
def func(x: int | str) -> None:
    pass
```

## CI/CD Environment Details

**GitHub Actions Workflow:** `.github/workflows/test.yml`

- **Python Version:** 3.10.18
- **OS:** ubuntu-latest
- **Test Command:** `python -m pytest tests/ -v --tb=short`
- **Linting:** `flake8 src/ tests/ --max-line-length=120`

## Switching Between Environments

### Development (Python 3.12)

```bash
source .venv/bin/activate
python --version  # 3.12.x
```

### Pre-Merge Testing (Python 3.10)

```bash
source .venv-py310/bin/activate
python --version  # 3.10.x
```

### Deactivate

```bash
deactivate
```

## Best Practices

1. **Always test in Python 3.10 before merging**
2. **Keep both venvs up to date** with dependencies:
   ```bash
   source .venv-py310/bin/activate
   pip install -e . --upgrade
   ```
3. **Check syntax compatibility** - avoid Python 3.11+ features
4. **Run linting in both environments** to catch version-specific issues
5. **Add `.venv-py310/` to `.gitignore`** (already done)

## Troubleshooting

### ImportError or ModuleNotFoundError

```bash
# Reinstall dependencies
source .venv-py310/bin/activate
pip install -e . --force-reinstall
```

### SyntaxError in tests

This means you're using Python 3.11+ syntax. Review the "Common Compatibility Issues" section above.

### Tests pass locally but fail in CI

1. Activate Python 3.10 venv: `source .venv-py310/bin/activate`
2. Run exact CI command: `python -m pytest tests/ -v --tb=short`
3. Fix any issues
4. Re-run tests
5. Commit and push

______________________________________________________________________

**Last Updated:** 2025-10-28 **Python 3.10 Version:** 3.10.19 **CI/CD Python Version:** 3.10.18
