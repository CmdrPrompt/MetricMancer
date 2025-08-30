import argparse
from collector import collect_results
from report import generate_html_report

def main():
    parser = argparse.ArgumentParser(description="Analyze cyclomatic complexity")
    parser.add_argument("directories", nargs="+", help="Root folders to scan")
    parser.add_argument("--threshold", type=float, default=20.0,
                        help="Threshold for complexity (default: 20.0)")
    parser.add_argument("--problem-file-threshold", type=float, default=None,
                        help="Threshold for problem files (default: same as threshold)")
    import sys
    if len(sys.argv) == 1:
        print("\nUSAGE:")
        print("  python main.py <directories> --threshold <value> --problem-file-threshold <value>")
        print("\nPARAMETERS:")
        print("  <directories>                One or more root folders to scan for code complexity.")
        print("  --threshold                  Sets the threshold for average folder/root complexity. Folders above this value are highlighted in the summary.")
        print("  --problem-file-threshold     Sets the threshold for individual file complexity. Files above this value are listed under each problematic folder in the summary.")
        print("\nEXAMPLE:")
        print("  python main.py src test --threshold 20 --problem-file-threshold 15\n")
        sys.exit(0)
    args = parser.parse_args()

    results = collect_results(args.directories)
    generate_html_report(
        results,
        output_file='komplexitet_rapport.html',
        threshold=args.threshold,
        problem_file_threshold=args.problem_file_threshold
    )

if __name__ == "__main__":
    main()
