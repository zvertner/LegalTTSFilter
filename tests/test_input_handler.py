"""
Tests for the input_handler module.
"""
import os
import tempfile
import unittest
from pathlib import Path

from input_handler import load_text, save_text


class TestInputHandler(unittest.TestCase):
    """Test cases for the input_handler module."""
    
    def test_load_text_from_string(self):
        """Test loading text directly from a string."""
        text = "This is sample text."
        result = load_text(text)
        self.assertEqual(result, text)
    
    def test_load_text_from_file(self):
        """Test loading text from a file."""
        test_content = "This is test content from a file."
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_path = temp_file.name
        
        try:
            # Test loading using string path
            result = load_text(temp_path)
            self.assertEqual(result, test_content)
            
            # Test loading using Path object
            result = load_text(Path(temp_path))
            self.assertEqual(result, test_content)
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_load_text_from_filelike(self):
        """Test loading text from a file-like object."""
        test_content = "This is test content from a file-like object."
        
        # Create a file-like object (StringIO would work too)
        with tempfile.TemporaryFile(mode='w+') as temp_file:
            temp_file.write(test_content)
            temp_file.seek(0)  # Reset position to start
            
            # Test loading
            result = load_text(temp_file)
            self.assertEqual(result, test_content)
    
    def test_save_text(self):
        """Test saving text to a file."""
        test_content = "This is content to save."
        
        # Create a temporary file path (but don't create the file)
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save text to the file
            save_text(test_content, temp_path)
            
            # Verify the content was saved correctly
            with open(temp_path, 'r') as f:
                saved_content = f.read()
            
            self.assertEqual(saved_content, test_content)
        finally:
            # Clean up if the file exists
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main() 