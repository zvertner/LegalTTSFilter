"""
Tests for the citation_filter module.
"""
import unittest

from citation_filter import (
    identify_citations,
    filter_citations,
    get_citation_statistics
)


class TestCitationFilter(unittest.TestCase):
    """Test cases for the citation_filter module."""
    
    def test_identify_citations(self):
        """Test identifying citations in legal text."""
        # Test with a simple case citation
        text = "The Supreme Court's decision in Brown v. Board of Education, 347 U.S. 483 (1954), changed education law."
        citations = identify_citations(text)
        
        # We should find at least one citation
        self.assertGreater(len(citations), 0)
        
        # The citation should be correctly identified with span positions
        citation = citations[0]
        self.assertIn('span', citation)
        self.assertIn('text', citation)
        self.assertIn('347 U.S. 483', citation['text'])
    
    def test_filter_citations_remove(self):
        """Test removing citations from legal text."""
        text = "The case of Smith v. Jones, 123 F.3d 456 (7th Cir. 2000), is instructive."
        result = filter_citations(text, strategy="remove")
        
        # The citation should be removed
        self.assertNotIn("123 F.3d 456", result)
        
        # The text around the citation should be preserved
        self.assertIn("The case of Smith v. Jones", result)
        self.assertIn("is instructive", result)
    
    def test_filter_citations_replace(self):
        """Test replacing citations with a placeholder."""
        text = "According to Roe v. Wade, 410 U.S. 113 (1973), the right to privacy extends to abortion."
        placeholder = "[LEGAL_CITATION]"
        result = filter_citations(text, strategy="replace", placeholder=placeholder)
        
        # The citation should be replaced with the placeholder
        self.assertNotIn("410 U.S. 113", result)
        self.assertIn(placeholder, result)
        
        # The text around the citation should be preserved
        self.assertIn("According to Roe v. Wade", result)
        self.assertIn("the right to privacy extends to abortion", result)
    
    def test_filter_citations_invalid_strategy(self):
        """Test that an invalid strategy raises a ValueError."""
        text = "Some legal text with a citation."
        with self.assertRaises(ValueError):
            filter_citations(text, strategy="invalid_strategy")
    
    def test_get_citation_statistics(self):
        """Test getting statistics about citations in text."""
        text = """
        In Brown v. Board of Education, 347 U.S. 483 (1954), the Court overturned 
        Plessy v. Ferguson, 163 U.S. 537 (1896). This was cited again in 
        Parents Involved in Community Schools v. Seattle School District No. 1, 
        551 U.S. 701 (2007).
        """
        
        stats = get_citation_statistics(text)
        
        # Should find 3 citations
        self.assertEqual(stats['total_citations'], 3)
        
        # Should have citation type counts
        self.assertIn('citation_types', stats)
        
        # Should calculate citation density
        self.assertIn('citation_density', stats)
        self.assertGreater(stats['citation_density'], 0)


if __name__ == '__main__':
    unittest.main() 