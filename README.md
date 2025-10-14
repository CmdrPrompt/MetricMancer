
# MetricMancer

MetricMancer is a software analytics tool that provides actionable insights into code quality, maintainability, and technical risk. Inspired by "Your Code as a Crime Scene" by Adam Tornhill, it analyzes source code repositories to extract key performance indicators (KPIs) such as cyclomatic complexity, code churn, and hotspots. MetricMancer is designed for extensibility, multi-language support, and integration with CI/CD pipelines.

For detailed requirements, architecture, and design, see the [Software Specification and Design](./SoftwareSpecificationAndDesign.md) document.

## Features

- **Multi-language support:** Analyze codebases in Python, JavaScript, TypeScript, Java, C#, C, C++, Go, Ada, IDL, JSON, YAML, Shell scripts, and more (via pluggable parsers).
- **Cyclomatic complexity:** Calculates logical complexity for each function/method in code files.
- **Structural complexity:** Measures nesting depth, object count, and configuration patterns in JSON/YAML files.
- **IDL complexity:** Analyzes interface definitions with structural metrics (interfaces, operations, inheritance, data structures).
- **Shell script complexity:** Analyzes control flow, loops, and functions in shell scripts.
- **Code churn:** Computes the number of commits affecting each file.
- **Hotspot analysis:** Identifies files/functions with both high complexity and high churn.
- **Code review advisor:** Generates data-driven code review recommendations based on complexity, churn, and ownership metrics.
- **Configurable thresholds:** Set custom thresholds for KPIs and grades (Low, Medium, High).
- **Aggregated KPIs:** Summarizes metrics at file, directory, and repository levels.
- **Flexible reporting:** Generates reports in CLI, HTML, JSON formats, plus specialized hotspot and review strategy reports.
- **Multi-format single run:** **[New in v3.1.0]** Generate multiple report formats in one analysis run (e.g., `--output-formats html,json,summary`) - 50-70% performance improvement by eliminating redundant scanning.
- **Extensible architecture:** Easily add new KPIs, languages, or report formats.
- **Error and edge case handling:** Robust error messages and handling for unsupported files, empty directories, and parse errors.
- **CI/CD ready:** Scriptable CLI and machine-readable JSON output for automation.

## Usage

Run from the command line:

```sh
python -m src.main <directories> [options]
```

### Common Options

- `<directories>`: One or more root folders to scan
- `--threshold-low <value>`: Set threshold for low complexity (default: 10.0)
- `--threshold-high <value>`: Set threshold for high complexity (default: 20.0)
- `--problem-file-threshold <value>`: Set threshold for individual file complexity
- `--auto-report-filename`: Generate a unique report filename based on date and scanned directories
- `--report-filename <filename>`: Set the report filename directly
- `--with-date`: Append date/time to the filename (used with --report-filename)
- `--report-folder <folder>`: Folder to write all reports to (default: **'output'**)
- `--output-format <format>`: Output format: 'summary' (default dashboard), 'human-tree' (file tree), 'html', 'json', 'machine' (CSV)
- `--output-formats <formats>`: **[New in v3.1.0]** Generate multiple formats in one run (comma-separated). Example: 'html,json,summary'. Scans code once, generates all formats - 50-70% faster than separate runs
- `--summary`: Show executive summary dashboard (default)
- `--detailed`: Show detailed file tree output
- `--level <level>`: Detail level for reports: 'file' (default) or 'function'
- `--hierarchical`: (JSON only) Output the full hierarchical data model
- `--list-hotspots`: Display list of highest hotspots after analysis
- `--hotspot-threshold <score>`: Minimum hotspot score to include (default: 50)
- `--hotspot-output <file>`: Save hotspot list to file. Use .md for markdown (default format), .txt for plain text
- `--review-strategy`: Generate code review strategy report based on KPIs
- `--review-output <file>`: Save review strategy to file (default: review_strategy.md, supports .txt and .md)
- `--review-branch-only`: Filter review strategy to only changed files in current branch
- `--review-base-branch <branch>`: Base branch for comparison (default: main)

### Examples

```sh
# Analyze <path-to-gitrepo> and test folders with default thresholds
python -m src.main <path-to-gitrepo> test

# Custom thresholds
python -m src.main <path-to-gitrepo> test --threshold-low 8 --threshold-high 15

# Generate HTML report with custom filename
python -m src.main <path-to-gitrepo> --report-filename myreport.html --output-format html

# Output executive summary (default)
python -m src.main path/to/repo

# Output detailed file tree
python -m src.main path/to/repo --detailed

# Output JSON report
python -m src.main path/to/repo --output-format json

# Output CSV (machine) report
python -m src.main path/to/repo --output-format machine

# Write report to a specific folder
python -m src.main path/to/repo --report-folder reports

# Use hierarchical JSON output
python -m src.main path/to/repo --output-format json --hierarchical

# Generate multiple formats in one run (NEW in v3.1.0 - much faster!)
python -m src.main path/to/repo --output-formats html,json,summary
python -m src.main path/to/repo tests --output-formats html,json

# Show prioritized quick win suggestions
python -m src.main path/to/repo --quick-wins

# Generate hotspot analysis
python -m src.main path/to/repo --list-hotspots --hotspot-threshold 100
python -m src.main path/to/repo --list-hotspots --hotspot-output hotspots.md

# Generate code review strategy report (all files)
python -m src.main path/to/repo --review-strategy
python -m src.main path/to/repo --review-strategy --review-output review_strategy.md

# Generate code review strategy for changed files in current branch only
python -m src.main path/to/repo --review-strategy --review-branch-only
```

### Multi-Format Generation (v3.1.0+)

**Performance improvement:** Generate multiple report formats in a single analysis run, avoiding redundant scanning and analysis.

**Use case:** You need both an HTML report for management and a JSON export for your dashboard - but don't want to wait for two full scans.

**How it works:**
1. Scans code **once**
2. Analyzes complexity, churn, and KPIs **once**
3. Generates **all specified formats** from the same analysis

**Performance:**
- **Before:** 3 separate runs for HTML, JSON, summary = ~7.8s (2.6s each)
- **After:** Single run with `--output-formats html,json,summary` = ~2.7s
- **Savings:** ~5.1 seconds (65% faster for 3 formats)

**Examples:**
```sh
# Generate HTML and JSON in one run
python -m src.main src tests --output-formats html,json

# Generate all common formats
python -m src.main src --output-formats html,json,summary

# Still works: single format (backward compatible)
python -m src.main src --output-format html
```

**Generated files** (in `output/` folder):
- `complexity_report.html` - Interactive HTML report
- `complexity_report.json` - Machine-readable JSON
- Terminal summary (for 'summary' format)

## Output

All reports are saved to the **`output/`** directory by default. This can be customized with the `--report-folder` option.

### Terminal Output Formats

- **Executive Summary (default):** Actionable dashboard showing critical issues, health metrics, and recommendations
- **Quick Wins:** Prioritized improvement suggestions ranked by ROI (impact vs. effort ratio)
- **Detailed Tree:** Traditional tree-structured output per repository, showing complexity, churn, hotspot score, and grade for each file

### Report Files

- **HTML report:** Interactive, modern report with summary, details, and usage instructions
- **JSON report:** Machine-readable output for dashboards and integrations
- **Hotspot analysis:** Markdown or text file listing high-risk files
- **Code review strategy:** Markdown or text file with prioritized review recommendations
- **Review strategy:** Markdown or text file with data-driven code review recommendations

### Cleaning Output

To clean the output directory:

```bash
# Remove all files from output directory
python clean_output.py

# Preview what would be deleted (dry-run)
python clean_output.py --dry-run

# Or use VS Code task: "Clean output directory"
```

**Example CLI Output:**

```text
.
repo_name
│   Scan-dir: <path-to-gitrepo> (Language: python)
│   | [C:12.3, Min:5.0, Max:22.0, Churn:18.1, Grade:Medium ⚠️]
│   ├── main.py [C:15, Churn:20, Hotspot:300, Grade:Medium, Ownership: {"Alice": 80.0, "Bob": 20.0}, SharedOwnership: {"num_significant_authors": 1, "significant_authors": ["Alice"]}]
│   └── utils.py [C:7, Churn:5, Hotspot:35, Grade:Low, Ownership: {"Alice": 60.0, "Bob": 40.0}, SharedOwnership: {"num_significant_authors": 2, "significant_authors": ["Alice", "Bob"]}]
```

**Example JSON Output (ownership & shared ownership excerpt):**

```json
{
	"files": [
		{
			"name": "main.py",
			"kpis": {
				"Code Ownership": {"Alice": 80.0, "Bob": 20.0},
				"Shared Ownership": {"num_significant_authors": 1, "significant_authors": ["Alice"]}
			}
		},
		{
			"name": "utils.py",
			"kpis": {
				"Code Ownership": {"Alice": 60.0, "Bob": 40.0},
				"Shared Ownership": {"num_significant_authors": 2, "significant_authors": ["Alice", "Bob"]}
			}
		}
	]
}
```

## Architecture

### Configuration Object Pattern

MetricMancer uses the **Configuration Object Pattern** to centralize all application settings, making the codebase more maintainable and reducing code churn. This architectural decision was implemented to address high modification frequency in `main.py` (23 commits/month).

**Key Components:**

1. **AppConfig** (`src/config/app_config.py`): A dataclass that encapsulates all configuration parameters with:
   - Type-safe fields with validation
   - Factory method `from_cli_args()` for easy CLI integration
   - Default values and comprehensive documentation

2. **ReportGeneratorFactory** (`src/report/report_generator_factory.py`): Factory pattern for creating report generators:
   - Eliminates conditional logic in main entry point
   - Easy to extend with new output formats
   - Clean separation of concerns

3. **MetricMancerApp** (`src/app/metric_mancer_app.py`): Application class that:
   - Accepts AppConfig as primary initialization method
   - Maintains backward compatibility with individual parameters
   - Provides clean dependency injection

**Benefits:**

- ✅ **Reduced Churn**: New features add to config, not main.py
- ✅ **Single Responsibility**: Each component has one clear purpose
- ✅ **Open/Closed Principle**: Closed for modification, open for extension
- ✅ **Testability**: Easy to mock and test components in isolation
- ✅ **Maintainability**: Clear, linear code flow with minimal complexity

**Usage Example:**

```python
from src.config.app_config import AppConfig
from src.report.report_generator_factory import ReportGeneratorFactory
from src.app.metric_mancer_app import MetricMancerApp

# Create configuration from CLI args
config = AppConfig.from_cli_args(args)

# Use factory to create appropriate report generator
generator_cls = ReportGeneratorFactory.create(config.output_format)

# Instantiate application with configuration
app = MetricMancerApp(config=config, report_generator_cls=generator_cls)
app.run()
```

For migration guidance, see [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md).

## Extending MetricMancer

- **Add new languages:** Implement a parser module and register it in `src/languages/parsers/` and `src/config.py`.
- **Add new KPIs:** Create a new KPI calculator in `src/kpis/` and register it in the configuration.
- **Customize reports:** Update templates in `src/report/templates/` for HTML, or extend CLI/JSON generators.
- **Add new output formats:** Register new format in `ReportGeneratorFactory.create()` method.
- **Extensible architecture:** The system is designed for easy addition of new metrics, languages, and report formats with minimal coupling between components. See the [SoftwareSpecificationAndDesign.md](./SoftwareSpecificationAndDesign.md) for details.

## Requirements

- Python 3.10+
- jinja2
- pydriller
- pytest (for testing)
- coverage (for test coverage)

## Key KPIs (Implemented & Planned)

**Implemented:**
- Cyclomatic Complexity (per function/method)
- Code Churn (per file)
- Hotspot Score (complexity × churn)
- Code Ownership (per file)
- Shared Ownership (per file/function, aggregation to directory/repo)

**Planned:**
- Temporal Coupling
- Change Coupling
- Author Churn / Knowledge Map
- Defect Density
- Hotspot Evolution
- Complexity Trend
- Code Age
- Test Coverage
- Logical Coupling

See [SoftwareSpecificationAndDesign.md](./SoftwareSpecificationAndDesign.md) for full KPI definitions and up-to-date implementation status.

## Testing

MetricMancer has comprehensive test coverage with 142 tests covering all functionality.

### Running Tests

**Quick test run:**
```bash
./run_tests.sh
```

**Manual test run:**
```bash
python -m pytest tests/ -v
```

**With coverage:**
```bash
python -m pytest tests/ -v --cov=src --cov-report=html
```

### Test Architecture

- **Unittest and Pytest**: Both testing frameworks supported
- **TDD Implementation**: All new features developed with test-driven development
- **CI/CD Integration**: All tests run automatically on GitHub Actions
- **Performance Tests**: Validates optimization improvements (Issue #40)

## Future Plans

- **Issue tracker integration:** Correlate code metrics with defect data from Jira, GitHub Issues, etc.
- **Test coverage integration:** Relate code coverage to hotspots and churn.
- **Historical trend analysis:** Track complexity/churn/hotspot evolution over time.
- **Accessibility:** Improve HTML report accessibility (ARIA, color contrast, keyboard navigation).

## License

MIT
