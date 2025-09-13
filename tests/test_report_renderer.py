import unittest
from unittest.mock import patch, MagicMock
from src.report.report_renderer import ReportRenderer

class TestReportRenderer(unittest.TestCase):
    def setUp(self):
        self.template_dir = 'src/templates'
        self.template_file = 'report.html'
        self.renderer = ReportRenderer(template_dir=self.template_dir, template_file=self.template_file)

    @patch('src.report.report_renderer.Environment.get_template')
    def test_render(self, mock_get_template):
        # Mock the template rendering process
        mock_template = MagicMock()
        mock_get_template.return_value = mock_template

        structured = 'structured_data'
        problem_roots = 'problematic_roots'
        mock_template.render.return_value = 'rendered_html'

        result = self.renderer.render(
            structured, 
            problem_roots, 
            problem_file_threshold=5.0, 
            threshold_low=8.0, 
            threshold_high=18.0
        )

        mock_get_template.assert_called_once_with(self.template_file)
        # Accept extra argument report_links (could be present or not)
        args, kwargs = mock_template.render.call_args
        assert kwargs['structured'] == 'structured_data'
        assert kwargs['problem_roots'] == 'problematic_roots'
        assert kwargs['threshold_low'] == 8.0
        assert kwargs['threshold_high'] == 18.0
        assert kwargs['problem_file_threshold'] == 5.0
        # Accept report_links if present
        if 'report_links' in kwargs:
            # Accept None or list
            assert kwargs['report_links'] is None or isinstance(kwargs['report_links'], list)
        self.assertEqual(result, 'rendered_html')

if __name__ == '__main__':
    unittest.main()