# Contributing to MetricMancer

Thank you for your interest in contributing to MetricMancer! This document provides guidelines and instructions for development.

## Development Setup

### Prerequisites

- Python 3.12+
- Git

### Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/CmdrPrompt/MetricMancer.git
   cd MetricMancer
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

## Code Quality Tools

MetricMancer uses several tools to maintain code quality:

- **autopep8** - Automatic code formatting
- **flake8** - Code linting and style checking
- **pytest** - Testing framework
- **pytest-cov** - Test coverage reporting

### Using the Code Quality Tools

#### Option 1: Using Makefile (Recommended)

```bash
# Show available commands
make help

# Auto-format code
make format

# Check code with linter
make lint

# Run all tests
make test

# Run lint + tests (CI workflow)
make check

# Clean temporary files
make clean
```

#### Option 2: Using Python Script

```bash
# Show available commands
python code_quality.py help

# Auto-format code
python code_quality.py format

# Check code with linter
python code_quality.py lint

# Run all tests
python code_quality.py test

# Run lint + tests (CI workflow)
python code_quality.py check

# Clean temporary files
python code_quality.py clean
```

#### Option 3: Manual Commands

```bash
# Auto-format code
python -m autopep8 --in-place --recursive --max-line-length=120 src/ tests/

# Check code style
python -m flake8 src/ tests/

# Run tests
python -m pytest tests/ -v --tb=short

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

## Code Style Guidelines

### PEP 8 Compliance

- **Maximum line length:** 120 characters
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Grouped and sorted (standard library, third-party, local)
- **Naming conventions:**
  - `snake_case` for functions, variables, and module names
  - `PascalCase` for class names
  - `UPPER_CASE` for constants

### Running autopep8 Before Committing

Always format your code before committing:

```bash
make format
# or
python code_quality.py format
```

### Checking Code Quality

Before pushing, ensure code passes all checks:

```bash
make check
# or
python code_quality.py check
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
python -m pytest tests/app/test_analyzer.py -v

# Run tests with coverage
python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing

# View coverage report
python -m http.server 8080 --directory coverage_html
# Then open http://localhost:8080 in browser
```

### Self-Analysis - Running MetricMancer on Itself

As part of testing and verification, run MetricMancer on its own codebase to identify quality issues:

```bash
# Quick wins - identify immediate improvements
make analyze-quick

# Summary - get high-level metrics overview
make analyze-summary

# Code review - get actionable recommendations (full repo)
make analyze-review

# Code review - ONLY changed files in current branch (faster!)
make analyze-review-branch

# Complete analysis - all reports (HTML, JSON, CLI)
make analyze-full

# Or using Python script:
python code_quality.py analyze-quick
python code_quality.py analyze-review
python code_quality.py analyze-review-branch
```

**Best Practice:** Run self-analysis before committing major changes:
1. Run `make analyze-quick` to identify quick wins
2. Run `make analyze-review-branch` to review ONLY your changed files (fast!)
3. Address high-priority issues found
4. Verify improvements with `make analyze-summary`

**Tip:** Use `analyze-review-branch` for faster feedback during development since it only analyzes files changed in your current branch compared to main.

Generated reports are stored in `output/self-analysis/`:
- `quick_wins_report.md` - Low-effort, high-impact improvements
- `code_review_recommendations.md` - Prioritized review suggestions
- `index.html` - Interactive HTML report
- `report.json` - Machine-readable data
- `report.md` - CLI-formatted report

### Writing Tests

- Place tests in the `tests/` directory
- Follow the existing test structure
- Use descriptive test names: `test_<what>_<condition>_<expected_result>`
- Follow TDD approach: Red → Green → Refactor

Example:
```python
def test_analyzer_calculates_complexity_correctly(self):
    """Test that analyzer correctly calculates cyclomatic complexity."""
    # Arrange
    analyzer = Analyzer(config)
    
    # Act
    result = analyzer.analyze_file('test.py')
    
    # Assert
    self.assertEqual(result.complexity, expected_value)
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code
- Write/update tests
- Format code: `make format`
- Check code: `make lint`
- Run tests: `make test`

### 3. Commit Changes

```bash
git add .
git commit -m "feat: Add new feature"
# or
git commit -m "fix: Fix bug in analyzer"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `style:` - Code style changes (formatting, etc.)
- `chore:` - Maintenance tasks

### 4. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Project Structure

```
MetricMancer/
├── src/
│   ├── app/                # Application core
│   │   ├── core/          # Core domain logic
│   │   ├── coordination/  # Coordination layer
│   │   ├── scanning/      # File scanning
│   │   ├── hierarchy/     # Data hierarchy
│   │   ├── kpi/           # KPI calculations
│   │   └── infrastructure/# Infrastructure services
│   ├── analysis/          # Analysis algorithms
│   ├── config/            # Configuration
│   ├── kpis/              # KPI models
│   ├── languages/         # Language parsers
│   ├── report/            # Report generation
│   └── utilities/         # Utility functions
├── tests/                 # Test files (mirrors src/)
├── output/                # Generated reports
├── docs/                  # Documentation
├── Makefile               # Code quality commands
├── code_quality.py        # Code quality script
├── .flake8                # Flake8 configuration
└── pyproject.toml         # Project configuration
```

## Architecture Guidelines

MetricMancer follows a layered architecture:

1. **Core Domain** - Business logic, entities, KPI calculations
2. **Coordination** - Orchestration between layers
3. **Infrastructure** - File I/O, Git operations, report writing
4. **Application** - Main entry point, CLI handling

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

## Common Development Tasks

### Adding a New KPI

1. Create KPI class in `src/kpis/`
2. Implement calculation logic
3. Add tests in `tests/kpis/`
4. Update `KPICalculator` to include new KPI
5. Update report templates if needed

### Adding a New Report Format

1. Create report generator in `src/report/`
2. Implement `ReportInterface`
3. Add tests in `tests/report/`
4. Register in `ReportGeneratorFactory`

### Adding Language Support

1. Create parser in `src/languages/`
2. Implement complexity calculation
3. Add tests with sample code
4. Update language detection logic

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/CmdrPrompt/MetricMancer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/CmdrPrompt/MetricMancer/discussions)
- **Documentation:** See `/docs` folder

## Dependencies and Licensing

### Adding New Dependencies

When adding new Python packages, ensure they use permissive licenses:

✅ **Allowed licenses:**
- MIT License
- Apache License 2.0
- BSD License (2-Clause or 3-Clause)
- ISC License
- Mozilla Public License 2.0 (MPL)
- zlib/libpng License

❌ **Not allowed:**
- GPL (any version)
- LGPL (any version)
- AGPL (any version)
- Commercial or proprietary licenses

### Verifying Licenses

Before adding a dependency:

```bash
# Check license with pip-licenses
pip install pip-licenses
pip-licenses --packages <package-name>

# Or check on PyPI
pip show <package-name> | grep License
```

Update [LICENSE_INFO.md](LICENSE_INFO.md) when adding new dependencies.

## License

By contributing to MetricMancer, you agree that your contributions will be licensed under the MIT License.

See [LICENSE_INFO.md](LICENSE_INFO.md) for complete licensing information including MetricMancer's license and all third-party dependencies.
