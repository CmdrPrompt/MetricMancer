"""
Tests for FormatMapper

Tests format to extension and base name mappings.
"""
import unittest
from src.app.coordination.format_mapper import FormatMapper


class TestFormatMapper(unittest.TestCase):
    """Test FormatMapper functionality."""
    
    def test_get_extension_simple_formats(self):
        """Test extension retrieval for simple formats."""
        self.assertEqual(FormatMapper.get_extension('json'), '.json')
        self.assertEqual(FormatMapper.get_extension('machine'), '.csv')
        self.assertEqual(FormatMapper.get_extension('html'), '.html')
    
    def test_get_extension_non_simple_format(self):
        """Test extension retrieval for non-simple formats."""
        self.assertIsNone(FormatMapper.get_extension('summary'))
        self.assertIsNone(FormatMapper.get_extension('quick-wins'))
        self.assertIsNone(FormatMapper.get_extension('unknown'))
    
    def test_get_cli_base_name_valid(self):
        """Test CLI base name retrieval for valid formats."""
        self.assertEqual(FormatMapper.get_cli_base_name('summary'), 'summary_report')
        self.assertEqual(FormatMapper.get_cli_base_name('quick-wins'), 'quick_wins_report')
        self.assertEqual(FormatMapper.get_cli_base_name('human-tree'), 'file_tree_report')
    
    def test_get_cli_base_name_invalid(self):
        """Test CLI base name retrieval for invalid formats."""
        self.assertIsNone(FormatMapper.get_cli_base_name('json'))
        self.assertIsNone(FormatMapper.get_cli_base_name('html'))
        self.assertIsNone(FormatMapper.get_cli_base_name('unknown'))
    
    def test_is_cli_format(self):
        """Test CLI format detection."""
        self.assertTrue(FormatMapper.is_cli_format('summary'))
        self.assertTrue(FormatMapper.is_cli_format('quick-wins'))
        self.assertTrue(FormatMapper.is_cli_format('human-tree'))
        self.assertFalse(FormatMapper.is_cli_format('json'))
        self.assertFalse(FormatMapper.is_cli_format('html'))
    
    def test_is_simple_format(self):
        """Test simple format detection."""
        self.assertTrue(FormatMapper.is_simple_format('json'))
        self.assertTrue(FormatMapper.is_simple_format('machine'))
        self.assertTrue(FormatMapper.is_simple_format('html'))
        self.assertFalse(FormatMapper.is_simple_format('summary'))
        self.assertFalse(FormatMapper.is_simple_format('quick-wins'))
    
    def test_is_review_strategy_format(self):
        """Test review strategy format detection."""
        self.assertTrue(FormatMapper.is_review_strategy_format('review-strategy'))
        self.assertTrue(FormatMapper.is_review_strategy_format('review-strategy-branch'))
        self.assertFalse(FormatMapper.is_review_strategy_format('json'))
        self.assertFalse(FormatMapper.is_review_strategy_format('summary'))


if __name__ == '__main__':
    unittest.main()
