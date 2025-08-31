# ComplexityScanner


Analyze cyclomatic complexity in your codebase and generate a modern, customizable HTML report.


## Features
- Scans specified directories for code files in the following languages:
	- Python
	- JavaScript
	- TypeScript
	- Java
	- C#
	- C
	- C++
	- Go
	- Ada
- Calculates cyclomatic complexity and function count per file
- Computes code churn (change frequency) for each file
- Hotspot analysis: highlights files with high complexity and high churn
- Grades complexity (Low, Medium, High) and summarizes per language and root folder
- Highlights problematic folders and files exceeding configurable thresholds of complexity
- Flexible CLI: set thresholds, file thresholds, and report filename options
- Generates a modern HTML report with summary, details, and usage instructions

## Usage

Run from the command line:

```sh
python -m src.main <directories> [--threshold-low <value>] [--threshold-high <value>] [--problem-file-threshold <value>] [--auto-report-filename] [--report-filename <filename>] [--with-date]
```

### Parameters
- `<directories>`: One or more root folders to scan for code complexity
- `--threshold-low`: Sets the threshold for low complexity (default: 10.0)
- `--threshold-high`: Sets the threshold for high complexity (default: 20.0)
- `--problem-file-threshold`: Sets the threshold for individual file complexity (optional)
- `--auto-report-filename`: Automatically generate a unique report filename based on date and scanned directories
- `--report-filename <filename>`: Set the report filename directly (directories not included in name)
- `--with-date`: If used with `--report-filename`, appends date and time to the filename before extension

### Examples

```sh
# Default thresholds, default filename
python -m src.main src test

# Custom thresholds and file threshold
python -m src.main src test --threshold-low 10 --threshold-high 20 --problem-file-threshold 15

# Auto-generated filename
python -m src.main src test --auto-report-filename

# Custom filename
python -m src.main src test --report-filename myreport.html

# Custom filename with date/time
python -m src.main src test --report-filename myreport.html --with-date
```


## Output
- The report is generated as `complexity_report.html` by default, or with a custom/dynamic name if specified
- Hotspot-score (complexity × churn) visas för varje fil där båda mätvärden finns, både i HTML-rapporten och CLI-rapporten.
- CLI-rapporten presenteras som en trädstruktur per repository, där varje fil visar komplexitet, churn, hotspot-score och grade. Exempel:

```
.
repo_name
│   Scan-dir: src (Language: python)
│   | [C:12.3, Min:5.0, Max:22.0, Churn:18.1, Grade:Medium ⚠️]
│   ├── main.py [C:15, Churn:20, Hotspot:300, Grade:Medium]
│   └── utils.py [C:7, Churn:5, Hotspot:35, Grade:Low]
```
- The summary section highlights folders and files exceeding the thresholds
- Usage instructions are included at the bottom of the report

## Extending
- Add support for more languages in `src/config.py`
- Customize the report appearance in `src/templates/report.html`

## Requirements
- Python 3.7+
- Jinja2 (`pip install jinja2`)

## Cyclomatic Complexity

Cyclomatic complexity is a software metric used to measure the number of independent paths through a program's source code. It is commonly used to:
- Assess code maintainability: High complexity can indicate code that is harder to understand, test, and maintain.
- Identify risk areas: Functions or files with high complexity are more likely to contain bugs and be difficult to modify safely.
- Guide refactoring: Developers often target highly complex code for simplification or splitting into smaller units.
- Plan testing: Cyclomatic complexity suggests the minimum number of test cases needed to cover all possible code paths.
- Enforce coding standards: Many teams set complexity thresholds and require action if these are exceeded.

**Note:** The cyclomatic complexity value for each file corresponds to the minimum number of test cases required to cover all possible code paths. However, this does not account for data validation, edge cases, or combinations of multiple decision points.


## Future Plans

The following features and KPIs are planned for future releases:

- **Git/Bitbucket-based KPIs:**
	- Code Ownership: Measures how many different developers have modified a file. Identifies files with low ownership (high risk for bugs).
	- Review Latency: Time from pull request creation to first comment. Highlights bottlenecks in the review process.
	- Merge Time: Time from PR creation to merge. Measures collaboration and delivery speed.
	- Comment Density: Number of comments per PR. Indicator of code review quality.

- **Jira-based KPIs:**
	- Cycle Time: Time from "In Progress" to "Done". Measures delivery speed.
	- Lead Time: Time from issue creation to delivery. Identifies bottlenecks in planning and prioritization.
	- Issue Reopen Rate: How often issues are reopened after being closed. Indicator of solution quality and test coverage.
	- Sprint Accuracy: Amount of planned work actually delivered. Measures team predictability.
	- Flow Efficiency: Active time vs. waiting time in the issue flow. Identifies waste in the process.

- **Combined Metric Ideas:**
	- Risk Index = churn × complexity × ownership diversity
	- Review Health Score = comment density ÷ review latency
	- Delivery Score = sprint accuracy × flow efficiency
	- Stability Score = low churn × high complexity × low reopen rate

MIT
