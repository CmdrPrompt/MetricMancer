import unittest
import os
from src.main import get_output_filename, ensure_report_folder

class Args:
    def __init__(self, report_filename=None, with_date=False, auto_report_filename=False, directories=None, report_folder=None):
        self.report_filename = report_filename
        self.with_date = with_date
        self.auto_report_filename = auto_report_filename
        self.directories = directories or ['src']
        self.report_folder = report_folder

class TestMainHelpers(unittest.TestCase):
    def test_get_output_filename_default(self):
        args = Args()
        self.assertEqual(get_output_filename(args), 'complexity_report.html')

    def test_get_output_filename_report_filename(self):
        args = Args(report_filename='custom.html')
        self.assertEqual(get_output_filename(args), 'custom.html')

    def test_get_output_filename_report_filename_with_date(self):
        args = Args(report_filename='custom.html', with_date=True)
        result = get_output_filename(args)
        self.assertTrue(result.startswith('custom_'))
        self.assertTrue(result.endswith('.html'))
        self.assertGreater(len(result), len('custom.html'))

    def test_get_output_filename_auto_report_filename(self):
        args = Args(auto_report_filename=True, directories=['src', 'tests'])
        result = get_output_filename(args)
        self.assertTrue(result.startswith('complexity_report_src_tests_'))
        self.assertTrue(result.endswith('.html'))

    def test_ensure_report_folder_none(self):
        self.assertIsNone(ensure_report_folder(None))

    def test_ensure_report_folder_creates(self):
        folder = 'test_reports_folder'
        try:
            result = ensure_report_folder(folder)
            self.assertEqual(result, folder)
            self.assertTrue(os.path.isdir(folder))
        finally:
            if os.path.isdir(folder):
                os.rmdir(folder)

if __name__ == '__main__':
    unittest.main()
