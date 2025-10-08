
import unittest
from unittest.mock import MagicMock, patch
from src.report.report_renderer import ReportRenderer
from src.kpis.model import RepoInfo, ScanDir, File

class TestReportRenderer(unittest.TestCase):
    def setUp(self):
        self.template_dir = "src/report/templates"
        self.template_file = "report.html"
        self.renderer = ReportRenderer(self.template_dir, self.template_file, threshold_low=5, threshold_high=15)

    @patch("src.report.report_renderer.Environment")
    def test_init_sets_env_and_thresholds(self, MockEnv):
        renderer = ReportRenderer(self.template_dir, self.template_file, threshold_low=1, threshold_high=2)
        self.assertEqual(renderer.template_file, self.template_file)
        self.assertEqual(renderer.threshold_low, 1)
        self.assertEqual(renderer.threshold_high, 2)
        MockEnv.assert_called_once()

    def test_collect_all_files_nested(self):
        file1 = File(name="a.py", file_path="a.py")
        file2 = File(name="b.py", file_path="b.py")
        subdir = ScanDir(dir_name="sub", scan_dir_path="sub", repo_root_path=".", repo_name="repo", files={"b.py": file2})
        root = ScanDir(dir_name="root", scan_dir_path=".", repo_root_path=".", repo_name="repo", files={"a.py": file1}, scan_dirs={"sub": subdir})
        result = self.renderer._collect_all_files(root)
        self.assertIn(file1, result)
        self.assertIn(file2, result)
        self.assertEqual(len(result), 2)

    @patch("src.report.report_renderer.Environment")
    def test_render_filters_problem_files_and_renders(self, MockEnv):
        # Setup fake template
        mock_template = MagicMock()
        mock_template.render.return_value = "<html>report</html>"
        mock_env = MockEnv.return_value
        mock_env.get_template.return_value = mock_template
        # Setup files with complexity
        file1 = File(name="a.py", file_path="a.py", kpis={"complexity": MagicMock(value=10)})
        file2 = File(name="b.py", file_path="b.py", kpis={"complexity": MagicMock(value=20)})
        root = ScanDir(dir_name="root", scan_dir_path=".", repo_root_path=".", repo_name="repo", files={"a.py": file1, "b.py": file2})
        renderer = ReportRenderer(self.template_dir, self.template_file, threshold_low=5, threshold_high=15)
        renderer.env = mock_env
        html = renderer.render(root, problem_file_threshold=15, report_links=["link"])
        mock_env.get_template.assert_called_once_with(self.template_file)
        mock_template.render.assert_called_once()
        # Only file2 should be in problem_files
        args, kwargs = mock_template.render.call_args
        self.assertIn("problem_files", kwargs)
        self.assertEqual(kwargs["problem_files"], [file2])
        self.assertEqual(html, "<html>report</html>")

if __name__ == "__main__":
    unittest.main()
