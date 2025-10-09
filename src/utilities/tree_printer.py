

"""
TreePrinter utility for printing directory trees.
"""


class TreePrinter:

    def __init__(self, debug_print=None):
        self.debug_print = debug_print or (lambda *a, **k: None)

    def build_tree(self, paths):
        import os
        # Normalize all paths once before sorting and building the tree
        normalized_paths = [(os.path.normpath(path), stats) for path, stats in paths]
        sorted_paths = self._sort_paths(normalized_paths, os)
        tree = {}
        for norm_path, stats in sorted_paths:
            parts = norm_path.split(os.sep)
            node = tree
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = stats
        return tree

    def _sort_paths(self, paths, os):
        """Sort: files directly in root first, then folders, both alphabetically."""
        direct_files = (item for item in paths if os.sep not in item[0])
        sub_files = (item for item in paths if os.sep in item[0])
        return (
            sorted(direct_files, key=lambda x: x[0].lower()) + sorted(sub_files, key=lambda x: x[0].lower())
        )

    def print_tree(self, node, prefix="", is_last=True):
        files, folders = self._split_files_folders(node)
        files_sorted = self._sort_items(files)
        folders_sorted = self._sort_items(folders)
        items = files_sorted + folders_sorted
        for idx, (name, value) in enumerate(items):
            connector = "└── " if idx == len(items) - 1 else "├── "
            if isinstance(value, dict):
                print(f"{prefix}{connector}{name}")
                extension = "    " if idx == len(items) - 1 else "│   "
                self.print_tree(value, prefix + extension, is_last=(idx == len(items) - 1))
            else:
                print(f"{prefix}{connector}{name} {value}")

    def _split_files_folders(self, node):
        files = (
            (name, value) for name, value in node.items() if not isinstance(value, dict)
        )
        folders = (
            (name, value) for name, value in node.items() if isinstance(value, dict)
        )
        return list(files), list(folders)

    def _sort_items(self, items):
        return sorted(items, key=lambda x: x[0].lower())
