import unittest
import os
from src.report.report_writer import ReportWriter


class TestReportWriter(unittest.TestCase):
    def test_write_html_creates_file_and_writes_content(self):
        html = "<html><body>Test</body></html>"
        output_file = "test_report_writer_output.html"
        try:
            ReportWriter.write_html(html, output_file)
            self.assertTrue(os.path.exists(output_file))
            with open(output_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertEqual(content, html)
        finally:
            if os.path.exists(output_file):
                os.remove(output_file)


if __name__ == "__main__":
    unittest.main()
