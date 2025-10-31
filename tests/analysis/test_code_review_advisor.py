"""
Tests for code_review_advisor module.
"""

import unittest
from src.analysis.code_review_advisor import (
    CodeReviewAdvisor,
    generate_review_report
)


class TestCodeReviewAdvisor(unittest.TestCase):
    """Test cases for CodeReviewAdvisor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.advisor = CodeReviewAdvisor()

    def test_analyze_critical_hotspot(self):
        """Test analysis of critical hotspot file."""
        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=90,
            churn=20.0,
            hotspot=1800
        )

        self.assertEqual(rec.risk_level, "critical")
        self.assertEqual(rec.priority, 1)
        self.assertEqual(rec.reviewers_needed, 3)
        self.assertIn("Senior architect", rec.reviewer_rationale)
        self.assertIn("Complexity Management", rec.focus_areas)
        self.assertIn("Architectural Impact", rec.focus_areas)
        self.assertGreater(rec.estimated_time_minutes, 60)

    def test_analyze_emerging_hotspot(self):
        """Test analysis of emerging hotspot file."""
        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=12,
            churn=15.0,
            hotspot=180
        )

        self.assertEqual(rec.risk_level, "high")
        self.assertEqual(rec.priority, 2)
        self.assertGreaterEqual(rec.reviewers_needed, 2)
        self.assertIn("Senior developer", rec.reviewer_rationale)
        self.assertIn("Root Cause Analysis", rec.focus_areas)

    def test_analyze_stable_complexity(self):
        """Test analysis of stable complexity file."""
        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=25,
            churn=2.0,
            hotspot=50
        )

        self.assertEqual(rec.risk_level, "medium")
        self.assertIn("Complexity Management", rec.focus_areas)

    def test_analyze_low_risk(self):
        """Test analysis of low risk file."""
        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=3,
            churn=1.0,
            hotspot=3
        )

        self.assertEqual(rec.risk_level, "low")
        self.assertEqual(rec.priority, 4)
        self.assertEqual(rec.reviewers_needed, 1)
        self.assertIn("Standard peer review", rec.reviewer_rationale)

    def test_analyze_with_single_ownership(self):
        """Test analysis with single owner ownership pattern."""
        ownership_data = {
            "Alice": 85.0,
            "Bob": 10.0,
            "Charlie": 5.0
        }

        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=20,
            churn=5.0,
            hotspot=100,
            ownership_data=ownership_data
        )

        self.assertIn("Knowledge Transfer", rec.focus_areas)
        self.assertIn("Documentation Quality", rec.focus_areas)

    def test_analyze_with_fragmented_ownership(self):
        """Test analysis with fragmented ownership pattern."""
        ownership_data = {
            "Alice": 25.0,
            "Bob": 20.0,
            "Charlie": 20.0,
            "Dave": 20.0,
            "Eve": 15.0
        }

        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=15,
            churn=8.0,
            hotspot=120,
            ownership_data=ownership_data
        )

        self.assertIn("API Consistency", rec.focus_areas)
        self.assertIn("Coordination Overhead", rec.focus_areas)

    def test_checklist_for_high_complexity(self):
        """Test that high complexity generates appropriate checklist."""
        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=50,
            churn=5.0,
            hotspot=250
        )

        checklist_text = " ".join(rec.checklist_items).lower()
        self.assertIn("complexity", checklist_text)
        self.assertTrue("simplification" in checklist_text or "simplified" in checklist_text)

    def test_checklist_for_high_churn(self):
        """Test that high churn generates appropriate checklist."""
        rec = self.advisor.analyze_file(
            file_path="test_file.py",
            complexity=8,
            churn=15.0,
            hotspot=120
        )

        checklist_text = " ".join(rec.checklist_items)
        self.assertIn("root cause", checklist_text.lower())
        self.assertIn("technical debt", checklist_text.lower())

    def test_template_generation(self):
        """Test that template is generated correctly."""
        rec = self.advisor.analyze_file(
            file_path="critical_file.py",
            complexity=100,
            churn=25.0,
            hotspot=2500
        )

        self.assertIn("CRITICAL HOTSPOT ALERT", rec.template)
        self.assertIn("critical_file.py", rec.template)
        self.assertIn("Complexity: 100", rec.template)
        self.assertIn("Mandatory architecture review", rec.template)

    def test_time_estimation(self):
        """Test that time estimation increases with complexity and churn."""
        low_risk_rec = self.advisor.analyze_file(
            file_path="simple.py",
            complexity=3,
            churn=1.0,
            hotspot=3
        )

        high_risk_rec = self.advisor.analyze_file(
            file_path="complex.py",
            complexity=100,
            churn=25.0,
            hotspot=2500
        )

        self.assertLess(
            low_risk_rec.estimated_time_minutes,
            high_risk_rec.estimated_time_minutes
        )

    def test_reviewer_rationale_critical(self):
        """Test reviewer rationale for critical risk files."""
        rec = self.advisor.analyze_file(
            file_path="critical.py",
            complexity=60,
            churn=5.0,
            hotspot=300
        )

        self.assertEqual(rec.reviewers_needed, 3)
        self.assertIn("Senior architect", rec.reviewer_rationale)
        self.assertIn("2 reviewers", rec.reviewer_rationale)

    def test_reviewer_rationale_high_risk(self):
        """Test reviewer rationale for high risk files."""
        rec = self.advisor.analyze_file(
            file_path="high.py",
            complexity=25,
            churn=5.0,
            hotspot=125
        )

        self.assertEqual(rec.reviewers_needed, 2)
        self.assertIn("Senior developer", rec.reviewer_rationale)
        self.assertIn("peer reviewer", rec.reviewer_rationale)

    def test_reviewer_rationale_low_risk(self):
        """Test reviewer rationale for low risk files."""
        rec = self.advisor.analyze_file(
            file_path="low.py",
            complexity=5,
            churn=2.0,
            hotspot=10
        )

        self.assertEqual(rec.reviewers_needed, 1)
        self.assertIn("Standard peer review", rec.reviewer_rationale)


class TestGenerateReviewReport(unittest.TestCase):
    """Test cases for generate_review_report function."""

    def test_generate_report_with_sample_data(self):
        """Test report generation with sample data."""
        data = {
            'files': {
                'critical.py': {
                    'kpis': {
                        'complexity': 90,
                        'churn': 20,
                        'hotspot': 1800
                    },
                    'ownership': {
                        'Alice': 100.0
                    }
                },
                'simple.py': {
                    'kpis': {
                        'complexity': 3,
                        'churn': 1,
                        'hotspot': 3
                    },
                    'ownership': {
                        'Bob': 100.0
                    }
                }
            },
            'scan_dirs': {}
        }

        report = generate_review_report(data)

        # Verify report structure
        self.assertIn("CODE REVIEW STRATEGY REPORT", report)
        self.assertIn("EXECUTIVE SUMMARY", report)
        self.assertIn("critical.py", report)
        self.assertIn("CRITICAL", report)
        self.assertIn("BEST PRACTICES", report)

    def test_generate_report_with_nested_directories(self):
        """Test report generation with nested directory structure."""
        data = {
            'files': {},
            'scan_dirs': {
                'src': {
                    'files': {
                        'app.py': {
                            'kpis': {
                                'complexity': 50,
                                'churn': 10,
                                'hotspot': 500
                            }
                        }
                    },
                    'scan_dirs': {}
                }
            }
        }

        report = generate_review_report(data)

        self.assertIn("CODE REVIEW STRATEGY REPORT", report)
        self.assertIn("src/app.py", report)

    def test_report_prioritization(self):
        """Test that report prioritizes critical files first."""
        data = {
            'files': {
                'low_priority.py': {
                    'kpis': {'complexity': 3, 'churn': 1, 'hotspot': 3}
                },
                'critical.py': {
                    'kpis': {'complexity': 90, 'churn': 20, 'hotspot': 1800}
                }
            },
            'scan_dirs': {}
        }

        report = generate_review_report(data)

        # Critical file should appear in report
        critical_pos = report.find('critical.py')
        self.assertGreater(critical_pos, 0)

        # Report should contain CRITICAL priority section
        self.assertIn("CRITICAL PRIORITY FILES", report)


if __name__ == '__main__':
    unittest.main()
