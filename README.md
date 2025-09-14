
# MetricMancer

MetricMancer is a software analytics tool that provides actionable insights into code quality, maintainability, and technical risk. Inspired by "Your Code as a Crime Scene" by Adam Tornhill, it analyzes source code repositories to extract key performance indicators (KPIs) such as cyclomatic complexity, code churn, and hotspots. MetricMancer is designed for extensibility, multi-language support, and integration with CI/CD pipelines.

For detailed requirements, architecture, and design, see the [Software Specification and Design](./SoftwareSpecificationAndDesign.md) document.

## Features

- **Multi-language support:** Analyze codebases in Python, JavaScript, TypeScript, Java, C#, C, C++, Go, Ada, and more (via pluggable parsers).
- **Cyclomatic complexity:** Calculates logical complexity for each function/method.
- **Code churn:** Computes the number of commits affecting each file.
- **Hotspot analysis:** Identifies files/functions with both high complexity and high churn.
- **Configurable thresholds:** Set custom thresholds for KPIs and grades (Low, Medium, High).
- **Aggregated KPIs:** Summarizes metrics at file, directory, and repository levels.
- **Flexible reporting:** Generates reports in CLI, HTML, and JSON formats.
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
- `--with-date`: Append date/time to the filename
- `--cli-report`: Output the report to the command line in a tree structure

### Examples

```sh
# Analyze src and test folders with default thresholds
python -m src.main src test

# Custom thresholds
python -m src.main src test --threshold-low 8 --threshold-high 15

# Generate HTML report with custom filename
python -m src.main src --report-filename myreport.html

# Output CLI report
python -m src.main src --cli-report
```

## Output

- **HTML report:** Interactive, modern report with summary, details, and usage instructions
- **CLI report:** Tree-structured output per repository, showing complexity, churn, hotspot score, and grade for each file
- **JSON report:** Machine-readable output for dashboards and integrations

**Example CLI Output:**

```text
.
repo_name
│   Scan-dir: src (Language: python)
│   | [C:12.3, Min:5.0, Max:22.0, Churn:18.1, Grade:Medium ⚠️]
│   ├── main.py [C:15, Churn:20, Hotspot:300, Grade:Medium]
│   └── utils.py [C:7, Churn:5, Hotspot:35, Grade:Low]
```

## Extending MetricMancer

- **Add new languages:** Implement a parser module and register it in `src/languages/parsers/` and `src/config.py`.
- **Add new KPIs:** Create a new KPI calculator in `src/kpis/` and register it in the configuration.
- **Customize reports:** Update templates in `src/report/templates/` for HTML, or extend CLI/JSON generators.

## Requirements

- Python 3.10+
- jinja2
- pytest
- coverage
- pydriller

## Key KPIs (Current & Planned)

- **Implemented:**
  - Cyclomatic Complexity (per function/method)
  - Code Churn (per file)
  - Hotspot Score (complexity × churn)
- **Planned:**
  - Temporal Coupling
  - Change Coupling
  - Author Churn / Knowledge Map
  - Code Ownership
  - Defect Density
  - Hotspot Evolution
  - Complexity Trend
  - Code Age
  - Test Coverage
  - Logical Coupling

See [SoftwareSpecificationAndDesign.md](./SoftwareSpecificationAndDesign.md) for full KPI definitions and implementation status.

## Future Plans

- **Issue tracker integration:** Correlate code metrics with defect data from Jira, GitHub Issues, etc.
- **Test coverage integration:** Relate code coverage to hotspots and churn.
- **Historical trend analysis:** Track complexity/churn/hotspot evolution over time.
- **Accessibility:** Improve HTML report accessibility (ARIA, color contrast, keyboard navigation).
- **Localization:** Support for additional languages in reports.

## License

MIT
