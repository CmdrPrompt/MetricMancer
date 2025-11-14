#!/usr/bin/env python3
"""
Clean MetricMancer output directory.
Removes all generated reports and analysis files.
"""

import os
import shutil
import argparse


def clean_output_directory(directory='output', dry_run=False):
    """
    Remove all files in the output directory.
    
    Args:
        directory: The output directory to clean (default: 'output')
        dry_run: If True, only show what would be deleted without actually deleting
    """
    if not os.path.exists(directory):
        print(f"✅ Directory '{directory}' does not exist. Nothing to clean.")
        return
    
    if dry_run:
        print(f"🔍 DRY RUN: Would remove the following from '{directory}':")
    else:
        print(f"🧹 Cleaning '{directory}' directory...")
    
    # Count files
    file_count = 0
    for root, dirs, files in os.walk(directory):
        file_count += len(files)
    
    if file_count == 0:
        print(f"✅ Directory '{directory}' is already empty.")
        return
    
    if dry_run:
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file != '.gitkeep':
                    filepath = os.path.join(root, file)
                    print(f"  - {filepath}")
    else:
        # Remove all contents except .gitkeep
        for item in os.listdir(directory):
            if item == '.gitkeep':
                continue
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
                print(f"  ✓ Removed: {item}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"  ✓ Removed directory: {item}")
        
        # Recalculate file count excluding .gitkeep
        actual_count = file_count - (1 if os.path.exists(os.path.join(directory, '.gitkeep')) else 0)
        print(f"\n✅ Cleaned {actual_count} files from '{directory}' directory.")


def main():
    parser = argparse.ArgumentParser(
        description='Clean MetricMancer output directory'
    )
    parser.add_argument(
        '--directory',
        type=str,
        default='output',
        help='Output directory to clean (default: output)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be deleted without actually deleting'
    )
    
    args = parser.parse_args()
    clean_output_directory(args.directory, args.dry_run)


if __name__ == '__main__':
    main()
