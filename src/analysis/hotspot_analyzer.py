"""
Hotspot analysis utility for identifying high-risk files based on complexity and churn metrics.
Based on "Your Code as a Crime Scene" methodology by Adam Tornhill.
"""

from typing import List, Tuple, Dict, Any


def _is_valid_hotspot(filedata: Dict[str, Any], threshold: int) -> bool:
    """
    Check if file data represents a valid hotspot.

    Args:
        filedata: File data dictionary
        threshold: Minimum hotspot score threshold

    Returns:
        True if file is a valid hotspot
    """
    return ('kpis' in filedata and
            'hotspot' in filedata['kpis'] and
            filedata['kpis']['hotspot'] >= threshold)


def _create_hotspot_tuple(file_path: str, filedata: Dict[str, Any]) -> Tuple[str, int, int, float]:
    """
    Create standardized hotspot tuple from file data.

    Args:
        file_path: Path to the file
        filedata: File data dictionary

    Returns:
        Tuple: (file_path, hotspot_score, complexity, churn)
    """
    hotspot = filedata['kpis']['hotspot']
    complexity = filedata['kpis'].get('complexity', 0)
    churn = filedata['kpis'].get('churn', 0)
    return (file_path, hotspot, complexity, churn)


def _extract_file_hotspots(data: Dict[str, Any], path: str, threshold: int) -> List[Tuple[str, int, int, float]]:
    """
    Extract hotspots from files in current directory.

    Args:
        data: Directory data dictionary
        path: Current path prefix
        threshold: Minimum hotspot score threshold

    Returns:
        List of hotspot tuples from files in current directory
    """
    hotspots = []
    if 'files' in data:
        for filename, filedata in data['files'].items():
            file_path = f"{path}/{filename}" if path else filename
            if _is_valid_hotspot(filedata, threshold):
                hotspots.append(_create_hotspot_tuple(file_path, filedata))
    return hotspots


def _extract_directory_hotspots(data: Dict[str, Any], path: str, threshold: int) -> List[Tuple[str, int, int, float]]:
    """
    Extract hotspots from subdirectories recursively.

    Args:
        data: Directory data dictionary
        path: Current path prefix
        threshold: Minimum hotspot score threshold

    Returns:
        List of hotspot tuples from all subdirectories
    """
    hotspots = []
    if 'scan_dirs' in data:
        for dirname, dirdata in data['scan_dirs'].items():
            dir_path = f"{path}/{dirname}" if path else dirname
            hotspots.extend(extract_hotspots_from_data(dirdata, threshold, dir_path))
    return hotspots


def extract_hotspots_from_data(data: Dict[str, Any], threshold: int = 50,
                               path: str = '') -> List[Tuple[str, int, int, float]]:
    """
    Extract hotspots from hierarchical report data.

    Args:
        data: Report data dictionary (from JSON report)
        threshold: Minimum hotspot score to include
        path: Current path prefix for files

    Returns:
        List of tuples: (file_path, hotspot_score, complexity, churn)
    """
    if not isinstance(data, dict):
        return []

    hotspots = []
    hotspots.extend(_extract_file_hotspots(data, path, threshold))
    hotspots.extend(_extract_directory_hotspots(data, path, threshold))
    return hotspots


def format_hotspots_table(hotspots: List[Tuple[str, int, int, float]],
                          show_risk_categories: bool = True) -> str:
    """
    Format hotspots as a readable table with risk categories.

    Args:
        hotspots: List of (file_path, hotspot_score, complexity, churn) tuples
        show_risk_categories: Whether to show risk category analysis

    Returns:
        Formatted string ready for display
    """
    if not hotspots:
        return "No hotspots found above the specified threshold."

    # Sort by hotspot score (highest first)
    sorted_hotspots = sorted(hotspots, key=lambda x: x[1], reverse=True)

    output = []
    output.append("=" * 100)
    output.append("HOTSPOT ANALYSIS - High Risk Files Requiring Attention")
    output.append("=" * 100)
    output.append("")

    # Add risk category analysis if requested
    if show_risk_categories:
        critical_hotspots = []
        emerging_hotspots = []
        stable_complexity = []

        for file_path, hotspot, complexity, churn in sorted_hotspots:
            if complexity > 15 and churn > 10:
                critical_hotspots.append((file_path, hotspot, complexity, churn))
            elif 5 <= complexity <= 15 and churn > 10:
                emerging_hotspots.append((file_path, hotspot, complexity, churn))
            elif complexity > 15 and churn <= 5:
                stable_complexity.append((file_path, hotspot, complexity, churn))

        if critical_hotspots:
            output.append("CRITICAL HOTSPOTS (Immediate Action Required)")
            output.append("   High Complexity (>15) + High Churn (>10)")
            output.append("   → Refactor into smaller functions, add comprehensive tests")
            output.append("")
            for file_path, hotspot, complexity, churn in critical_hotspots:
                output.append(f"   {file_path:<60} Hotspot: {hotspot:>6} (C:{complexity:>3}, Ch:{churn:>4.1f})")
            output.append("")

        if emerging_hotspots:
            output.append("EMERGING HOTSPOTS (High Priority)")
            output.append("   Medium Complexity (5-15) + High Churn (>10)")
            output.append("   → Monitor closely, preventive refactoring")
            output.append("")
            for file_path, hotspot, complexity, churn in emerging_hotspots:
                output.append(f"   {file_path:<60} Hotspot: {hotspot:>6} (C:{complexity:>3}, Ch:{churn:>4.1f})")
            output.append("")

        if stable_complexity:
            output.append("STABLE COMPLEXITY (Low Priority)")
            output.append("   High Complexity (>15) + Low Churn (≤5)")
            output.append("   → Document thoroughly, add integration tests")
            output.append("")
            for file_path, hotspot, complexity, churn in stable_complexity:
                output.append(f"   {file_path:<60} Hotspot: {hotspot:>6} (C:{complexity:>3}, Ch:{churn:>4.1f})")
            output.append("")

    # Legend before full table
    output.append("Legend: Hotspot = Complexity × Churn | C = Complexity | Ch = Churn (commits/month)")
    output.append("")

    # Interpretation guide
    output.append("INTERPRETATION GUIDE")
    output.append("-" * 100)
    output.append("")
    output.append("Hotspot Score Classification:")
    output.append("   0-25      Low Risk       → Monitor, no immediate action needed")
    output.append("   26-75     Medium Risk    → Plan improvements in next sprint")
    output.append("   76-150    High Risk      → Prioritize refactoring soon")
    output.append("   151+      Critical Risk  → Immediate action required")
    output.append("")
    output.append("Complexity Thresholds (McCabe Cyclomatic Complexity):")
    output.append("   1-5       Low            → Simple procedures, low risk")
    output.append("   6-10      Moderate       → Well-structured, monitor for growth")
    output.append("   11-15     High           → Consider refactoring")
    output.append("   16+       Very High      → Immediate attention, hard to test")
    output.append("")
    output.append("Code Churn Thresholds (commits/month):")
    output.append("   0-2       Stable         → Document and preserve")
    output.append("   3-5       Active         → Normal development pattern")
    output.append("   6-10      High Activity  → Monitor for instability")
    output.append("   11+       Very High      → Investigate root causes")
    output.append("")
    output.append("Recommended Actions by Category:")
    output.append("   Critical Hotspots     → Refactor into smaller functions, add comprehensive tests,")
    output.append("                            consider architectural redesign, assign senior dev ownership")
    output.append("   Emerging Hotspots     → Monitor closely, preventive refactoring, strengthen testing,")
    output.append("                            code reviews by experienced team members")
    output.append("   Stable Complexity     → Document thoroughly, add integration tests,")
    output.append("                            consider if refactoring adds value")
    output.append("   Active Simple Code    → Good pattern - ensure it stays simple")
    output.append("")
    output.append("Note: These thresholds are based on 'Your Code as a Crime Scene' by Adam Tornhill")
    output.append("      and industry research. Adjust based on your project context and domain.")
    output.append("-" * 100)
    output.append("")

    # Full table
    output.append("COMPLETE HOTSPOT LIST")
    output.append("-" * 100)
    output.append(f"{'File Path':<60} {'Hotspot':>8} {'Complexity':>12} {'Churn':>8}")
    output.append("-" * 100)
    for file_path, hotspot, complexity, churn in sorted_hotspots:
        output.append(f"{file_path:<60} {hotspot:>8} {complexity:>12} {churn:>8.1f}")
    output.append("-" * 100)
    output.append(f"Total files above threshold: {len(sorted_hotspots)}")
    output.append("")
    output.append("=" * 100)

    return "\n".join(output)


def _format_hotspots_markdown(hotspots: List[Tuple[str, int, int, float]],
                              show_risk_categories: bool = True) -> str:
    """
    Format hotspots as markdown with tables and emojis.

    Args:
        hotspots: List of (file_path, hotspot_score, complexity, churn) tuples
        show_risk_categories: Whether to show risk category analysis

    Returns:
        Formatted markdown string
    """
    if not hotspots:
        return "# 🔥 Hotspot Analysis\n\n**No hotspots found above the specified threshold.**\n"

    # Sort by hotspot score (highest first)
    sorted_hotspots = sorted(hotspots, key=lambda x: x[1], reverse=True)

    output = []
    output.append("# 🔥 Hotspot Analysis - High Risk Files\n")
    output.append("> *Generated by MetricMancer, based on 'Your Code as a Crime Scene' by Adam Tornhill*\n")
    output.append("> **Methodology:** Hotspot Score = Complexity × Churn\n")

    # Add risk category analysis if requested
    if show_risk_categories:
        critical_hotspots = []
        emerging_hotspots = []
        stable_complexity = []

        for file_path, hotspot, complexity, churn in sorted_hotspots:
            if complexity > 15 and churn > 10:
                critical_hotspots.append((file_path, hotspot, complexity, churn))
            elif 5 <= complexity <= 15 and churn > 10:
                emerging_hotspots.append((file_path, hotspot, complexity, churn))
            elif complexity > 15 and churn <= 5:
                stable_complexity.append((file_path, hotspot, complexity, churn))

        if critical_hotspots:
            output.append("\n## 🔴 Critical Hotspots (Immediate Action Required)\n")
            output.append("**Criteria:** High Complexity (>15) + High Churn (>10)\n")
            output.append("**Actions:** Refactor into smaller functions, add comprehensive tests\n")
            output.append("\n| File | Hotspot | Complexity | Churn |")
            output.append("|------|---------|------------|-------|")
            for file_path, hotspot, complexity, churn in critical_hotspots:
                output.append(f"| `{file_path}` | {hotspot} | {complexity} | {churn:.1f} |")

        if emerging_hotspots:
            output.append("\n## 🟡 Emerging Hotspots (High Priority)\n")
            output.append("**Criteria:** Medium Complexity (5-15) + High Churn (>10)\n")
            output.append("**Actions:** Monitor closely, preventive refactoring\n")
            output.append("\n| File | Hotspot | Complexity | Churn |")
            output.append("|------|---------|------------|-------|")
            for file_path, hotspot, complexity, churn in emerging_hotspots:
                output.append(f"| `{file_path}` | {hotspot} | {complexity} | {churn:.1f} |")

        if stable_complexity:
            output.append("\n## 🟢 Stable Complexity (Low Priority)\n")
            output.append("**Criteria:** High Complexity (>15) + Low Churn (≤5)\n")
            output.append("**Actions:** Document thoroughly, add integration tests\n")
            output.append("\n| File | Hotspot | Complexity | Churn |")
            output.append("|------|---------|------------|-------|")
            for file_path, hotspot, complexity, churn in stable_complexity:
                output.append(f"| `{file_path}` | {hotspot} | {complexity} | {churn:.1f} |")

    # Interpretation guide
    output.append("\n## 📊 Interpretation Guide\n")

    output.append("### Hotspot Score Classification\n")
    output.append("| Score Range | Risk Level | Action |")
    output.append("|-------------|------------|--------|")
    output.append("| 0-25 | 🟢 Low | Monitor, no immediate action |")
    output.append("| 26-75 | 🟡 Medium | Plan improvements in next sprint |")
    output.append("| 76-150 | 🟠 High | Prioritize refactoring soon |")
    output.append("| 151+ | 🔴 Critical | **Immediate action required** |")

    output.append("\n### Complexity Thresholds (McCabe Cyclomatic)\n")
    output.append("| Complexity | Level | Assessment |")
    output.append("|------------|-------|------------|")
    output.append("| 1-5 | Low | Simple procedures, low risk |")
    output.append("| 6-10 | Moderate | Well-structured, monitor growth |")
    output.append("| 11-15 | High | Consider refactoring |")
    output.append("| 16+ | Very High | **Immediate attention, hard to test** |")

    output.append("\n### Code Churn Thresholds (commits/month)\n")
    output.append("| Churn | Activity Level | Assessment |")
    output.append("|-------|----------------|------------|")
    output.append("| 0-2 | Stable | Document and preserve |")
    output.append("| 3-5 | Active | Normal development pattern |")
    output.append("| 6-10 | High Activity | Monitor for instability |")
    output.append("| 11+ | Very High | **Investigate root causes** |")

    output.append("\n### Recommended Actions by Category\n")
    output.append("| Category | Actions |")
    output.append("|----------|---------|")
    output.append("| 🔴 Critical Hotspots | Refactor into smaller functions, add comprehensive tests, " +
                  "consider architectural redesign, assign senior dev ownership |")
    output.append(
        "| 🟡 Emerging Hotspots | Monitor closely, preventive refactoring, strengthen testing, " +
        "code reviews by experienced team members |")
    output.append("| 🟢 Stable Complexity | Document thoroughly, add integration tests, "
                  "consider if refactoring adds value |")
    output.append("| ✅ Active Simple Code | Good pattern - ensure it stays simple |")

    # Full table
    output.append("\n## 📋 Complete Hotspot List\n")
    output.append("| File | Hotspot | Complexity | Churn |")
    output.append("|------|---------|------------|-------|")
    for file_path, hotspot, complexity, churn in sorted_hotspots:
        output.append(f"| `{file_path}` | {hotspot} | {complexity} | {churn:.1f} |")

    output.append(f"\n**Total files above threshold:** {len(sorted_hotspots)}\n")

    return "\n".join(output)


def save_hotspots_to_file(hotspots: List[Tuple[str, int, int, float]],
                          filename: str,
                          show_risk_categories: bool = True) -> None:
    """
    Save hotspot analysis to a file.
    Automatically detects format based on file extension (.md for markdown, .txt for plain text).

    Args:
        hotspots: List of hotspot tuples
        filename: Output filename (.md for markdown, .txt for plain text)
        show_risk_categories: Whether to include risk category analysis
    """
    # Auto-detect format based on file extension
    if filename.endswith('.md'):
        content = _format_hotspots_markdown(hotspots, show_risk_categories)
    else:
        content = format_hotspots_table(hotspots, show_risk_categories)

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Hotspot analysis saved to: {filename}")


def print_hotspots_summary(hotspots: List[Tuple[str, int, int, float]]) -> None:
    """
    Print a brief summary of hotspots to the terminal.

    Args:
        hotspots: List of hotspot tuples
    """
    if not hotspots:
        print("No high-risk hotspots found.")
        return

    critical_count = len([h for h in hotspots if h[2] > 15 and h[3] > 10])  # complexity > 15, churn > 10
    total_count = len(hotspots)

    print("\nHOTSPOT SUMMARY:")
    print(f"   Total hotspots found: {total_count}")
    print(f"   Critical hotspots: {critical_count}")

    if critical_count > 0:
        print("   Files need immediate attention!")
    else:
        print("   No critical hotspots found.")
