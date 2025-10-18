# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MetricMancer is a software analytics tool that analyzes code repositories to extract key performance indicators (KPIs) like cyclomatic complexity, code churn, hotspots, and code ownership. Inspired by "Your Code as a Crime Scene" by Adam Tornhill, it provides actionable insights into code quality and technical risk.

**Key Features:**
- Multi-language support (Python, JavaScript, TypeScript, Java, C#, C++, Go, Shell, Ada, IDL, JSON, YAML)
- Multiple report formats (CLI summary/tree, HTML, JSON, CSV)
- Multi-format generation in single run (50-70% faster than separate runs)
- Hotspot analysis (complexity × churn)
- Code ownership and shared ownership metrics
- Code review strategy recommendations

## Common Development Commands

### Testing

```bash
# Run all tests (pytest - preferred)
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing

# Run single test file
python -m pytest tests/path/to/test_file.py -v

# Run single test function
python -m pytest tests/path/to/test_file.py::test_function_name -v

# Quick test script
./run_tests.sh
```

### Linting and Formatting

```bash
# Auto-format code
python -m autopep8 --in-place --recursive --max-line-length=120 src/ tests/

# Run linter
python -m flake8 src/ tests/

# Check licenses
python check_licenses.py
```

### Running MetricMancer

```bash
# Basic analysis (generates summary report)
python -m src.main <directory> [additional_directories...]

# Generate multiple formats in one run (much faster)
python -m src.main src/ --output-formats html,json,summary

# Custom thresholds
python -m src.main src/ --threshold-low 8 --threshold-high 15

# HTML report
python -m src.main src/ --output-format html --report-filename report.html

# Code review recommendations (full repo)
python -m src.main src/ --review-strategy

# Code review for changed files only (current branch)
python -m src.main src/ --review-strategy --review-branch-only --review-base-branch main

# Hotspot analysis
python -m src.main src/ --list-hotspots --hotspot-threshold 100 --hotspot-output hotspots.md

# Custom churn period (default is 30 days)
python -m src.main src/ --churn-period 90
```

### Self-Analysis (Makefile Targets)

```bash
# Quick wins - immediate improvements
make analyze-quick

# Summary report
make analyze-summary

# Code review recommendations (full repo)
make analyze-review

# Code review for current branch only
make analyze-review-branch

# Complete analysis (HTML + JSON + CLI)
make analyze-full

# Run all quality checks (lint + test + licenses)
make check
```

### Utility Commands

```bash
# Clean output directory
python clean_output.py

# Clean output (dry-run)
python clean_output.py --dry-run

# Clean temporary files
make clean
```

## Architecture Overview

MetricMancer uses modern design patterns emphasizing maintainability and extensibility:

### Core Design Patterns

1. **Configuration Object Pattern** (`src/config/app_config.py`)
   - All configuration centralized in `AppConfig` dataclass
   - Type-safe with automatic validation
   - Reduces main.py complexity (17% reduction achieved)
   - Factory method `AppConfig.from_cli_args()` for CLI integration

2. **Factory Pattern** (`src/report/report_generator_factory.py`)
   - `ReportGeneratorFactory.create(format)` eliminates conditional logic
   - Easy to extend with new output formats
   - Maps format strings to generator classes

3. **Strategy Pattern** (`src/report/report_interface.py`)
   - All report generators implement `ReportInterface`
   - Polymorphic behavior allows interchangeable generators
   - Clean separation of format-specific rendering logic

4. **Builder Pattern** (`src/report/report_data_collector.py`)
   - Incremental construction of complex report data
   - Fluent interface for data collection

### Key Components

```
src/
├── main.py                  # Entry point - simplified via Configuration Object Pattern
├── config/
│   └── app_config.py       # Central configuration dataclass
├── app/
│   ├── metric_mancer_app.py # Application orchestration
│   ├── analyzer.py          # Main analysis coordinator
│   ├── scanner.py           # Directory/file scanning
│   └── hierarchy_builder.py # Data model construction
├── kpis/                    # KPI calculators (complexity, churn, hotspots, ownership)
│   ├── complexity/
│   ├── codechurn/
│   ├── hotspot/
│   ├── codeownership/
│   └── sharedcodeownership/
├── languages/               # Language parsers and configuration
│   ├── config.py           # Language/extension mapping
│   └── parsers/            # Language-specific parsers
├── report/                  # Report generation
│   ├── report_generator_factory.py  # Factory for creating generators
│   ├── cli/                # CLI report formats (summary, tree, quick-wins)
│   ├── html/               # HTML report generator
│   ├── json/               # JSON report generator
│   └── templates/          # Jinja2 templates for HTML
├── analysis/                # Higher-level analysis
│   ├── hotspot_analyzer.py # Hotspot detection
│   └── code_review_advisor.py # Review strategy generation
└── utilities/               # Helper functions
    ├── git_helpers.py
    ├── git_cache.py        # Git command caching
    └── cli_helpers.py
```

### Data Model Hierarchy

```
RepoInfo (inherits ScanDir)
├── repo_root_path: str
├── repo_name: str
└── (from ScanDir):
    ├── files: Dict[str, File]
    ├── scan_dirs: Dict[str, ScanDir]
    └── kpis: Dict[str, BaseKPI]

File
├── name: str
├── file_path: str
├── kpis: Dict[str, BaseKPI]
└── functions: List[Function]

Function
├── name: str
└── kpis: Dict[str, BaseKPI]
```

See `plantuml/data_model_2025-09-24.puml` for complete UML diagram.

## Important Implementation Details

### Configuration Flow

```python
# main.py uses Configuration Object Pattern
args = parse_args().parse_args()
config = AppConfig.from_cli_args(args)  # Type-safe configuration
generator_cls = ReportGeneratorFactory.create(config.output_format)
app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
app.run()
```

### Multi-Format Generation (v3.1.0)

When using `--output-formats html,json,summary`:
- Code is scanned once, all formats generated in single pass
- 50-70% performance improvement vs. separate runs
- `MetricMancerApp` receives `report_generator_cls=None` for multi-format mode
- Factory creates appropriate generators for each format

### Code Churn Measurement

**IMPORTANT**: Current churn implementation measures **total historical commits**, not commits per time period.
- This deviates from "Your Code as a Crime Scene" methodology
- Should measure commits/month over configurable period
- `--churn-period <days>` parameter exists but implementation needs completion
- See `SoftwareSpecificationAndDesign.md` section 5.0.2 for correct thresholds

### Adding New Features

**New Output Format:**
1. Implement `ReportInterface` in `src/report/`
2. Add to `ReportGeneratorFactory._FORMAT_MAP`
3. No changes needed in `main.py` or `MetricMancerApp`

**New KPI:**
1. Create calculator inheriting from `BaseKPI` in `src/kpis/`
2. Implement `calculate()` method
3. Register in appropriate analyzer

**New Language:**
1. Create parser in `src/languages/parsers/`
2. Add extension mapping in `src/languages/config.py`
3. Parser must extract functions/methods for complexity analysis

## Testing Architecture

- **Framework**: pytest (primary), unittest (legacy support)
- **Coverage Target**: >80% for core functionality
- **Test Location**: `tests/` directory mirrors `src/` structure
- **Current Stats**: 675+ passing tests, high coverage

**Test Organization:**
```
tests/
├── app/              # Application layer tests
├── config/           # Configuration tests
├── kpis/             # KPI calculator tests
├── report/           # Report generator tests
└── test_main.py      # Entry point tests
```

**Key Testing Principles:**
- **TDD RED-GREEN-REFACTOR**: ALWAYS write tests BEFORE implementation
  1. 🔴 RED: Write failing test first
  2. 🟢 GREEN: Write minimal code to pass test
  3. 🔵 REFACTOR: Improve code while keeping tests green
- Test isolation: Use mocks/fixtures for external dependencies
- Backward compatibility: All legacy tests maintained during refactoring
- Edge cases: Explicit edge case test files (e.g., `test_*_edge.py`)

**IMPORTANT - Development Workflow:**
1. **Always follow RED-GREEN-REFACTOR** for all new features/fixes
2. **Run tests after each change**: `python -m pytest tests/ -v`
3. **Ensure all tests pass** before proposing commits
4. **Follow ARCHITECTURE.md** - Use Strategy pattern, SOLID principles, etc.
5. **Claude Code can always run tests without user confirmation** - Test execution is encouraged and never requires permission

## Documentation

**Architecture & Design:**
- `ARCHITECTURE.md` - Detailed patterns, SOLID principles, component architecture
- `SoftwareSpecificationAndDesign.md` - Complete requirements, use cases, analysis framework
- `MIGRATION_GUIDE.md` - Migration to Configuration Object Pattern
- `plantuml/` - Static class diagrams (architecture, data model)
- `mermaid/` - Dynamic flow diagrams (system flows, processes)

**Development:**
- `CONTRIBUTING.md` - Contribution guidelines
- `CHANGELOG.md` - Release history and changes
- `LICENSE_INFO.md` - Licensing information for all dependencies

## Code Quality Standards

- **Line Length**: 120 characters (PEP8 extended)
- **Style**: PEP8 with autopep8 formatting
- **Type Hints**: Recommended for new code
- **Docstrings**: Required for public functions/classes
- **Test Coverage**: >80% for new code

## Git Workflow

**Branch Naming:**
- Feature: `<issue-number>-feature-<name>`
- Bugfix: `<issue-number>-bugfix-<name>`
- Refactor: `<issue-number>-refactor-<name>`

**Commit Workflow (IMPORTANT):**
1. **Claude Code NEVER commits directly** - User commits manually
2. When ready to commit, Claude Code should:
   - Run `git add` for changed files
   - Propose a commit message following conventional commits format
   - Wait for user to commit manually
3. This ensures user maintains control and awareness of changes

**Commit Message Format:**
- Follow conventional commits: `type(scope): description`
- Types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`
- Reference issue numbers: `feat(#62): add cognitive complexity to CLI report`
- Include Claude Code attribution: "🤖 Generated with [Claude Code](https://claude.com/claude-code)"

**Example Commit Proposal:**
```bash
# Claude Code runs:
git add src/report/cli/cli_report_format.py tests/report/test_cli_report_format.py

# Claude Code proposes:
# Commit message: "test(#62): add end-to-end tests for cognitive complexity in FileAnalyzer"
#
# Then USER runs:
git commit -m "test(#62): add end-to-end tests for cognitive complexity in FileAnalyzer

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Key Files to Know

- `src/main.py` - Entry point, simplified via patterns (cyclomatic complexity: 10, down from 12)
- `src/config/app_config.py` - Central configuration (70+ lines)
- `src/app/metric_mancer_app.py` - Main application class
- `src/report/report_generator_factory.py` - Generator factory
- `src/kpis/complexity/analyzer.py` - Complexity calculation (supports 10+ languages)
- `src/kpis/codechurn/code_churn.py` - Churn analysis (needs time-based fix)
- `src/analysis/code_review_advisor.py` - Code review recommendations

## Performance Characteristics

- **Small repos** (<100 files): ~2s
- **Medium repos** (1,000 files): ~15s
- **Large repos** (10,000 files): ~2 min
- **Multi-format generation**: 50-70% faster than separate runs (v3.1.0)

## Output Files

All reports go to `output/` directory by default (configurable with `--report-folder`):
- HTML reports: `index.html` (interactive, modern)
- JSON reports: `report.json` (machine-readable, OpenSearch-compatible)
- CLI reports: Saved as `.md` files when using multi-format
- Hotspot reports: `.md` or `.txt`
- Review strategy reports: `code_review_recommendations.md` or `review_strategy_branch.md`

## VS Code Integration

Tasks defined in `.vscode/tasks.json`:
- "Run all tests (pytest)" - Default test task
- "Run tests with coverage (pytest)" - Full coverage workflow
- "Activate venv" - Activate virtual environment
- "Clean output directory" - Clean generated reports
- "Serve output files" - HTTP server for viewing HTML reports

## Dependencies

**Core:**
- jinja2 - HTML template rendering
- pydriller - Git history analysis
- pytest, pytest-cov - Testing
- autopep8, flake8 - Code quality
- PyYAML - YAML parsing
- tqdm - Progress bars

**Python Version**: 3.10+ required

## Common Pitfalls

1. **Import paths**: Always use `from src.module import ...` (not relative imports)
2. **Virtual environment**: Activate `.venv` before running (ensure `PYTHONPATH` includes src/)
3. **Git cache**: Git operations are cached for performance - use `git_cache.py`
4. **Churn periods**: Current implementation doesn't respect time-based churn correctly
5. **Test isolation**: Some tests depend on git state - check test fixtures
6. **Multi-format**: When using `--output-formats`, pass `None` for report_generator_cls

## Useful Patterns in Codebase

**Configuration access:**
```python
config = AppConfig.from_cli_args(args)
threshold_low = config.threshold_low  # Type-safe access
```

**Creating report generators:**
```python
generator_cls = ReportGeneratorFactory.create('html')
generator = generator_cls(config)
output = generator.generate(repo_infos)
```

**KPI calculation:**
```python
kpi = ComplexityKPI()
complexity = kpi.calculate(file_path, language)
```

**Git operations (cached):**
```python
from src.utilities.git_cache import GitCache
cache = GitCache()
commits = cache.get_commits(repo_path, file_path)
```
