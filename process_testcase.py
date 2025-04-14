#!/usr/bin/env python3
"""
Script to process TestCase.txt using the dictionary filter.
"""
import os
import time
from tts_preparator import apply_dictionary_filter

def main():
    """Process the TestCase.txt file and save the filtered output."""
    print("Processing TestCase.txt...")
    start_time = time.time()
    
    input_file = '/Users/zacharyzanevertner/Desktop/LegalTTSFilter/TestCase.txt'
    output_file = '/Users/zacharyzanevertner/Desktop/LegalTTSFilter/TestCase_new_filtered.txt'
    
    # Load the test case
    print(f"Loading file: {input_file}")
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_size = len(content)
    original_words = len(content.split())
    print(f"Original content: {original_size} characters, {original_words} words")
    
    # Apply the enhanced dictionary filter
    print("Applying dictionary filter...")
    filtered = apply_dictionary_filter(content)
    
    # Save the filtered result
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(filtered)
    
    filtered_size = len(filtered)
    filtered_words = len(filtered.split())
    
    # Report results
    processing_time = time.time() - start_time
    print(f"Processing completed in {processing_time:.2f} seconds")
    print(f"Output saved to: {output_file}")
    print(f"Filtered content: {filtered_size} characters, {filtered_words} words")
    print(f"Reduction: {100 - (filtered_size / original_size * 100):.1f}% by characters")
    print(f"Reduction: {100 - (filtered_words / original_words * 100):.1f}% by words")
    
    # Check URL removal
    if 'https' in filtered or 'scholar' in filtered:
        print("\nWARNING: URLs may still be present in the filtered text")
    else:
        print("\nURL filtering successful: No 'https' or 'scholar' text found in filtered output")
    
    # Show a sample of the filtered text
    print("\nSample of filtered text (first 500 characters):")
    print(filtered[:500] + "...")

if __name__ == "__main__":
    main() 