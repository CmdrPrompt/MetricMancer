"""
Hotspot analysis utility for identifying high-risk files based on complexity and churn metrics.
Based on "Your Code as a Crime Scene" methodology by Adam Tornhill.
"""

from typing import List, Tuple, Dict, Any


def extract_hotspots_from_data(data: Dict[str, Any], threshold: int = 50, path: str = '') -> List[Tuple[str, int, int, float]]:
    """
    Extract hotspots from hierarchical report data.
    
    Args:
        data: Report data dictionary (from JSON report)
        threshold: Minimum hotspot score to include
        path: Current path prefix for files
        
    Returns:
        List of tuples: (file_path, hotspot_score, complexity, churn)
    """
    hotspots = []
    
    if isinstance(data, dict):
        # Process files in current directory
        if 'files' in data:
            for filename, filedata in data['files'].items():
                file_path = f"{path}/{filename}" if path else filename
                if 'kpis' in filedata and 'hotspot' in filedata['kpis']:
                    hotspot = filedata['kpis']['hotspot']
                    if hotspot >= threshold:
                        complexity = filedata['kpis'].get('complexity', 0)
                        churn = filedata['kpis'].get('churn', 0)
                        hotspots.append((file_path, hotspot, complexity, churn))
        
        # Process subdirectories recursively
        if 'scan_dirs' in data:
            for dirname, dirdata in data['scan_dirs'].items():
                dir_path = f"{path}/{dirname}" if path else dirname
                hotspots.extend(extract_hotspots_from_data(dirdata, threshold, dir_path))
    
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
    output.append("Legend: Hotspot = Complexity × Churn | C = Complexity | Ch = Churn (commits/month)")
    output.append("=" * 100)
    
    return "\n".join(output)


def save_hotspots_to_file(hotspots: List[Tuple[str, int, int, float]], 
                         filename: str, 
                         show_risk_categories: bool = True) -> None:
    """
    Save hotspot analysis to a file.
    
    Args:
        hotspots: List of hotspot tuples
        filename: Output filename
        show_risk_categories: Whether to include risk category analysis
    """
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
    
    print(f"\nHOTSPOT SUMMARY:")
    print(f"   Total hotspots found: {total_count}")
    print(f"   Critical hotspots: {critical_count}")
    
    if critical_count > 0:
        print(f"   {critical_count} files need immediate attention!")
    else:
        print(f"   No critical hotspots found.")