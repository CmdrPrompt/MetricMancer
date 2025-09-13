import os
from src.utilities.debug import debug_print

def find_git_repo_root(start_path: str) -> str:
    """
    Hittar roten på ett git-repository genom att gå uppåt i filsystemet
    från en given startpunkt och leta efter en .git-mapp.

    Args:
        start_path: Sökvägen att börja leta från.

    Returns:
        Den absoluta sökvägen till git-repots rot, eller den ursprungliga
        start_path om inget .git-repo hittas.
    """
    current = os.path.abspath(start_path)
    while True:
        if os.path.isdir(os.path.join(current, '.git')):
            debug_print(f"[DEBUG] find_git_repo_root: Found .git at {current}")
            return current
        parent = os.path.dirname(current)
        if parent == current:  # Har nått filsystemets rot
            debug_print(f"[DEBUG] find_git_repo_root: No .git found. Returning original path {start_path}")
            return os.path.abspath(start_path) # Fallback
        current = parent