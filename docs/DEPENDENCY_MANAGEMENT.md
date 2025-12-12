# Dependency Management - Quick Reference

## Summary

MetricMancer uses **`pyproject.toml`** as the single source of truth for all dependencies (PEP 621/517 standard).

## Key Files

| File                                   | Purpose                       | When to Update            |
| -------------------------------------- | ----------------------------- | ------------------------- |
| **`pyproject.toml`**                   | ✅ PRIMARY - All dependencies | Add/update packages       |
| **`.python-version`**                  | Python version pinning        | Change Python requirement |
| **`.github/workflows/python-app.yml`** | CI/CD configuration           | Change test setup         |
| **`Makefile`**                         | Development commands          | Change install process    |

❌ **NO `requirements.txt`** - Not needed with modern Python packaging

## Installation Commands

### For Developers (Local/Codespaces)

```bash
# Quick setup (recommended)
python3.10 -m venv .venv
source .venv/bin/activate
make install

# Manual setup
pip install --upgrade pip
pip install -e ".[dev]"  # Runtime + dev dependencies
```

### For CI/CD (GitHub Actions)

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install -e ".[dev]"
```

### For End Users (PyPI)

```bash
pip install metricmancer  # Runtime dependencies only
```

## Dependency Categories

### Runtime (Core)

```toml
[project]
dependencies = [
  "jinja2>=3.1.0",
  "tqdm>=4.65.0",
  "PyYAML>=6.0",
  "pip-licenses>=4.0",
  "unidiff>=0.7.5",
  "tree-sitter>=0.25.0",
  "tree-sitter-language-pack>=0.10.0"  # ⚠️ NOT tree-sitter-languages!
]
```

### Development (Optional)

```toml
[project.optional-dependencies]
dev = [
  "pytest>=7.0.0",
  "pytest-cov>=4.0.0",
  "coverage>=7.0.0",
  "autopep8>=2.0.0",
  "flake8>=6.0.0"
]
```

### Build (Optional)

```toml
build = [
  "build>=1.0.0",
  "twine>=4.0.0"
]
```

## Critical: Tree-Sitter Migration (v3.2.0)

**⚠️ BREAKING CHANGE in v3.2.0**

| ❌ OLD (Deprecated)     | ✅ NEW (Current)            |
| ----------------------- | --------------------------- |
| `tree-sitter-languages` | `tree-sitter-language-pack` |

**Why?**

- Old package abandoned/unmaintained
- New package officially supported
- Better compatibility with tree-sitter 0.25+

**Migration:**

```bash
pip uninstall tree-sitter-languages -y
pip install tree-sitter-language-pack>=0.10.0
```

**Automatic Fix:**

```bash
make install  # Detects and removes old package automatically
```

## Verification

```bash
# Check tree-sitter packages
pip list | grep tree-sitter

# Expected output:
tree-sitter                0.25.0+
tree-sitter-language-pack  0.10.0+

# NOT:
tree-sitter-languages      ❌ MUST NOT BE PRESENT

# Run all tests
python -m pytest tests/ -v
# Expected: 839 passed, 0 failed
```

## Troubleshooting

### Error: `ModuleNotFoundError: No module named 'tree_sitter_language_pack'`

**Solution:**

```bash
make install  # Automatic fix
# OR
pip uninstall tree-sitter-languages -y
pip install tree-sitter-language-pack>=0.10.0
```

### Error: Tests failing (121 failures)

**Cause:** Wrong tree-sitter package installed

**Solution:** See above

## Adding New Dependencies

### Runtime Dependency

```toml
# pyproject.toml
[project]
dependencies = [
  # ... existing ...
  "new-package>=1.0.0"
]
```

### Dev Dependency

```toml
# pyproject.toml
[project.optional-dependencies]
dev = [
  # ... existing ...
  "new-dev-tool>=1.0.0"
]
```

**Then:**

```bash
pip install -e ".[dev]"  # Reinstall with new dependency
```

## Environment-Specific Notes

### Local Development

- Use virtual environment: `python3.10 -m venv .venv`
- Install: `make install`
- Verify: `pip check`

### GitHub Codespaces

- Python pre-installed (3.12+, compatible)
- Run: `make install`
- Auto-setup: Future enhancement with `.devcontainer/devcontainer.json`

### CI/CD (GitHub Actions)

- Python 3.10 specified in workflow
- Install command: `pip install -e ".[dev]"`
- Runs all tests automatically

### Production (PyPI)

- Users install: `pip install metricmancer`
- Only runtime dependencies installed
- No test/dev tools needed

## Best Practices

1. ✅ Always use virtual environments
2. ✅ Pin Python version: See `.python-version`
3. ✅ Use `make install` for consistent setup
4. ✅ Run `pip check` to verify integrity
5. ✅ Run tests after dependency changes
6. ❌ Never commit virtual environment directories
7. ❌ Never use `tree-sitter-languages` (old package)

## Related Documentation

- Full setup guide: [SETUP.md](SETUP.md)
- PyPI publishing: [PYPI_PUBLISHING_GUIDE.md](PYPI_PUBLISHING_GUIDE.md)
- Development: [CONTRIBUTING.md](../CONTRIBUTING.md)
- Changelog: [CHANGELOG.md](../CHANGELOG.md) (see v3.2.0 migration notes)

______________________________________________________________________

**Last Updated:** 2025-11-12 (v3.2.0) **Python Version:** 3.10+ **Build System:** setuptools (PEP 517/621)
