import unittest
from unittest.mock import patch, MagicMock
import tempfile
import os
from src.app.analyzer import Analyzer

class TestAnalyzerSharedOwnership(unittest.TestCase):
    def setUp(self):
        self.analyzer = Analyzer({'.py': {'name': 'python'}})
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        self.temp_file.write("def test(): pass")
        self.temp_file.close()
        
    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)

    @patch('src.app.analyzer.SharedOwnershipKPI')
    @patch('src.app.analyzer.CodeChurnAnalyzer')
    def test_analyzer_includes_shared_ownership_kpi(self, mock_churn_analyzer, mock_shared_ownership):
        """Test that analyzer includes SharedOwnershipKPI."""
        # Mock churn analyzer
        mock_churn_instance = MagicMock()
        mock_churn_instance.analyze.return_value = {}
        mock_churn_analyzer.return_value = mock_churn_instance
        
        # Mock shared ownership KPI
        mock_shared_ownership_instance = MagicMock()
        mock_shared_ownership_instance.name = "Shared Ownership"
        mock_shared_ownership_instance.value = {"num_significant_authors": 2}
        mock_shared_ownership.return_value = mock_shared_ownership_instance
        
        files = [{
            'path': self.temp_file.name,
            'ext': '.py',
            'root': os.path.dirname(self.temp_file.name)
        }]
        
        result = self.analyzer.analyze(files)
        
        # Verify SharedOwnershipKPI was called
        mock_shared_ownership.assert_called()
        
        # Verify shared ownership is in results
        repo_info = list(result.values())[0]
        file_obj = list(repo_info.files.values())[0]
        self.assertIn("Shared Ownership", file_obj.kpis)

    @patch('src.app.analyzer.SharedOwnershipKPI')
    @patch('src.app.analyzer.CodeChurnAnalyzer')
    def test_shared_ownership_exception_handling(self, mock_churn_analyzer, mock_shared_ownership):
        """Test that SharedOwnershipKPI exceptions are handled gracefully."""
        # Mock churn analyzer
        mock_churn_instance = MagicMock()
        mock_churn_instance.analyze.return_value = {}
        mock_churn_analyzer.return_value = mock_churn_instance
        
        # Make SharedOwnershipKPI raise an exception
        mock_shared_ownership.side_effect = Exception("Git not available")
        
        files = [{
            'path': self.temp_file.name,
            'ext': '.py',
            'root': os.path.dirname(self.temp_file.name)
        }]
        
        # Should not crash
        result = self.analyzer.analyze(files)
        
        # Should still have a repo result
        self.assertEqual(len(result), 1)
        repo_info = list(result.values())[0]
        file_obj = list(repo_info.files.values())[0]
        
        # Should have a fallback KPI with error
        self.assertIn("Shared Ownership", file_obj.kpis)
        kpi = file_obj.kpis["Shared Ownership"]
        self.assertIn("error", kpi.value)

if __name__ == '__main__':
    unittest.main()