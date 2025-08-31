import unittest
from unittest.mock import patch, MagicMock
from src.report.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        # Example data
        results = {
            'python': {
                'root1': [
                    {'path': 'file1.py', 'complexity': 15, 'functions': 3, 'grade': None},
                    {'path': 'file2.py', 'complexity': 7, 'functions': 2, 'grade': None},
                ],
                'root2': [
                    {'path': 'file3.py', 'complexity': 22, 'functions': 4, 'grade': None}
                ]
            }
        }
        class RepoInfo:
            pass
        self.repo_info = RepoInfo()
        self.repo_info.results = results

    @patch('src.report.report_generator.ReportDataCollector')
    @patch('src.report.report_generator.ReportDataAnalyzer')
    @patch('src.report.report_generator.ReportRenderer')
    @patch('src.report.report_generator.ReportWriter')
    def test_generate(self, MockReportWriter, MockReportRenderer, MockReportDataAnalyzer, MockReportDataCollector):
        # Mocking the external components
        mock_collector = MockReportDataCollector.return_value
        mock_collector.prepare_structured_data.return_value = 'structured_data'

        mock_analyzer = MockReportDataAnalyzer.return_value
        mock_analyzer.find_problematic_roots.return_value = 'problematic_roots'

        mock_renderer = MockReportRenderer.return_value
        mock_renderer.render.return_value = 'html_content'

        generator = ReportGenerator(self.repo_info)
        generator.generate(output_file='test_output.html')

        mock_collector.prepare_structured_data.assert_called_once()
        mock_analyzer.find_problematic_roots.assert_called_once()
        mock_renderer.render.assert_called_once_with(
            'structured_data',
            'problematic_roots',
            problem_file_threshold=None,
            threshold_low=10.0,
            threshold_high=20.0
        )
        MockReportWriter.write_html.assert_called_once_with('html_content', 'test_output.html')

if __name__ == '__main__':
    unittest.main()