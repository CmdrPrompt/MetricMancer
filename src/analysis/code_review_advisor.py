"""
Code Review Advisor - Generates code review recommendations based on KPI metrics.
Based on "Your Code as a Crime Scene" methodology by Adam Tornhill.
"""

import os
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass


@dataclass
class ReviewRecommendation:
    """Represents a code review recommendation for a file."""
    file_path: str
    risk_level: str  # "critical", "high", "medium", "low"
    priority: int  # 1-5, where 1 is highest
    reviewers_needed: int
    focus_areas: List[str]
    checklist_items: List[str]
    template: str
    estimated_time_minutes: int


class CodeReviewAdvisor:
    """Generates code review recommendations based on complexity, churn, and ownership metrics."""

    def __init__(self):
        self.recommendations = []

    def analyze_file(self, file_path: str, complexity: int, churn: float,
                     hotspot: int, ownership_data: Optional[Dict[str, float]] = None,
                     shared_ownership_data: Optional[Dict[str, Any]] = None) -> ReviewRecommendation:
        """
        Analyze a single file and generate review recommendations.

        Args:
            file_path: Path to the file
            complexity: Cyclomatic complexity
            churn: Churn rate (commits/month)
            hotspot: Hotspot score (complexity × churn)
            ownership_data: Dict of author -> percentage (Code Ownership)
            shared_ownership_data: Dict with num_significant_authors, authors, threshold (Shared Ownership)

        Returns:
            ReviewRecommendation object
        """
        # Determine risk level and category
        risk_level, category = self._classify_risk(complexity, churn, hotspot)

        # Calculate ownership concentration using both ownership types
        ownership_type = self._analyze_ownership(ownership_data, shared_ownership_data)

        # Generate recommendations
        priority = self._calculate_priority(risk_level, category)
        reviewers_needed = self._determine_reviewer_count(risk_level, complexity)
        focus_areas = self._generate_focus_areas(complexity, churn, category, ownership_type)
        checklist = self._generate_checklist(complexity, churn, ownership_type)
        template = self._generate_template(risk_level, complexity, churn, ownership_type, file_path)
        estimated_time = self._estimate_review_time(complexity, churn, risk_level)

        return ReviewRecommendation(
            file_path=file_path,
            risk_level=risk_level,
            priority=priority,
            reviewers_needed=reviewers_needed,
            focus_areas=focus_areas,
            checklist_items=checklist,
            template=template,
            estimated_time_minutes=estimated_time
        )

    def _classify_risk(self, complexity: int, churn: float, hotspot: int) -> Tuple[str, str]:
        """Classify file into risk level and category."""
        if complexity > 15 and churn > 10:
            return ("critical", "critical_hotspot")
        elif complexity > 15 and churn <= 5:
            return ("medium", "stable_complexity")
        elif 5 <= complexity <= 15 and churn > 10:
            return ("high", "emerging_hotspot")
        elif complexity < 5 and churn > 10:
            return ("low", "active_simple")
        elif hotspot > 150:
            return ("critical", "critical_hotspot")
        elif hotspot > 75:
            return ("high", "high_risk")
        elif hotspot > 25:
            return ("medium", "medium_risk")
        else:
            return ("low", "low_risk")

    def _get_ownership_from_shared_data(self, shared_ownership_data: Dict[str, Any]) -> str:
        """Determine ownership type from shared ownership data."""
        num_significant = shared_ownership_data.get('num_significant_authors', 0)
        authors = shared_ownership_data.get('authors', [])
        
        # Filter out placeholders
        real_authors = [a for a in authors if a != 'Not Committed Yet' and a.strip()]
        num_real = len(real_authors)
        
        # Determine ownership based on author counts
        if num_significant <= 1 and num_real <= 1:
            return "single_owner"
        elif num_significant >= 4 or num_real >= 4:
            return "fragmented"
        elif num_significant >= 3 or num_real >= 3:
            return "shared"
        else:
            return "balanced"
    
    def _get_ownership_from_code_data(self, ownership_data: Dict[str, float]) -> str:
        """Determine ownership type from code ownership data."""
        if not ownership_data:
            return "unknown"
        
        max_ownership = max(ownership_data.values())
        num_authors = len(ownership_data)
        
        if max_ownership >= 70:
            return "single_owner"
        elif max_ownership < 30 and num_authors >= 4:
            return "fragmented"
        elif num_authors >= 3:
            return "shared"
        else:
            return "balanced"

    def _analyze_ownership(self, ownership_data: Optional[Dict[str, float]] = None,
                           shared_ownership_data: Optional[Dict[str, Any]] = None) -> str:
        """Analyze ownership distribution using both Code and Shared Ownership data."""
        # Use Shared Ownership data if available (more accurate)
        if shared_ownership_data and 'num_significant_authors' in shared_ownership_data:
            return self._get_ownership_from_shared_data(shared_ownership_data)
        
        # Fallback to Code Ownership data
        return self._get_ownership_from_code_data(ownership_data)

    def _calculate_priority(self, risk_level: str, category: str) -> int:
        """Calculate review priority (1-5, where 1 is highest)."""
        priority_map = {
            "critical": 1,
            "high": 2,
            "medium": 3,
            "low": 4
        }
        return priority_map.get(risk_level, 5)

    def _determine_reviewer_count(self, risk_level: str, complexity: int) -> int:
        """Determine how many reviewers are needed."""
        if risk_level == "critical" or complexity > 50:
            return 3  # Senior architect + 2 reviewers
        elif risk_level == "high" or complexity > 20:
            return 2
        else:
            return 1

    def _generate_focus_areas(self, complexity: int, churn: float,
                              category: str, ownership_type: str) -> List[str]:
        """Generate specific focus areas for review."""
        focus_areas = []
        
        # Define focus areas based on different aspects
        complexity_areas = ["Complexity Management", "Code Simplification Opportunities", 
                           "Error Handling Patterns"]
        churn_areas = ["Root Cause Analysis", "Pattern Consistency", 
                       "Technical Debt Assessment"]
        critical_areas = ["Architectural Impact", "Performance Implications", 
                         "Test Coverage Adequacy"]
        ownership_areas = {
            "single_owner": ["Knowledge Transfer", "Documentation Quality"],
            "fragmented": ["API Consistency", "Coordination Overhead"]
        }
        
        # Add focus areas based on conditions
        if complexity > 15:
            focus_areas.extend(complexity_areas)
        if churn > 10:
            focus_areas.extend(churn_areas)
        if category == "critical_hotspot":
            focus_areas.extend(critical_areas)
        if ownership_type in ownership_areas:
            focus_areas.extend(ownership_areas[ownership_type])
        
        return focus_areas

    def _generate_checklist(self, complexity: int, churn: float,
                            ownership_type: str) -> List[str]:
        """Generate review checklist items."""
        # Define checklist items for different conditions
        complexity_items = [
            "Is the change adding unnecessary complexity?",
            "Can complex logic be extracted into smaller functions?",
            "Are edge cases properly handled?",
            "Is error handling comprehensive?",
            "Would this benefit from simplification?",
            "Are there clear unit tests for complex paths?"
        ]
        
        churn_items = [
            "Does this change follow established patterns in the file?",
            "Is this change addressing root cause or symptoms?",
            "Could this change reduce future churn?",
            "Are we introducing technical debt?",
            "Is the change scope appropriate?",
            "Do we need architectural discussion before proceeding?"
        ]
        
        ownership_items = {
            "single_owner": [
                "Is documentation clear enough for new contributors?",
                "Should we involve additional team members for knowledge transfer?",
                "Are design decisions explained?",
                "Could this be an opportunity for pair programming?"
            ],
            "fragmented": [
                "Does this change affect module interfaces?",
                "Do we need broader team consultation?",
                "Are we maintaining API compatibility?",
                "Should this trigger integration testing?",
                "Do other teams need to be notified?"
            ]
        }
        
        default_items = [
            "Does this change maintain code quality standards?",
            "Are tests adequate?",
            "Is documentation updated if needed?"
        ]
        
        # Build checklist
        checklist = []
        if complexity > 15:
            checklist.extend(complexity_items)
        if churn > 10:
            checklist.extend(churn_items)
        if ownership_type in ownership_items:
            checklist.extend(ownership_items[ownership_type])
        if not checklist:
            checklist.extend(default_items)
        
        return checklist

    def _get_template_header(self, risk_level: str, file_path: str, 
                            complexity: int, churn: float) -> List[str]:
        """Generate template header based on risk level."""
        headers = {
            "critical": [
                f"🔥 CRITICAL HOTSPOT ALERT: {file_path}",
                f"   Complexity: {complexity} | Churn: {churn:.1f} commits/month",
                ""
            ],
            "high": [
                f"⚠️  HIGH RISK AREA: {file_path}",
                f"   Complexity: {complexity} | Churn: {churn:.1f} commits/month",
                ""
            ]
        }
        return headers.get(risk_level, [])
    
    def _get_template_ownership_context(self, ownership_type: str) -> List[str]:
        """Generate ownership context section."""
        ownership_contexts = {
            "single_owner": [
                "📚 KNOWLEDGE SHARING OPPORTUNITY: Single owner detected",
                "   - Consider involving additional reviewers for knowledge transfer",
                "   - Document design decisions clearly",
                ""
            ],
            "fragmented": [
                "👥 HIGH COORDINATION: Multiple active contributors",
                "   - Ensure API consistency across changes",
                "   - Consider broader team discussion if needed",
                ""
            ]
        }
        return ownership_contexts.get(ownership_type, [])
    
    def _get_template_focus_items(self, complexity: int, churn: float, 
                                  risk_level: str) -> List[str]:
        """Generate focus items for review."""
        items = ["Review Focus:"]
        
        if complexity > 15:
            items.extend([
                "   □ Complexity: Can logic be simplified or extracted?",
                "   □ Testing: Comprehensive coverage for complex paths?"
            ])
        if churn > 10:
            items.extend([
                "   □ Patterns: Following established conventions?",
                "   □ Root Cause: Addressing underlying issues?"
            ])
        if risk_level in ["critical", "high"]:
            items.extend([
                "   □ Architecture: Discuss impact before merge",
                "   □ Performance: Consider performance implications"
            ])
        
        return items
    
    def _get_template_actions(self, risk_level: str) -> List[str]:
        """Generate required actions based on risk level."""
        actions = {
            "critical": [
                "Action Required:",
                "   ⚡ Mandatory architecture review",
                "   ⚡ Minimum 2 approvals required",
                "   ⚡ Comprehensive test coverage verification"
            ],
            "high": [
                "Action Required:",
                "   ⚠️  Senior developer review recommended",
                "   ⚠️  Consider refactoring opportunities"
            ]
        }
        return actions.get(risk_level, ["Action Required:", "   ✓ Standard review process"])

    def _generate_template(self, risk_level: str, complexity: int, churn: float,
                           ownership_type: str, file_path: str) -> str:
        """Generate a review comment template."""
        template_parts = []
        
        # Add sections
        template_parts.extend(self._get_template_header(risk_level, file_path, complexity, churn))
        template_parts.extend(self._get_template_ownership_context(ownership_type))
        template_parts.extend(self._get_template_focus_items(complexity, churn, risk_level))
        template_parts.append("")
        template_parts.extend(self._get_template_actions(risk_level))
        
        return "\n".join(template_parts)

    def _estimate_review_time(self, complexity: int, churn: float, risk_level: str) -> int:
        """Estimate review time in minutes."""
        # Define time additions based on thresholds
        complexity_time = {50: 60, 20: 30, 10: 15}
        churn_time = {15: 20, 10: 10}
        risk_time = {"critical": 30, "high": 15}
        
        # Calculate total time
        base_time = 15
        
        # Add complexity time (first matching threshold)
        for threshold, time in sorted(complexity_time.items(), reverse=True):
            if complexity > threshold:
                base_time += time
                break
        
        # Add churn time (first matching threshold)
        for threshold, time in sorted(churn_time.items(), reverse=True):
            if churn > threshold:
                base_time += time
                break
        
        # Add risk time
        base_time += risk_time.get(risk_level, 0)
        
        return base_time


def generate_review_report(data: Dict[str, Any], output_file: Optional[str] = None,
                           filter_files: Optional[List[str]] = None,
                           branch_name: Optional[str] = None,
                           base_branch: Optional[str] = None) -> str:
    """
    Generate a comprehensive code review strategy report from KPI data.

    Args:
        data: Report data dictionary (from JSON report)
        output_file: Optional file path to save the report
        filter_files: Optional list of file paths to filter by (e.g., changed files in branch)
        branch_name: Optional current branch name to display in report
        base_branch: Optional base branch name for comparison

    Returns:
        Formatted report string
    """
    advisor = CodeReviewAdvisor()
    recommendations = []

    # Extract files and their metrics
    files_data = _extract_files_from_data(data)

    # Filter files if filter list provided
    if filter_files:
        # Normalize paths for comparison (both relative and absolute paths)
        filter_set = set()
        for f in filter_files:
            # Add both the path as-is and just the filename part
            filter_set.add(os.path.normpath(f))
            # Also add the path relative to any common prefixes
            filter_set.add(f.lstrip('./'))

        original_count = len(files_data)
        filtered_data = []
        for file_info in files_data:
            file_path = file_info['path']
            norm_path = os.path.normpath(file_path)

            # Check for exact match or if the file path ends with any of the filter paths
            if (norm_path in filter_set or
                any(norm_path.endswith(os.path.normpath(ff)) or
                    os.path.normpath(ff).endswith(norm_path) for ff in filter_files)):
                filtered_data.append(file_info)

        files_data = filtered_data
        print(f"   Filtered: {original_count} files → {len(files_data)} files")

    for file_info in files_data:
        rec = advisor.analyze_file(
            file_path=file_info['path'],
            complexity=file_info['complexity'],
            churn=file_info['churn'],
            hotspot=file_info['hotspot'],
            ownership_data=file_info.get('ownership'),
            shared_ownership_data=file_info.get('shared_ownership')
        )
        recommendations.append(rec)

    # Sort by priority
    recommendations.sort(key=lambda x: (x.priority, -x.estimated_time_minutes))

    # Generate report - check file extension to determine format
    use_markdown = output_file and output_file.endswith('.md')

    if use_markdown:
        report = _format_review_report_markdown(recommendations, filter_files is not None,
                                                branch_name=branch_name, base_branch=base_branch)
    else:
        report = _format_review_report(recommendations, filter_files is not None,
                                       branch_name=branch_name, base_branch=base_branch)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Code review strategy report saved to: {output_file}")

    return report


def _extract_files_from_data(data: Dict[str, Any], path: str = '') -> List[Dict[str, Any]]:
    """Extract file information from hierarchical data structure."""
    files = []

    if isinstance(data, dict):
        if 'files' in data:
            for filename, filedata in data['files'].items():
                file_path = f"{path}/{filename}" if path else filename

                kpis = filedata.get('kpis', {})
                ownership = filedata.get('ownership', {})

                # Extract Shared Ownership data from KPIs
                shared_ownership = {}
                if 'Shared Ownership' in kpis:
                    shared_ownership = kpis['Shared Ownership']

                files.append({
                    'path': file_path,
                    'complexity': kpis.get('complexity', 0),
                    'churn': kpis.get('churn', 0),
                    'hotspot': kpis.get('hotspot', 0),
                    'ownership': ownership,
                    'shared_ownership': shared_ownership
                })

        if 'scan_dirs' in data:
            for dirname, dirdata in data['scan_dirs'].items():
                dir_path = f"{path}/{dirname}" if path else dirname
                files.extend(_extract_files_from_data(dirdata, dir_path))

    return files


def _format_md_header(is_filtered: bool, branch_name: Optional[str],
                     base_branch: Optional[str]) -> List[str]:
    """Format markdown report header."""
    output = []
    output.append("# 📋 Code Review Strategy Report")
    output.append("")
    output.append("**Based on Complexity, Churn, and Ownership Metrics**")
    output.append("")

    if is_filtered:
        output.append("> 🔍 **FILTERED**: Showing only changed files in current branch")
        if branch_name:
            output.append(f"> 📍 **Current Branch**: `{branch_name}`")
        if base_branch:
            output.append(f"> 📊 **Comparing against**: `{base_branch}`")
        output.append("")
    
    return output


def _format_md_summary(recommendations: List[ReviewRecommendation]) -> List[str]:
    """Format markdown executive summary."""
    output = []
    output.append("## 📊 Executive Summary")
    output.append("")

    critical_files = [r for r in recommendations if r.risk_level == "critical"]
    high_files = [r for r in recommendations if r.risk_level == "high"]
    total_time = sum(r.estimated_time_minutes for r in recommendations)

    output.append("| Metric | Value |")
    output.append("|--------|-------|")
    output.append(f"| **Total files analyzed** | {len(recommendations)} |")
    output.append(f"| **Critical risk files** 🔴 | {len(critical_files)} (require immediate attention) |")
    output.append(f"| **High risk files** 🟡 | {len(high_files)} (require senior review) |")
    output.append(f"| **Estimated total review time** | {total_time // 60}h {total_time % 60}m |")
    output.append("")
    
    return output


def _format_md_priority_section(recommendations: List[ReviewRecommendation],
                                priority: int, emoji: str, label: str) -> List[str]:
    """Format a single priority section in markdown."""
    output = []
    priority_recs = [r for r in recommendations if r.priority == priority]
    
    if not priority_recs:
        return output

    output.append(f"## {emoji} {label} Priority Files (Priority {priority})")
    output.append("")

    for rec in priority_recs[:10]:  # Show top 10 per priority
        output.append(f"### 📄 `{rec.file_path}`")
        output.append("")

        # File metrics in table
        output.append("| Metric | Value |")
        output.append("|--------|-------|")
        output.append(f"| **Risk Level** | {rec.risk_level.upper()} |")
        output.append(f"| **Reviewers Needed** | {rec.reviewers_needed} |")
        output.append(f"| **Estimated Time** | {rec.estimated_time_minutes} minutes |")
        output.append("")

        # Focus areas
        output.append("**Focus Areas:**")
        output.append("")
        for area in rec.focus_areas:
            output.append(f"- {area}")
        output.append("")

        # Review checklist
        output.append("**Review Checklist:**")
        output.append("")
        for item in rec.checklist_items:
            output.append(f"- [ ] {item}")
        output.append("")
        output.append("---")
        output.append("")

    if len(priority_recs) > 10:
        output.append(f"*... and {len(priority_recs) - 10} more files at this priority level*")
        output.append("")
    
    return output


def _format_md_resource_allocation(recommendations: List[ReviewRecommendation]) -> List[str]:
    """Format markdown resource allocation section."""
    output = []
    output.append("## 👥 Resource Allocation Guidance")
    output.append("")

    output.append("### ⏱️ Recommended Review Time Distribution")
    output.append("")

    critical_files = [r for r in recommendations if r.risk_level == "critical"]
    high_files = [r for r in recommendations if r.risk_level == "high"]
    critical_time = sum(r.estimated_time_minutes for r in critical_files)
    high_time = sum(r.estimated_time_minutes for r in high_files)
    total_time = sum(r.estimated_time_minutes for r in recommendations)

    if total_time > 0:
        output.append("| Category | Time | Percentage |")
        output.append("|----------|------|------------|")
        output.append(f"| **Critical files** 🔴 | {critical_time}m | {critical_time * 100 // total_time}% |")
        output.append(f"| **High priority** 🟡 | {high_time}m | {high_time * 100 // total_time}% |")
        output.append("")

    output.append("### 👤 Reviewer Assignment Strategy")
    output.append("")
    output.append("- **Critical files** 🔴: Senior architect + 2 experienced developers")
    output.append("- **High priority** 🟡: Senior developer + peer reviewer")
    output.append("- **Medium/Low** 🟢: Standard peer review")
    output.append("")
    
    return output


def _format_md_best_practices() -> List[str]:
    """Format markdown best practices section."""
    output = []
    output.append("## 💡 Best Practices")
    output.append("")

    output.append("### 1. Pre-Review KPI Assessment")
    output.append("")
    output.append("- Check complexity, churn, and ownership metrics before reviewing")
    output.append("- Adjust review depth based on risk level")
    output.append("")

    output.append("### 2. Use Risk-Based Checklists")
    output.append("")
    output.append("- **High complexity files**: Focus on simplification opportunities")
    output.append("- **High churn files**: Investigate root causes of instability")
    output.append("- **Single owner files**: Emphasize knowledge transfer")
    output.append("")

    output.append("### 3. Knowledge Management")
    output.append("")
    output.append("- Use reviews for knowledge transfer in single-owner files")
    output.append("- Document decisions in high-complexity areas")
    output.append("- Encourage pair programming for critical hotspots")
    output.append("")

    output.append("### 4. Continuous Monitoring")
    output.append("")
    output.append("- Track whether changes increase or decrease metrics")
    output.append("- Celebrate complexity reductions")
    output.append("- Monitor churn patterns for early warning signs")
    output.append("")

    output.append("---")
    output.append("")
    output.append("*Report generated by MetricMancer, based on 'Your Code as a Crime Scene' methodology*")
    
    return output


def _format_review_report_markdown(recommendations: List[ReviewRecommendation],
                                   is_filtered: bool = False,
                                   branch_name: Optional[str] = None,
                                   base_branch: Optional[str] = None) -> str:
    """Format recommendations into a markdown report."""
    output = []

    # Header
    output.extend(_format_md_header(is_filtered, branch_name, base_branch))
    
    # Executive Summary
    output.extend(_format_md_summary(recommendations))

    # Priority-based recommendations
    priority_config = {
        1: ("🔴", "CRITICAL"),
        2: ("🟡", "HIGH"),
        3: ("🟢", "MEDIUM")
    }

    for priority, (emoji, label) in priority_config.items():
        output.extend(_format_md_priority_section(recommendations, priority, emoji, label))

    # Example review template
    critical_files = [r for r in recommendations if r.risk_level == "critical"]
    if critical_files:
        output.append("## 📝 Example Review Template")
        output.append("")
        output.append("*(For critical files)*")
        output.append("")
        output.append("```")
        output.append(critical_files[0].template)
        output.append("```")
        output.append("")

    # Resource allocation
    output.extend(_format_md_resource_allocation(recommendations))
    
    # Best practices
    output.extend(_format_md_best_practices())

    return "\n".join(output)


def _format_txt_header(is_filtered: bool, branch_name: Optional[str],
                      base_branch: Optional[str]) -> List[str]:
    """Format text report header."""
    output = []
    output.append("=" * 100)
    output.append("CODE REVIEW STRATEGY REPORT")
    output.append("Based on Complexity, Churn, and Ownership Metrics")
    if is_filtered:
        output.append("🔍 FILTERED: Showing only changed files in current branch")
        if branch_name:
            output.append(f"📍 Current Branch: {branch_name}")
        if base_branch:
            output.append(f"📊 Comparing against: {base_branch}")
    output.append("=" * 100)
    output.append("")
    return output


def _format_txt_summary(recommendations: List[ReviewRecommendation]) -> List[str]:
    """Format text executive summary."""
    output = []
    output.append("EXECUTIVE SUMMARY")
    output.append("-" * 100)

    critical_files = [r for r in recommendations if r.risk_level == "critical"]
    high_files = [r for r in recommendations if r.risk_level == "high"]
    total_time = sum(r.estimated_time_minutes for r in recommendations)

    output.append(f"Total files analyzed: {len(recommendations)}")
    output.append(f"Critical risk files: {len(critical_files)} (require immediate attention)")
    output.append(f"High risk files: {len(high_files)} (require senior review)")
    output.append(f"Estimated total review time: {total_time // 60}h {total_time % 60}m")
    output.append("")
    return output


def _format_txt_priority_section(recommendations: List[ReviewRecommendation],
                                 priority: int, label: str) -> List[str]:
    """Format a single priority section in text format."""
    output = []
    priority_recs = [r for r in recommendations if r.priority == priority]
    
    if not priority_recs:
        return output

    output.append(f"{label} PRIORITY FILES (Priority {priority})")
    output.append("-" * 100)
    output.append("")

    for rec in priority_recs[:10]:  # Show top 10 per priority
        output.append(f"File: {rec.file_path}")
        output.append(f"   Risk Level: {rec.risk_level.upper()}")
        output.append(f"   Reviewers Needed: {rec.reviewers_needed}")
        output.append(f"   Estimated Time: {rec.estimated_time_minutes} minutes")
        output.append(f"   Focus Areas: {', '.join(rec.focus_areas)}")
        output.append("")
        output.append(f"   Review Checklist:")

        # Always show all checklist items (simpler and more useful)
        for item in rec.checklist_items:
            output.append(f"      □ {item}")
        output.append("")

    if len(priority_recs) > 10:
        output.append(f"   ... and {len(priority_recs) - 10} more files at this priority level")
        output.append("")
    
    return output


def _format_txt_resource_allocation(recommendations: List[ReviewRecommendation]) -> List[str]:
    """Format text resource allocation section."""
    output = []
    output.append("RESOURCE ALLOCATION GUIDANCE")
    output.append("-" * 100)
    output.append("")
    output.append("Recommended Review Time Distribution:")

    critical_files = [r for r in recommendations if r.risk_level == "critical"]
    high_files = [r for r in recommendations if r.risk_level == "high"]
    critical_time = sum(r.estimated_time_minutes for r in critical_files)
    high_time = sum(r.estimated_time_minutes for r in high_files)
    total_time = sum(r.estimated_time_minutes for r in recommendations)

    if total_time > 0:
        output.append(f"   Critical files: {critical_time}m ({critical_time * 100 // total_time}% of total time)")
        output.append(f"   High priority: {high_time}m ({high_time * 100 // total_time}% of total time)")

    output.append("")
    output.append("Reviewer Assignment Strategy:")
    output.append("   - Critical files: Senior architect + 2 experienced developers")
    output.append("   - High priority: Senior developer + peer reviewer")
    output.append("   - Medium/Low: Standard peer review")
    output.append("")
    return output


def _format_txt_best_practices() -> List[str]:
    """Format text best practices section."""
    output = []
    output.append("BEST PRACTICES")
    output.append("-" * 100)
    output.append("1. Pre-Review KPI Assessment:")
    output.append("   - Check complexity, churn, and ownership metrics before reviewing")
    output.append("   - Adjust review depth based on risk level")
    output.append("")
    output.append("2. Use Risk-Based Checklists:")
    output.append("   - High complexity files: Focus on simplification opportunities")
    output.append("   - High churn files: Investigate root causes of instability")
    output.append("   - Single owner files: Emphasize knowledge transfer")
    output.append("")
    output.append("3. Knowledge Management:")
    output.append("   - Use reviews for knowledge transfer in single-owner files")
    output.append("   - Document decisions in high-complexity areas")
    output.append("   - Encourage pair programming for critical hotspots")
    output.append("")
    output.append("4. Continuous Monitoring:")
    output.append("   - Track whether changes increase or decrease metrics")
    output.append("   - Celebrate complexity reductions")
    output.append("   - Monitor churn patterns for early warning signs")
    output.append("")

    output.append("=" * 100)
    output.append("Report generated by MetricMancer, based on 'Your Code as a Crime Scene' methodology")
    output.append("=" * 100)
    return output


def _format_review_report(recommendations: List[ReviewRecommendation],
                          is_filtered: bool = False,
                          branch_name: Optional[str] = None,
                          base_branch: Optional[str] = None) -> str:
    """Format recommendations into a readable text report."""
    output = []

    # Header
    output.extend(_format_txt_header(is_filtered, branch_name, base_branch))

    # Executive Summary
    output.extend(_format_txt_summary(recommendations))

    # Priority-based recommendations
    priority_labels = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM"}
    for priority, label in priority_labels.items():
        output.extend(_format_txt_priority_section(recommendations, priority, label))

    # Example review template
    critical_files = [r for r in recommendations if r.risk_level == "critical"]
    if critical_files:
        output.append("EXAMPLE REVIEW TEMPLATE (for critical files)")
        output.append("-" * 100)
        output.append(critical_files[0].template)
        output.append("")

    # Resource allocation
    output.extend(_format_txt_resource_allocation(recommendations))

    # Best practices
    output.extend(_format_txt_best_practices())

    return "\n".join(output)
