#!/usr/bin/env python3
"""
Main script for the Legal Text Filter for TTS Optimization.

This script demonstrates the full workflow of the application:
1. Loading a legal document
2. Filtering out citations
3. Cleaning the text using NLP
4. Preparing the text for TTS
5. Saving or outputting the results
"""

import argparse
import os
import sys
from typing import Dict, Optional
import traceback

from input_handler import load_text, save_text
from citation_filter import filter_citations
from nlp_cleaner import clean_text
from tts_preparator import prepare_for_tts


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process legal documents for TTS optimization"
    )
    
    parser.add_argument(
        "--input-file", 
        type=str, 
        help="Path to input legal document (supports TXT, RTF, and RTFD formats)"
    )
    
    parser.add_argument(
        "--output-file", 
        type=str, 
        help="Path to save the processed output (if not specified, prints to stdout)"
    )
    
    parser.add_argument(
        "--citation-strategy", 
        type=str, 
        choices=["remove", "replace"],
        default="remove",
        help="Strategy for handling citations (remove or replace)"
    )
    
    parser.add_argument(
        "--citation-placeholder", 
        type=str, 
        default="[CITATION]",
        help="Placeholder text when using replace strategy"
    )
    
    parser.add_argument(
        "--spacy-model", 
        type=str, 
        default="en_core_web_sm",
        help="spaCy model to use for NLP processing"
    )
    
    parser.add_argument(
        "--remove-stopwords", 
        action="store_true",
        help="Remove stopwords during text cleaning"
    )
    
    parser.add_argument(
        "--keep-punctuation", 
        action="store_true",
        help="Keep punctuation during text cleaning"
    )
    
    parser.add_argument(
        "--skip-jargon-removal",
        action="store_true",
        help="Skip legal jargon removal step"
    )
    
    parser.add_argument(
        "--skip-sentence-optimization",
        action="store_true",
        help="Skip sentence boundary optimization step"
    )
    
    parser.add_argument(
        "--skip-tts-preparation",
        action="store_true",
        help="Skip final TTS preparation step"
    )
    
    parser.add_argument(
        "--remove-digits",
        action="store_true",
        help="Remove all digits (0-9) from the final output"
    )
    
    parser.add_argument(
        "--remove-urls",
        action="store_true",
        help="Remove all URLs (links starting with https:) from the final output"
    )
    
    parser.add_argument(
        "--use-dictionary-filter",
        action="store_true",
        help="Apply dictionary filtering to keep only recognized words (removes URLs, citations, etc.)"
    )
    
    parser.add_argument(
        "--ssml-output", 
        action="store_true",
        help="Format output as SSML (Speech Synthesis Markup Language)"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true",
        help="Print processing statistics"
    )
    
    parser.add_argument(
        "--input-text", 
        type=str,
        help="Process text provided directly as argument (instead of a file)"
    )
    
    parser.add_argument(
        "--custom-dictionary", 
        type=str,
        help="Path to a custom dictionary file (one word per line)"
    )
    
    parser.add_argument(
        "--skip-nlp-cleaning",
        action="store_true",
        help="Skip the NLP cleaning step that can negatively affect tokenization"
    )
    
    return parser.parse_args()


def main() -> int:
    """
    Main entry point for the application.
    """
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Process legal text to optimize for TTS by filtering citations and other elements.'
    )
    parser.add_argument('--input-file', help='Path to the input file containing legal text')
    parser.add_argument('--output-file', help='Path to save the processed output (if not specified, prints to console)')
    parser.add_argument('--citation-strategy', choices=['remove', 'replace'], default='remove',
                        help='Strategy for handling citations: remove them entirely or replace with a placeholder')
    parser.add_argument('--remove-digits', action='store_true',
                        help='Remove all numeric digits (0-9) from the final output')
    parser.add_argument('--remove-urls', action='store_true',
                        help='Remove all URLs from the final output')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose output')
    parser.add_argument('--use-dictionary-filter', action='store_true',
                        help='Apply dictionary filtering to keep only recognized words')
    parser.add_argument('--custom-dictionary', 
                        help='Path to a custom dictionary file (one word per line)')
    parser.add_argument('--skip-nlp-cleaning', action='store_true',
                        help='Skip the NLP cleaning step that can negatively affect tokenization')
    
    args = parser.parse_args()
    
    # If no input file specified, print help and exit
    if not args.input_file:
        parser.print_help()
        return 1
    
    # Process the text
    try:
        raw_text = load_text(args.input_file)
        
        if args.verbose:
            print(f"Successfully loaded text from {args.input_file}")
        
        # Apply the processing pipeline
        # 1. Filter citations
        citation_filtered_text = filter_citations(raw_text, strategy=args.citation_strategy)
        
        if args.verbose:
            print("Citations filtered.")
        
        # 2. Apply NLP cleaning (if not skipped)
        if args.skip_nlp_cleaning:
            nlp_cleaned_text = citation_filtered_text
            if args.verbose:
                print("NLP cleaning skipped.")
        else:
            nlp_cleaned_text = clean_text(citation_filtered_text)
            if args.verbose:
                print("NLP cleaning applied (removing legal jargon, etc.).")
        
        # 3. Prepare for TTS - apply final optimizations
        final_text = prepare_for_tts(
            nlp_cleaned_text, 
            remove_digits=args.remove_digits,
            remove_urls=args.remove_urls,
            use_dictionary_filter=args.use_dictionary_filter,
            custom_dictionary_path=args.custom_dictionary
        )
        
        if args.verbose:
            print("TTS preparation complete.")
        
        # Output the result
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(final_text)
            if args.verbose:
                print(f"Output saved to {args.output_file}")
        else:
            print(final_text)
        
    except Exception as e:
        print(f"Error processing text: {e}")
        if args.verbose:
            traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 