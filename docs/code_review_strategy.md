# Code Review Strategy Report

MetricMancer can generate data-driven code review recommendations based on your codebase's complexity, churn, and ownership metrics. This feature helps teams optimize their code review process by focusing attention where it matters most.

## How to Generate

```bash
# Basic usage - generates review_strategy.md for all files
python -m src.main src --review-strategy

# Custom output file (supports .md and .txt)
python -m src.main src --review-strategy --review-output my_review_plan.md

# Focus on changed files in current branch only (vs main)
python -m src.main src --review-strategy --review-branch-only

# Focus on changed files vs a specific base branch
python -m src.main src --review-strategy --review-branch-only --review-base-branch develop

# Combined with other analyses
python -m src.main src --review-strategy --list-hotspots --hotspot-output hotspots.md
```

## What's Included

The code review strategy report contains:

### 1. Executive Summary
- Total files analyzed
- Critical risk files (requiring immediate attention)
- High risk files (requiring senior review)
- Estimated total review time

### 2. Priority-Based File Lists

Files are categorized by priority:

- **Priority 1 (Critical)**: High complexity + high churn = immediate action required
- **Priority 2 (High)**: Emerging hotspots or high churn areas
- **Priority 3 (Medium)**: Stable complexity or moderate risk

For each file, you get:
- Risk level assessment
- Number of reviewers needed
- Estimated review time
- Specific focus areas
- Checklist items

### 3. Review Templates

Pre-written review comment templates for different risk levels, including:
- 🔥 Critical hotspot alerts
- 📚 Knowledge sharing opportunities (single ownership)
- 🔄 High churn area warnings
- Specific action items

### 4. Resource Allocation Guidance

- Recommended time distribution across priority levels
- Reviewer assignment strategies
- Critical files requiring senior architect review

### 5. Best Practices

- Pre-review KPI assessment guidelines
- Risk-based checklists
- Knowledge management strategies
- Continuous monitoring recommendations

## Risk Classification Logic

The advisor classifies files based on multiple factors:

### Critical Risk
- **Critical Hotspots**: Complexity > 15 AND Churn > 10
- **Very High Hotspot Score**: Score > 150
- Requires: 3 reviewers (architect + 2 developers)
- Focus: Architecture, performance, refactoring

### High Risk
- **Emerging Hotspots**: Complexity 5-15 AND Churn > 10
- **High Hotspot Score**: Score 75-150
- Requires: 2 reviewers (senior + peer)
- Focus: Pattern consistency, preventive refactoring

### Medium Risk
- **Stable Complexity**: Complexity > 15 AND Churn ≤ 5
- **Medium Hotspot Score**: Score 25-75
- Requires: 1-2 reviewers
- Focus: Documentation, integration tests

### Low Risk
- **Low Hotspot Score**: Score < 25
- Requires: 1 reviewer (standard process)
- Focus: Code quality standards

## Ownership Impact

The advisor also considers ownership patterns:

- **Single Owner (>70%)**: Emphasizes knowledge transfer and documentation
- **Balanced Ownership (40-70%)**: Standard review process
- **Shared Ownership (<40%, 3+ authors)**: Focuses on API consistency
- **Fragmented Ownership (<30%, 4+ authors)**: Highlights coordination needs

## Example Use Cases

### 1. Sprint Planning
Use the report to allocate review resources at sprint start:
```bash
python -m src.main src --review-strategy --review-output sprint_review_plan.md
```

### 2. Focus on Your Branch Changes
Generate a focused review strategy for only the files you've changed:
```bash
# When working on a feature branch
python -m src.main src --review-strategy --review-branch-only --review-output my_branch_review.md
```

**Benefits:**
- Reduces review scope from 68 files → ~18 files (example)
- Focuses on files you actually modified
- Provides immediate, actionable feedback
- Ideal for pre-PR self-review

**Output comparison:**
- Full repository: `Total files analyzed: 68, Critical: 12, High: 4, Est. time: 36h 25m`
- Branch only: `Total files analyzed: 18, Critical: 7, High: 1, Est. time: 15h 5m`

### 3. Onboarding New Team Members
Help new reviewers understand which files need extra attention:
- Critical files: Pair with senior developers
- High churn areas: Learn about common patterns
- Single owner files: Knowledge transfer opportunities

### 4. Technical Debt Reduction
Identify which files should be refactored first:
- Sort by estimated review time
- Focus on critical hotspots
- Track improvements over time

### 5. Code Review Audits
Ensure review depth matches risk level:
- Compare actual vs. recommended reviewer count
- Verify time spent on critical files
- Check if checklists are being used

## Integration with Development Workflow

### Pre-Commit / Pre-PR
```bash
# Check what needs extra attention in your changes
python -m src.main src --review-strategy --review-branch-only

# Review the generated report before creating your PR
cat review_strategy.md
```

### Pull Request Template
Include relevant checklist items from the report in your PR template.

**Tip:** Run `--review-branch-only` before creating a PR to:
- Self-review critical changes
- Ensure all high-risk files have adequate tests
- Add extra documentation for complex areas

### CI/CD Pipeline
```yaml
# Example GitHub Actions step
- name: Generate Review Strategy
  run: |
    python -m src.main src --review-strategy --review-output review_strategy.md
- name: Upload Review Strategy
  uses: actions/upload-artifact@v2
  with:
    name: review-strategy
    path: review_strategy.md
```

### Weekly Team Review
1. Generate report at week start
2. Discuss critical files in team meeting
3. Assign senior reviewers to high-risk areas
4. Track whether metrics improve over time

## Metrics Used

The code review advisor leverages these KPIs:

1. **Cyclomatic Complexity**: Measures code complexity
2. **Code Churn**: Tracks change frequency (commits/month)
3. **Hotspot Score**: Complexity × Churn
4. **Code Ownership**: Author contribution percentages
5. **Shared Ownership**: Number of significant contributors

## Thresholds Reference

Based on "Your Code as a Crime Scene" by Adam Tornhill:

### Complexity
- 1-5: Low (simple procedures)
- 6-10: Moderate (well-structured)
- 11-15: High (consider refactoring)
- 16+: Very High (immediate attention)

### Churn (commits/month)
- 0-2: Stable
- 3-5: Active (normal)
- 6-10: High activity (monitor)
- 11+: Very high (investigate root causes)

### Hotspot Score
- 0-25: Low risk
- 26-75: Medium risk
- 76-150: High risk
- 151+: Critical risk

## Customization

The thresholds and recommendations can be adjusted for your project's needs. See `src/analysis/code_review_advisor.py` for implementation details.

## Related Features

- **Hotspot Analysis** (`--list-hotspots`): Quick view of highest-risk files
- **JSON Reports** (`--output-format json`): Raw data for custom analysis
- **HTML Reports** (`--output-format html`): Interactive visualization

## Further Reading

- [Software Specification and Design](../SoftwareSpecificationAndDesign.md) - Chapter 5: Analysis Framework
- [Your Code as a Crime Scene](https://pragprog.com/titles/atcrime/your-code-as-a-crime-scene/) by Adam Tornhill
