#!/usr/bin/env python3
"""
Demonstration script for the Legal Text Filter for TTS Optimization.

This script provides a simple demonstration of the enhanced text processing
capabilities, particularly showing the effects of sentence boundary optimization
and the integrated processing pipeline.
"""

import sys
from input_handler import load_text
from text_processor import process_legal_text
from nlp_cleaner import optimize_sentence_boundaries, load_spacy_model


def display_processing_comparison(text):
    """Display the text before and after different processing steps."""
    print("\n" + "=" * 80)
    print("LEGAL TEXT PROCESSING DEMONSTRATION")
    print("=" * 80)
    
    # Show original text
    print("\nORIGINAL TEXT:")
    print("-" * 50)
    print(text[:500] + "..." if len(text) > 500 else text)
    print("-" * 50)
    
    # Show citation filtering only
    print("\nAFTER CITATION FILTERING:")
    print("-" * 50)
    citation_filtered = process_legal_text(
        text,
        citation_strategy="remove",
        clean_legal_jargon=False,
        optimize_sentences=False,
        prepare_tts_text=False,
        verbose=False
    )
    print(citation_filtered[:500] + "..." if len(citation_filtered) > 500 else citation_filtered)
    print("-" * 50)
    
    # Show sentence boundary optimization
    print("\nAFTER SENTENCE BOUNDARY OPTIMIZATION:")
    print("-" * 50)
    nlp = load_spacy_model()
    optimized = optimize_sentence_boundaries(citation_filtered, model=nlp)
    print(optimized[:500] + "..." if len(optimized) > 500 else optimized)
    print("-" * 50)
    
    # Show fully processed text
    print("\nFULLY PROCESSED TEXT:")
    print("-" * 50)
    fully_processed = process_legal_text(text, verbose=False)
    print(fully_processed[:500] + "..." if len(fully_processed) > 500 else fully_processed)
    print("-" * 50)
    
    # Show statistics
    print("\nSTATISTICS:")
    print("-" * 50)
    print(f"Original word count: {len(text.split())}")
    print(f"Citation filtered word count: {len(citation_filtered.split())}")
    print(f"Sentence optimized word count: {len(optimized.split())}")
    print(f"Fully processed word count: {len(fully_processed.split())}")
    
    citation_reduction = len(text.split()) - len(citation_filtered.split())
    citation_percent = (citation_reduction / len(text.split()) * 100) if len(text.split()) > 0 else 0
    print(f"Citation filtering reduced text by {citation_reduction} words ({citation_percent:.1f}%)")
    
    total_reduction = len(text.split()) - len(fully_processed.split())
    total_percent = (total_reduction / len(text.split()) * 100) if len(text.split()) > 0 else 0
    print(f"Full processing reduced text by {total_reduction} words ({total_percent:.1f}%)")
    print("-" * 50)


def main():
    """Main function to run the demonstration."""
    if len(sys.argv) > 1:
        # Use provided file
        try:
            text = load_text(sys.argv[1])
        except ValueError as e:
            print(f"Error loading file: {e}", file=sys.stderr)
            return 1
    else:
        # Use example text
        text = """
        IN THE SUPREME COURT OF THE UNITED STATES
        
        JOHN DOE, Petitioner,
        v.
        JANE SMITH, et al., Respondents.
        
        On the morning of January 15, 2020, Officer Williams received an anonymous call. 
        In Terry v. Ohio, 392 U.S. 1 (1968), this Court established that a police officer may, 
        consistent with the Fourth Amendment, conduct a brief investigatory stop. When Officer 
        Williams arrived at the location, he observed petitioner, John Doe, sitting in a parked vehicle. 
        Relying on Carroll v. United States, 267 U.S. 132 (1925), and its progeny, including 
        United States v. Ross, 456 U.S. 798 (1982), Officer Williams approached the vehicle.
        The suspect was subsequently charged with possession.The Court of Appeals affirmed,
        holding that the search was constitutional under the principles established in Arizona v. Gant,
        556 U.S. 332 (2009).It is well established that searches conducted outside the judicial process,
        without prior approval by judge or magistrate,are per se unreasonable under the Fourth Amendment
        subject only to a few specifically established and well-delineated exceptions.
        One such exception is the so-called "automobile exception," first recognized in Carroll v. United States,
        267 U.S. 132 (1925).The question we must address is whether an anonymous tip, without more,
        establishes the probable cause necessary to justify a warrantless search under the automobile exception.
        """
    
    display_processing_comparison(text)
    return 0


if __name__ == "__main__":
    sys.exit(main()) 