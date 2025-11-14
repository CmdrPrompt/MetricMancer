# Contributing to MetricMancer

Thank you for your interest in contributing to MetricMancer! This document provides guidelines and instructions for
development.

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
python scripts/code_quality.py help

# Auto-format code
python scripts/code_quality.py format

# Check code with linter
python scripts/code_quality.py lint

# Run all tests
python scripts/code_quality.py test

# Run lint + tests (CI workflow)
python scripts/code_quality.py check

# Clean temporary files
python scripts/code_quality.py clean
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
python scripts/code_quality.py format
```

### Checking Code Quality

Before pushing, ensure code passes all checks:

```bash
make check
# or
python scripts/code_quality.py check
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
python scripts/code_quality.py analyze-quick
python scripts/code_quality.py analyze-review
python scripts/code_quality.py analyze-review-branch
```

**Best Practice:** Run self-analysis before committing major changes:

1. Run `make analyze-quick` to identify quick wins
2. Run `make analyze-review-branch` to review ONLY your changed files (fast!)
3. Address high-priority issues found
4. Verify improvements with `make analyze-summary`

**Tip:** Use `analyze-review-branch` for faster feedback during development since it only analyzes files changed in your
current branch compared to main.

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
├── scripts/               # Utility scripts
│   ├── code_quality.py   # Code quality script
│   ├── clean_output.py   # Output cleaning script
│   └── check_licenses.py # License checking script
├── output/                # Generated reports
├── docs/                  # Documentation
├── Makefile               # Code quality commands
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

## Extending MetricMancer

MetricMancer is designed for easy extensibility. You can add new KPIs, languages, or report formats with minimal changes
to the core codebase thanks to the Factory and Strategy patterns.

### Adding a New KPI

**Step-by-step guide:**

1. **Create KPI class** in `src/kpis/<your_kpi>/`:

   ```python
   from src.kpis.base_kpi import BaseKPI

   class MyCustomKPI(BaseKPI):
       def __init__(self, value, description="My custom metric"):
           super().__init__(
               name="My Custom KPI",
               description=description,
               value=value
           )
   ```

2. **Implement calculator** in the same directory:

   ```python
   class MyCustomKPICalculator:
       def calculate(self, file_path: str, language: str) -> MyCustomKPI:
           # Your calculation logic here
           value = self._perform_analysis(file_path)
           return MyCustomKPI(value=value)
   ```

3. **Create KPI strategy** in `src/app/kpi/kpi_calculator.py`:

   ```python
   class MyCustomKPIStrategy(KPIStrategy):
       def calculate(self, file_path: str, language: str) -> Dict[str, BaseKPI]:
           calculator = MyCustomKPICalculator()
           kpi = calculator.calculate(file_path, language)
           return {"My Custom KPI": kpi}
   ```

4. **Register in KPICalculator** (`src/app/kpi/kpi_calculator.py`):

   ```python
   self.strategies = [
       ComplexityKPIStrategy(),
       MyCustomKPIStrategy(),  # Add your strategy
       # ... other strategies
   ]
   ```

5. **Add tests** in `tests/kpis/test_my_custom_kpi.py`:

   ```python
   def test_my_custom_kpi_calculation():
       calculator = MyCustomKPICalculator()
       result = calculator.calculate("test_file.py", "python")
       assert result.value > 0
   ```

6. **Update report templates** if needed:

   - HTML: `src/report/templates/report_template.html`
   - JSON: Automatically included via `BaseKPI` serialization
   - CLI: Update format classes in `src/report/cli/`

**Example from codebase:** See `src/kpis/cognitive_complexity/` for a complete implementation example.

### Adding a New Report Format

**Step-by-step guide:**

1. **Create report generator** in `src/report/<format_name>/`:

   ```python
   from src.report.report_interface import ReportInterface

   class MyCustomReportGenerator(ReportInterface):
       def __init__(self, config):
           self.config = config

       def generate(self, repo_infos: Dict[str, RepoInfo]) -> str:
           # Your report generation logic
           output = self._format_data(repo_infos)
           self._write_output(output)
           return "Report generated successfully"
   ```

2. **Implement required methods**:

   ```python
   def _format_data(self, repo_infos):
       # Convert repo data to your format
       pass

   def _write_output(self, output):
       # Write to file or console
       pass
   ```

3. **Register in Factory** (`src/report/report_generator_factory.py`):

   ```python
   class ReportGeneratorFactory:
       _FORMAT_MAP = {
           'html': HTMLReportGenerator,
           'json': JSONReportGenerator,
           'mycustom': MyCustomReportGenerator,  # Add your generator
           # ... other formats
       }
   ```

4. **Add tests** in `tests/report/test_my_custom_report.py`:

   ```python
   def test_my_custom_report_generation():
       config = AppConfig(directories=['test_data'], output_format='mycustom')
       generator = MyCustomReportGenerator(config)
       result = generator.generate(test_repo_infos)
       assert "success" in result.lower()
   ```

5. **Update CLI argument parser** in `src/main.py` (if new format needs special handling):

   ```python
   parser.add_argument('--output-format',
                       choices=['summary', 'html', 'json', 'mycustom'],
                       help='Output format')
   ```

**Example from codebase:** See `src/report/html/` or `src/report/json/` for complete implementations.

### Adding Language Support

**Step-by-step guide:**

1. **Create parser** in `src/languages/parsers/<language_name>_parser.py`:

   ```python
   class MyLanguageParser:
       def parse(self, source_code: str):
           """Parse source code and extract functions/methods."""
           # Use tree-sitter, regex, or AST parsing
           functions = self._extract_functions(source_code)
           return functions

       def _extract_functions(self, source_code: str):
           # Language-specific extraction logic
           pass
   ```

2. **Register language** in `src/languages/config.py`:

   ```python
   LANGUAGE_EXTENSIONS = {
       '.py': 'python',
       '.js': 'javascript',
       '.mylang': 'mylanguage',  # Add your language
       # ... other extensions
   }

   LANGUAGE_PARSERS = {
       'python': PythonParser,
       'javascript': JavaScriptParser,
       'mylanguage': MyLanguageParser,  # Add your parser
       # ... other parsers
   }
   ```

3. **Implement complexity calculation** (if applicable):

   ```python
   # For cyclomatic complexity, update src/kpis/complexity/
   # For cognitive complexity, update src/kpis/cognitive_complexity/
   ```

4. **Add test files** in `tests/languages/test_my_language_parser.py`:

   ```python
   def test_parse_my_language():
       parser = MyLanguageParser()
       source = """
       function myFunc() {
           if (x > 0) {
               return x;
           }
       }
       """
       functions = parser.parse(source)
       assert len(functions) == 1
       assert functions[0].name == "myFunc"
   ```

5. **Add sample code** in `tests/test_data/sample_code.<ext>` for integration tests.

**Example from codebase:** See `src/languages/parsers/python_parser.py` or tree-sitter implementations in
`src/kpis/cognitive_complexity/calculator_*.py`.

### Design Patterns Used

Understanding these patterns will help you extend MetricMancer correctly:

- **Factory Pattern**: `ReportGeneratorFactory` creates report generators based on format string
- **Strategy Pattern**: KPI calculators implement `KPIStrategy` interface for polymorphic behavior
- **Configuration Object**: `AppConfig` centralizes all settings in one type-safe object
- **Builder Pattern**: Report data structures built incrementally

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed explanations of each pattern.

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

Update [LICENSE_INFO.md](docs/LICENSE_INFO.md) when adding new dependencies.

## License

By contributing to MetricMancer, you agree that your contributions will be licensed under the MIT License.

See [LICENSE_INFO.md](docs/LICENSE_INFO.md) for complete licensing information including MetricMancer's license and all
third-party dependencies.
