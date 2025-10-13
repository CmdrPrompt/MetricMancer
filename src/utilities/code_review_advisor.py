"""
Code Review Advisor - Generates code review recommendations based on KPI metrics.
Based on "Your Code as a Crime Scene" methodology by Adam Tornhill.
"""

import os
from typing import Dict, List, Tuple, Any
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
                    hotspot: int, ownership_data: Dict[str, float] = None) -> ReviewRecommendation:
        """
        Analyze a single file and generate review recommendations.
        
        Args:
            file_path: Path to the file
            complexity: Cyclomatic complexity
            churn: Churn rate (commits/month)
            hotspot: Hotspot score (complexity × churn)
            ownership_data: Dict of author -> percentage
            
        Returns:
            ReviewRecommendation object
        """
        # Determine risk level and category
        risk_level, category = self._classify_risk(complexity, churn, hotspot)
        
        # Calculate ownership concentration
        ownership_type = self._analyze_ownership(ownership_data) if ownership_data else "unknown"
        
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
    
    def _analyze_ownership(self, ownership_data: Dict[str, float]) -> str:
        """Analyze ownership distribution."""
        if not ownership_data:
            return "unknown"
        
        max_ownership = max(ownership_data.values()) if ownership_data else 0
        num_authors = len(ownership_data)
        
        if max_ownership >= 70:
            return "single_owner"
        elif max_ownership < 40 and num_authors > 3:
            return "fragmented"
        elif num_authors >= 3:
            return "shared"
        else:
            return "balanced"
    
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
        
        if complexity > 15:
            focus_areas.append("Complexity Management")
            focus_areas.append("Code Simplification Opportunities")
            focus_areas.append("Error Handling Patterns")
        
        if churn > 10:
            focus_areas.append("Root Cause Analysis")
            focus_areas.append("Pattern Consistency")
            focus_areas.append("Technical Debt Assessment")
        
        if category == "critical_hotspot":
            focus_areas.append("Architectural Impact")
            focus_areas.append("Performance Implications")
            focus_areas.append("Test Coverage Adequacy")
        
        if ownership_type == "single_owner":
            focus_areas.append("Knowledge Transfer")
            focus_areas.append("Documentation Quality")
        elif ownership_type == "fragmented":
            focus_areas.append("API Consistency")
            focus_areas.append("Coordination Overhead")
        
        return focus_areas
    
    def _generate_checklist(self, complexity: int, churn: float, 
                           ownership_type: str) -> List[str]:
        """Generate review checklist items."""
        checklist = []
        
        if complexity > 15:
            checklist.extend([
                "Is the change adding unnecessary complexity?",
                "Can complex logic be extracted into smaller functions?",
                "Are edge cases properly handled?",
                "Is error handling comprehensive?",
                "Would this benefit from simplification?",
                "Are there clear unit tests for complex paths?"
            ])
        
        if churn > 10:
            checklist.extend([
                "Does this change follow established patterns in the file?",
                "Is this change addressing root cause or symptoms?",
                "Could this change reduce future churn?",
                "Are we introducing technical debt?",
                "Is the change scope appropriate?",
                "Do we need architectural discussion before proceeding?"
            ])
        
        if ownership_type == "single_owner":
            checklist.extend([
                "Is documentation clear enough for new contributors?",
                "Should we involve additional team members for knowledge transfer?",
                "Are design decisions explained?",
                "Could this be an opportunity for pair programming?"
            ])
        elif ownership_type == "fragmented":
            checklist.extend([
                "Does this change affect module interfaces?",
                "Do we need broader team consultation?",
                "Are we maintaining API compatibility?",
                "Should this trigger integration testing?",
                "Do other teams need to be notified?"
            ])
        
        if not checklist:
            checklist.extend([
                "Does this change maintain code quality standards?",
                "Are tests adequate?",
                "Is documentation updated if needed?"
            ])
        
        return checklist
    
    def _generate_template(self, risk_level: str, complexity: int, churn: float,
                          ownership_type: str, file_path: str) -> str:
        """Generate a review comment template."""
        template_parts = []
        
        # Header based on risk level
        if risk_level == "critical":
            template_parts.append(f"🔥 CRITICAL HOTSPOT ALERT: {file_path}")
            template_parts.append(f"   Complexity: {complexity} | Churn: {churn:.1f} commits/month")
            template_parts.append("")
        elif risk_level == "high":
            template_parts.append(f"⚠️  HIGH RISK AREA: {file_path}")
            template_parts.append(f"   Complexity: {complexity} | Churn: {churn:.1f} commits/month")
            template_parts.append("")
        
        # Ownership context
        if ownership_type == "single_owner":
            template_parts.append("📚 KNOWLEDGE SHARING OPPORTUNITY: Single owner detected")
            template_parts.append("   - Consider involving additional reviewers for knowledge transfer")
            template_parts.append("   - Document design decisions clearly")
            template_parts.append("")
        elif ownership_type == "fragmented":
            template_parts.append("👥 HIGH COORDINATION: Multiple active contributors")
            template_parts.append("   - Ensure API consistency across changes")
            template_parts.append("   - Consider broader team discussion if needed")
            template_parts.append("")
        
        # Specific recommendations
        template_parts.append("Review Focus:")
        
        if complexity > 15:
            template_parts.append("   □ Complexity: Can logic be simplified or extracted?")
            template_parts.append("   □ Testing: Comprehensive coverage for complex paths?")
        
        if churn > 10:
            template_parts.append("   □ Patterns: Following established conventions?")
            template_parts.append("   □ Root Cause: Addressing underlying issues?")
        
        if risk_level in ["critical", "high"]:
            template_parts.append("   □ Architecture: Discuss impact before merge")
            template_parts.append("   □ Performance: Consider performance implications")
        
        template_parts.append("")
        template_parts.append("Action Required:")
        
        if risk_level == "critical":
            template_parts.append("   ⚡ Mandatory architecture review")
            template_parts.append("   ⚡ Minimum 2 approvals required")
            template_parts.append("   ⚡ Comprehensive test coverage verification")
        elif risk_level == "high":
            template_parts.append("   ⚠️  Senior developer review recommended")
            template_parts.append("   ⚠️  Consider refactoring opportunities")
        else:
            template_parts.append("   ✓ Standard review process")
        
        return "\n".join(template_parts)
    
    def _estimate_review_time(self, complexity: int, churn: float, risk_level: str) -> int:
        """Estimate review time in minutes."""
        base_time = 15  # Base review time
        
        # Add time based on complexity
        if complexity > 50:
            base_time += 60
        elif complexity > 20:
            base_time += 30
        elif complexity > 10:
            base_time += 15
        
        # Add time based on churn
        if churn > 15:
            base_time += 20
        elif churn > 10:
            base_time += 10
        
        # Add time based on risk level
        if risk_level == "critical":
            base_time += 30
        elif risk_level == "high":
            base_time += 15
        
        return base_time


def generate_review_report(data: Dict[str, Any], output_file: str = None, 
                          filter_files: List[str] = None, 
                          branch_name: str = None,
                          base_branch: str = None) -> str:
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
            ownership_data=file_info.get('ownership')
        )
        recommendations.append(rec)
    
    # Sort by priority
    recommendations.sort(key=lambda x: (x.priority, -x.estimated_time_minutes))
    
    # Generate report
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
                
                files.append({
                    'path': file_path,
                    'complexity': kpis.get('complexity', 0),
                    'churn': kpis.get('churn', 0),
                    'hotspot': kpis.get('hotspot', 0),
                    'ownership': ownership
                })
        
        if 'scan_dirs' in data:
            for dirname, dirdata in data['scan_dirs'].items():
                dir_path = f"{path}/{dirname}" if path else dirname
                files.extend(_extract_files_from_data(dirdata, dir_path))
    
    return files


def _format_review_report(recommendations: List[ReviewRecommendation], 
                         is_filtered: bool = False,
                         branch_name: str = None,
                         base_branch: str = None) -> str:
    """Format recommendations into a readable report."""
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
    
    # Executive Summary
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
    
    # Priority-based recommendations
    for priority in [1, 2, 3]:
        priority_recs = [r for r in recommendations if r.priority == priority]
        if not priority_recs:
            continue
        
        priority_label = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM"}
        output.append(f"{priority_label[priority]} PRIORITY FILES (Priority {priority})")
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
    
    # Example review template
    if critical_files:
        output.append("EXAMPLE REVIEW TEMPLATE (for critical files)")
        output.append("-" * 100)
        output.append(critical_files[0].template)
        output.append("")
    
    # Resource allocation guidance
    output.append("RESOURCE ALLOCATION GUIDANCE")
    output.append("-" * 100)
    output.append("")
    output.append("Recommended Review Time Distribution:")
    
    critical_time = sum(r.estimated_time_minutes for r in critical_files)
    high_time = sum(r.estimated_time_minutes for r in high_files)
    
    if total_time > 0:
        output.append(f"   Critical files: {critical_time}m ({critical_time * 100 // total_time}% of total time)")
        output.append(f"   High priority: {high_time}m ({high_time * 100 // total_time}% of total time)")
    
    output.append("")
    output.append("Reviewer Assignment Strategy:")
    output.append("   - Critical files: Senior architect + 2 experienced developers")
    output.append("   - High priority: Senior developer + peer reviewer")
    output.append("   - Medium/Low: Standard peer review")
    output.append("")
    
    # Best practices
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
    output.append("Report generated based on 'Your Code as a Crime Scene' methodology")
    output.append("=" * 100)
    
    return "\n".join(output)
