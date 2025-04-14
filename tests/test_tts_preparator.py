"""
Tests for the tts_preparator module.
"""
import unittest

from tts_preparator import (
    prepare_for_tts,
    expand_abbreviations,
    normalize_numeric_text,
    ensure_sentence_pauses,
    finalize_tts_text,
    create_ssml_output
)


class TestTTSPreparator(unittest.TestCase):
    """Test cases for the tts_preparator module."""
    
    def test_prepare_for_tts(self):
        """Test preparing text for TTS with all options enabled."""
        text = "The dates are 12/25/2023 and 1/1/2024. Dr. Smith et al. published a paper."
        abbreviations = {"Dr.": "Doctor", "et al.": "and others"}
        
        result = prepare_for_tts(
            text,
            abbreviation_dict=abbreviations,
            normalize_numbers=True,
            add_sentence_pauses=True
        )
        
        # Dates should be normalized
        self.assertIn("December", result)
        self.assertIn("January", result)
        
        # Abbreviations should be expanded
        self.assertIn("Doctor", result)
        self.assertIn("and others", result)
    
    def test_expand_abbreviations(self):
        """Test expanding abbreviations to their full forms."""
        text = "The U.S.A. is a country. NASA is an agency. Dr. Lee is a Ph.D."
        abbreviations = {
            "U.S.A.": "United States of America",
            "NASA": "National Aeronautics and Space Administration",
            "Dr.": "Doctor",
            "Ph.D.": "Doctor of Philosophy"
        }
        
        result = expand_abbreviations(text, abbreviations)
        
        # Abbreviations should be expanded
        self.assertIn("United States of America", result)
        self.assertIn("National Aeronautics and Space Administration", result)
        self.assertIn("Doctor", result)
        self.assertIn("Doctor of Philosophy", result)
        
        # Original abbreviations should be replaced
        self.assertNotIn("U.S.A.", result)
        self.assertNotIn("Dr.", result)
        self.assertNotIn("Ph.D.", result)
    
    def test_normalize_numeric_text(self):
        """Test normalizing numeric expressions in text."""
        text = "Sections 1-5 explain the concept. See § 123.45 for details."
        result = normalize_numeric_text(text)
        
        # Number ranges should be normalized
        self.assertIn("1 to 5", result)
        
        # Section symbols should be expanded
        self.assertIn("Section 123 point 45", result)
        
        # Original formats should be replaced
        self.assertNotIn("1-5", result)
        self.assertNotIn("§ 123.45", result)
    
    def test_normalize_dates(self):
        """Test normalizing date formats."""
        text = "The event is on 12/25/2023."
        result = normalize_numeric_text(text)
        
        # Date should be normalized to month name format
        self.assertIn("December 25, 2023", result)
        self.assertNotIn("12/25/2023", result)
    
    def test_ensure_sentence_pauses(self):
        """Test ensuring proper sentence boundaries."""
        text = "This is a sentence This is another The end"
        result = ensure_sentence_pauses(text)
        
        # Should end with a period
        self.assertTrue(result.endswith('.'))
        
        text_with_punct = "First sentence.Second sentence"
        result_with_punct = ensure_sentence_pauses(text_with_punct)
        
        # Should add space after period
        self.assertIn(". Second", result_with_punct)
    
    def test_finalize_tts_text(self):
        """Test finalizing text for TTS."""
        text = "This has  multiple   spaces!!!"
        result = finalize_tts_text(text)
        
        # Multiple spaces should be normalized
        self.assertNotIn("  ", result)
        
        # Multiple punctuation should be reduced
        self.assertNotIn("!!!", result)
        self.assertIn("!", result)
    
    def test_create_ssml_output(self):
        """Test creating SSML formatted output."""
        text = "First sentence. Second sentence. Third sentence."
        result = create_ssml_output(text, add_breaks=True)
        
        # Output should be wrapped in SSML speak tags
        self.assertTrue(result.startswith('<speak>'))
        self.assertTrue(result.endswith('</speak>'))
        
        # Should have break tags
        self.assertIn('<break strength="medium"/>', result)
    
    def test_create_ssml_escape_xml(self):
        """Test that XML special characters are escaped in SSML."""
        text = "This & that <tag> and \"quotes\" with 'apostrophes'."
        result = create_ssml_output(text)
        
        # Special characters should be escaped
        self.assertIn("&amp;", result)
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertIn("&quot;", result)
        self.assertIn("&apos;", result)
        
        # Original special characters should be replaced
        self.assertNotIn(" & ", result)
        self.assertNotIn("<tag>", result)


if __name__ == '__main__':
    unittest.main() 