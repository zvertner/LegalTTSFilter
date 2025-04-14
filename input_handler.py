"""
Module for loading legal text from files or other sources.

This module provides functions to load legal text data from different 
sources like files, strings, or potentially other input formats.
"""
from pathlib import Path
import os
import sys
from typing import Union, Optional, TextIO

# Import striprtf for RTF conversion if available
try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    rtf_to_text = None


def process_rtfd(rtfd_path: Union[str, Path]) -> str:
    """
    Extract and process text from an RTFD document bundle.
    
    Args:
        rtfd_path: Path to the RTFD directory bundle
        
    Returns:
        The extracted plain text from the RTFD document
        
    Raises:
        ValueError: If the path is not a valid RTFD bundle or TXT.rtf not found
        ImportError: If striprtf package is not installed
    """
    if rtf_to_text is None:
        raise ImportError(
            "The striprtf package is required for RTFD support. "
            "Install it with: pip install striprtf"
        )
    
    path = Path(rtfd_path)
    
    # Check if the path is an RTFD directory
    if not path.is_dir() or not str(path).lower().endswith('.rtfd'):
        raise ValueError(f"{rtfd_path} is not a valid RTFD document bundle")
    
    # The main RTF content is typically in a file named TXT.rtf inside the bundle
    rtf_file_path = path / 'TXT.rtf'
    
    if not rtf_file_path.exists():
        raise ValueError(f"Could not find TXT.rtf in {rtfd_path}")
    
    # Read the RTF content
    with open(rtf_file_path, 'r', encoding='utf-8', errors='ignore') as file:
        rtf_content = file.read()
    
    # Convert RTF to plain text
    plain_text = rtf_to_text(rtf_content)
    
    return plain_text


def load_text(source: Union[str, Path, TextIO]) -> str:
    """
    Load legal text from a file path, Path object, or file-like object.
    If a string that is not a valid file path is provided, it is treated as the text content.
    Supports TXT, RTF, and RTFD formats.
    
    Args:
        source: The source of the legal text, which can be:
               - A string file path
               - A Path object
               - A file-like object with a read method
               - Raw text content as a string
    
    Returns:
        The loaded text as a string
        
    Raises:
        ValueError: If the source is a file path that doesn't exist or can't be read
        ImportError: If required packages for certain formats are not installed
    """
    # If source is a file-like object with a read method
    if hasattr(source, 'read') and callable(source.read):
        return source.read()
    
    # If source is a Path object or string path, try to open and read the file
    path = Path(source) if isinstance(source, (str, Path)) else None
    
    if path and path.exists():
        # Handle RTFD directories
        if path.is_dir() and str(path).lower().endswith('.rtfd'):
            return process_rtfd(path)
        
        # Handle regular files
        if path.is_file():
            # Handle different file formats
            if path.suffix.lower() == '.rtf':
                if rtf_to_text is None:
                    raise ImportError(
                        "The striprtf package is required for RTF support. "
                        "Install it with: pip install striprtf"
                    )
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        rtf_content = file.read()
                    return rtf_to_text(rtf_content)
                except Exception as e:
                    raise ValueError(f"Failed to process RTF file at {path}: {str(e)}")
            else:
                # Default handling for text files
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        return file.read()
                except Exception as e:
                    raise ValueError(f"Failed to read file at {path}: {str(e)}")
    
    # If source is a string but not a valid file path, treat it as the text content
    if isinstance(source, str):
        return source
    
    raise ValueError(
        f"Invalid source: {source}. Expected a file path, Path object, "
        "file-like object, or text content as a string."
    )


def save_text(text: str, output_file: Union[str, Path, TextIO]) -> None:
    """
    Save text to a file.
    
    Args:
        text: The text content to save
        output_file: The path where the text should be saved, or a file-like object
    
    Raises:
        ValueError: If the output_file path is invalid or can't be written to
    """
    # If output_file is a file-like object with a write method
    if hasattr(output_file, 'write') and callable(output_file.write):
        output_file.write(text)
        return
    
    # Otherwise, treat as a file path
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(text)
    except Exception as e:
        raise ValueError(f"Failed to write to {output_file}: {str(e)}") 