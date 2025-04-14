#!/usr/bin/env python3
"""
Script to test the dictionary filter functionality on a test case file.
"""
import os
import time
from tts_preparator import apply_dictionary_filter

def main():
    """Run the dictionary filter test and report results."""
    print("Running dictionary filter test...")
    start_time = time.time()
    
    # Load the test case
    print("Loading test case...")
    with open('TestCase_no_nlp.txt', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    original_size = len(content)
    print(f"Original content: {original_size} characters, {len(content.split())} words")
    
    # Apply the enhanced dictionary filter
    print("Applying dictionary filter...")
    filtered = apply_dictionary_filter(content)
    
    # Save the filtered result
    output_file = 'TestCase_new_dict_filtered.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(filtered)
    
    filtered_size = len(filtered)
    
    # Report results
    processing_time = time.time() - start_time
    print(f"Filtering completed in {processing_time:.2f} seconds")
    print(f"Output saved to: {output_file}")
    print(f"Filtered content: {filtered_size} characters, {len(filtered.split())} words")
    print(f"Reduction: {100 - (filtered_size / original_size * 100):.1f}%")
    
    # Compare with previous filters
    try:
        with open('TestCase_dict_filtered.txt', 'r', encoding='utf-8', errors='ignore') as f:
            old_filtered = f.read()
        with open('TestCase_legal_dict_filtered.txt', 'r', encoding='utf-8', errors='ignore') as f:
            legal_filtered = f.read()
            
        print(f"Old dictionary filter: {len(old_filtered.split())} words")
        print(f"Legal dictionary filter: {len(legal_filtered.split())} words")
        print(f"New enhanced filter: {len(filtered.split())} words")
        
        # Show examples of words retained in the new filter but not in the old one
        old_words = set(old_filtered.lower().split())
        new_words = set(filtered.lower().split())
        
        preserved_words = new_words - old_words
        if preserved_words:
            print("\nSample of legal terms preserved in the new filter that were not in the old filter:")
            sample = list(preserved_words)[:10]  # Show first 10 examples
            print(", ".join(sample))
            
        # Check URL removal
        if 'https' in filtered or 'scholar' in filtered:
            print("\nWARNING: URLs may still be present in the filtered text")
        else:
            print("\nURL filtering successful: No 'https' or 'scholar' text found in filtered output")
            
    except FileNotFoundError:
        print("Note: Could not find previous filter output files for comparison")
    
    # Show a sample of the filtered text
    print("\nSample of filtered text (first 300 characters):")
    print(filtered[:300] + "...")

if __name__ == "__main__":
    main() 