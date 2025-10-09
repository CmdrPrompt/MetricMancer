import os
import sys
import unittest
from io import StringIO

from src.utilities.tree_printer import TreePrinter


class TestTreePrinter(unittest.TestCase):
    def setUp(self):
        self.printer = TreePrinter()

    def test_build_tree_single_file(self):
        paths = [("file.txt", {"size": 123})]
        tree = self.printer.build_tree(paths)
        self.assertIn("file.txt", tree)
        self.assertEqual(tree["file.txt"], {"size": 123})

    def test_build_tree_nested(self):
        paths = [("dir/file.txt", {"size": 1}), ("dir/sub/file2.txt", {"size": 2})]
        tree = self.printer.build_tree(paths)
        self.assertIn("dir", tree)
        self.assertIn("file.txt", tree["dir"])
        self.assertIn("sub", tree["dir"])
        self.assertIn("file2.txt", tree["dir"]["sub"])

    def test_sort_paths(self):
        paths = [("b.txt", {}), ("a.txt", {}), ("dir/c.txt", {}), ("dir/a.txt", {})]
        sorted_paths = self.printer._sort_paths(paths, os)
        self.assertEqual([p[0] for p in sorted_paths], ["a.txt", "b.txt", "dir/a.txt", "dir/c.txt"])

    def test_split_files_folders(self):
        node = {"file.txt": 1, "folder": {"a": 2}}
        files, folders = self.printer._split_files_folders(node)
        self.assertEqual(files, [("file.txt", 1)])
        self.assertEqual(folders, [("folder", {"a": 2})])

    def test_sort_items(self):
        items = [("b", 1), ("a", 2)]
        sorted_items = self.printer._sort_items(items)
        self.assertEqual(sorted_items, [("a", 2), ("b", 1)])

    def test_print_tree_output(self):
        node = {"file.txt": 1, "folder": {"a.txt": 2}}
        captured = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = captured
        try:
            self.printer.print_tree(node)
        finally:
            sys.stdout = sys_stdout
        output = captured.getvalue()
        self.assertIn("file.txt", output)
        self.assertIn("folder", output)
        self.assertIn("a.txt", output)


if __name__ == "__main__":
    unittest.main()
