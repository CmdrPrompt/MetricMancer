import unittest
from unittest.mock import patch, MagicMock, mock_open
from src.report.report_generator import ReportGenerator

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        # Patch open and file existence for dummy files
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
        self.patcher_exists = patch('os.path.exists', return_value=True)
        self.patcher_open = patch('builtins.open', mock_open(read_data="dummy code"))
        self.patcher_exists.start()
        self.patcher_open.start()
        self.addCleanup(self.patcher_exists.stop)
        self.addCleanup(self.patcher_open.stop)

    @patch('src.report.html_report_format.ReportDataCollector')
    @patch('src.report.html_report_format.ReportDataAnalyzer')
    @patch('src.report.html_report_format.ReportRenderer')
    @patch('src.report.html_report_format.ReportWriter')
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
        # Accept extra argument report_links (could be present or not)
        args, kwargs = mock_renderer.render.call_args
        assert args[0] == 'structured_data'
        assert args[1] == 'problematic_roots'
        assert kwargs['problem_file_threshold'] == None
        assert kwargs['threshold_low'] == 10.0
        assert kwargs['threshold_high'] == 20.0
        # Accept report_links if present
        if 'report_links' in kwargs:
            assert isinstance(kwargs['report_links'], list)
        MockReportWriter.write_html.assert_called_once_with('html_content', 'test_output.html')

if __name__ == '__main__':
    unittest.main()