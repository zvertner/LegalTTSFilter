"""
Tests for the nlp_cleaner module.
"""
import unittest
import pytest
import spacy

from nlp_cleaner import (
    load_spacy_model,
    clean_text,
    remove_legal_jargon,
    create_custom_cleaner
)


class TestNLPCleaner(unittest.TestCase):
    """Test cases for the nlp_cleaner module."""
    
    @classmethod
    def setUpClass(cls):
        """Load spaCy model once for all tests."""
        try:
            cls.nlp = spacy.load("en_core_web_sm")
        except OSError:
            pytest.skip("spaCy model 'en_core_web_sm' not available. Skipping tests.")
    
    def test_load_spacy_model(self):
        """Test loading a spaCy model."""
        try:
            model = load_spacy_model("en_core_web_sm")
            self.assertIsNotNone(model)
        except ValueError:
            self.skipTest("spaCy model 'en_core_web_sm' not available.")
    
    def test_clean_text_remove_stopwords(self):
        """Test cleaning text with stopword removal."""
        text = "The quick brown fox jumps over the lazy dog."
        result = clean_text(text, model=self.nlp, remove_stopwords=True)
        
        # The stopwords should be removed
        self.assertNotIn(" the ", result.lower())
        
        # Other content words should be preserved
        self.assertIn("quick", result.lower())
        self.assertIn("brown", result.lower())
        self.assertIn("fox", result.lower())
    
    def test_clean_text_remove_punctuation(self):
        """Test cleaning text with punctuation removal."""
        text = "Hello, world! This is a test."
        result = clean_text(text, model=self.nlp, remove_punctuation=True)
        
        # Punctuation should be removed
        self.assertNotIn(",", result)
        self.assertNotIn("!", result)
        self.assertNotIn(".", result)
        
        # Content should be preserved
        self.assertIn("Hello", result)
        self.assertIn("world", result)
        self.assertIn("test", result)
    
    def test_clean_text_normalize_whitespace(self):
        """Test cleaning text with whitespace normalization."""
        text = "This   has    multiple    spaces    and\ttabs\nand\nnewlines."
        result = clean_text(text, model=self.nlp, normalize_whitespace=True)
        
        # Multiple whitespace should be normalized to single spaces
        self.assertNotIn("  ", result)
        self.assertNotIn("\t", result)
        self.assertNotIn("\n", result)
    
    def test_clean_text_custom_patterns(self):
        """Test cleaning text with custom regex patterns."""
        text = "Email me at user@example.com or call at 123-456-7890."
        patterns = [
            {'pattern': r'\S+@\S+\.\S+', 'replacement': '[EMAIL]'},
            {'pattern': r'\d{3}-\d{3}-\d{4}', 'replacement': '[PHONE]'}
        ]
        
        result = clean_text(text, model=self.nlp, custom_patterns=patterns)
        
        # Email and phone number should be replaced
        self.assertNotIn("user@example.com", result)
        self.assertNotIn("123-456-7890", result)
        self.assertIn("[EMAIL]", result)
        self.assertIn("[PHONE]", result)
    
    def test_remove_legal_jargon(self):
        """Test removing legal jargon."""
        text = "The court ruled, inter alia, that the defendant was prima facie liable."
        result = remove_legal_jargon(text, model=self.nlp)
        
        # Latin terms should be removed
        self.assertNotIn("inter alia", result.lower())
        self.assertNotIn("prima facie", result.lower())
        
        # Other content should be preserved
        self.assertIn("court", result.lower())
        self.assertIn("ruled", result.lower())
    
    def test_create_custom_cleaner(self):
        """Test creating and using a custom cleaner function."""
        # Create simple cleaning functions
        def remove_numbers(text):
            import re
            return re.sub(r'\d+', '', text)
        
        def replace_names(text):
            import re
            return re.sub(r'\b(John|Jane)\b', '[NAME]', text)
        
        # Create a custom cleaner combining these functions
        custom_cleaner = create_custom_cleaner([remove_numbers, replace_names])
        
        # Test the custom cleaner
        text = "John called 5 times and Jane called 10 times."
        result = custom_cleaner(text)
        
        # Numbers should be removed
        self.assertNotIn("5", result)
        self.assertNotIn("10", result)
        
        # Names should be replaced
        self.assertNotIn("John", result)
        self.assertNotIn("Jane", result)
        self.assertIn("[NAME]", result)


if __name__ == '__main__':
    unittest.main() 