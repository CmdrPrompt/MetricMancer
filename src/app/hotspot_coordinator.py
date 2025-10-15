"""
Hotspot Coordinator Module

Handles hotspot analysis coordination and output formatting.
Separates hotspot-specific logic from main application flow.
"""
from typing import List, Dict, Any
import json


class HotspotCoordinator:
    """
    Coordinates hotspot analysis and formatting.
    
    Responsibilities:
    - Generate hotspot analysis
    - Format hotspot data for console output
    - Write hotspot data to files
    """
    
    @staticmethod
    def generate_hotspots(analyzer, config) -> List[Dict[str, Any]]:
        """
        Generate hotspot analysis from analyzer.
        
        Args:
            analyzer: Analyzer instance with KPI results
            config: Application configuration
            
        Returns:
            List of hotspot dictionaries
        """
        if not config.repo.analyze_hotspots:
            return []
        
        return analyzer.get_hotspots(
            complexity_threshold=config.repo.hotspot.complexity_threshold,
            churn_threshold=config.repo.hotspot.churn_threshold,
            complexity_weight=config.repo.hotspot.complexity_weight,
            churn_weight=config.repo.hotspot.churn_weight
        )
    
    @staticmethod
    def format_hotspots_text(hotspots: List[Dict[str, Any]]) -> str:
        """
        Format hotspots as human-readable text.
        
        Args:
            hotspots: List of hotspot dictionaries
            
        Returns:
            Formatted text representation
        """
        if not hotspots:
            return "No hotspots detected."
        
        lines = ["=== HOTSPOTS ==="]
        for h in hotspots:
            lines.append(
                f"- {h['file']} "
                f"(C:{h['complexity']}, Churn:{h['churn']}, Score:{h['score']:.2f})"
            )
        return "\n".join(lines)
    
    @staticmethod
    def write_hotspots_file(hotspots: List[Dict[str, Any]], output_path: str):
        """
        Write hotspots to text file.
        
        Args:
            hotspots: List of hotspot dictionaries
            output_path: Path to output file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(HotspotCoordinator.format_hotspots_text(hotspots))
            print(f"\n✅ Hotspots written to: {output_path}")
        except Exception as e:
            print(f"\n⚠️  Failed to write hotspots file: {e}")
    
    @staticmethod
    def write_hotspots_json(hotspots: List[Dict[str, Any]], output_path: str):
        """
        Write hotspots to JSON file.
        
        Args:
            hotspots: List of hotspot dictionaries
            output_path: Path to output JSON file
        """
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(hotspots, f, indent=2, ensure_ascii=False)
            print(f"✅ Hotspots JSON written to: {output_path}")
        except Exception as e:
            print(f"⚠️  Failed to write hotspots JSON: {e}")
    
    @staticmethod
    def print_hotspots(hotspots: List[Dict[str, Any]]):
        """
        Print hotspots to console.
        
        Args:
            hotspots: List of hotspot dictionaries
        """
        print("\n" + HotspotCoordinator.format_hotspots_text(hotspots))
