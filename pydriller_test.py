
from pydriller import Repository
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python pydriller_test.py <repo_path>")
        sys.exit(1)
    repo_path = sys.argv[1]
    for commit in Repository(repo_path).traverse_commits():
        print(f"Commit: {commit.hash}")
        for mod in commit.modified_files:
            added = len(mod.diff_parsed['added']) if hasattr(mod, 'diff_parsed') else 'N/A'
            removed = len(mod.diff_parsed['deleted']) if hasattr(mod, 'diff_parsed') else 'N/A'
            print(f"  Modified: {mod.filename} | new_path: {mod.new_path} | old_path: {mod.old_path} | added: {added} | removed: {removed}")

if __name__ == "__main__":
    main()
