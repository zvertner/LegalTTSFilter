"""
Module for integrated legal text processing.

This module combines citation filtering and NLP cleaning in a single pipeline,
providing high-level functions for complete processing of legal documents for TTS.
"""
from typing import Dict, List, Optional, Union

from citation_filter import filter_citations, get_citation_statistics
from nlp_cleaner import (
    clean_text, 
    remove_legal_jargon, 
    optimize_sentence_boundaries, 
    load_spacy_model
)
from tts_preparator import prepare_for_tts


def process_legal_text(
    text: str,
    citation_strategy: str = "remove",
    citation_placeholder: str = "[CITATION]",
    spacy_model: str = "en_core_web_sm",
    remove_stopwords: bool = False,
    remove_punctuation: bool = False,
    clean_legal_jargon: bool = True,
    optimize_sentences: bool = True,
    prepare_tts_text: bool = True,
    abbreviation_dict: Optional[Dict[str, str]] = None,
    remove_digits: bool = False,
    remove_urls: bool = False,
    use_dictionary_filter: bool = False,
    verbose: bool = False
) -> str:
    """
    Complete processing pipeline for legal text optimized for TTS.
    
    This function provides an integrated pipeline that:
    1. Removes or replaces citations using eyecite
    2. Cleans text with spaCy NLP
    3. Removes legal jargon
    4. Optimizes sentence boundaries 
    5. Prepares the text for TTS systems
    
    Args:
        text: The legal text to process
        citation_strategy: Strategy for handling citations ("remove" or "replace")
        citation_placeholder: Placeholder text when using "replace" strategy
        spacy_model: Name of spaCy model to use
        remove_stopwords: Whether to remove stopwords
        remove_punctuation: Whether to remove punctuation
        clean_legal_jargon: Whether to remove common legal jargon
        optimize_sentences: Whether to optimize sentence boundaries
        prepare_tts_text: Whether to apply TTS-specific formatting
        abbreviation_dict: Dictionary of abbreviations to expand
        remove_digits: Whether to remove all digits (0-9) from the text
        remove_urls: Whether to remove URLs (links starting with https:) from the text
        use_dictionary_filter: Whether to use a dictionary filter
        verbose: Whether to print progress information
        
    Returns:
        Processed text ready for TTS
    """
    if not text:
        return ""
    
    result = text
    steps_completed = []
    
    # Step 1: Citation filtering with eyecite
    if verbose:
        print("Step 1: Filtering citations...")
        stats = get_citation_statistics(text)
        print(f"Found {stats['total_citations']} citations")
    
    result = filter_citations(
        result, 
        strategy=citation_strategy,
        placeholder=citation_placeholder
    )
    steps_completed.append("citation filtering")
    
    # Step 2: Basic NLP cleaning with spaCy
    if verbose:
        print("Step 2: Applying NLP cleaning...")
    
    result = clean_text(
        result,
        model=spacy_model,
        remove_stopwords=remove_stopwords,
        remove_punctuation=remove_punctuation
    )
    steps_completed.append("basic NLP cleaning")
    
    # Step 3: Remove legal jargon
    if clean_legal_jargon:
        if verbose:
            print("Step 3: Removing legal jargon...")
        
        result = remove_legal_jargon(result, model=spacy_model)
        steps_completed.append("legal jargon removal")
    
    # Step 4: Optimize sentence boundaries
    if optimize_sentences:
        if verbose:
            print("Step 4: Optimizing sentence boundaries...")
        
        result = optimize_sentence_boundaries(result, model=spacy_model)
        steps_completed.append("sentence boundary optimization")
    
    # Step 5: Prepare for TTS
    if prepare_tts_text:
        if verbose:
            print("Step 5: Preparing text for TTS...")
        
        # Default legal abbreviations if none provided
        if abbreviation_dict is None:
            abbreviation_dict = {
                "i.e.": "that is",
                "e.g.": "for example",
                "et al.": "and others",
                "etc.": "etcetera",
                "v.": "versus",
                "cf.": "compare",
                "id.": "the same"
            }
        
        result = prepare_for_tts(
            result,
            abbreviation_dict=abbreviation_dict,
            remove_digits=remove_digits,
            remove_urls=remove_urls,
            use_dictionary_filter=use_dictionary_filter
        )
        steps_completed.append("TTS preparation")
        
        if remove_digits:
            steps_completed.append("digit removal")
            
        if remove_urls:
            steps_completed.append("URL removal")
            
        if use_dictionary_filter:
            steps_completed.append("dictionary filtering")
    
    if verbose:
        print(f"Processing complete. Applied: {', '.join(steps_completed)}")
        
        # Calculate statistics
        original_words = len(text.split())
        final_words = len(result.split())
        reduction = original_words - final_words
        reduction_percent = (reduction / original_words * 100) if original_words > 0 else 0
        
        print(f"Word count: {original_words} → {final_words} ({reduction_percent:.1f}% reduction)")
    
    return result


def batch_process_legal_texts(
    texts: List[str],
    **kwargs
) -> List[str]:
    """
    Process multiple legal texts using the same parameters.
    
    Args:
        texts: List of legal texts to process
        **kwargs: Additional arguments to pass to process_legal_text
        
    Returns:
        List of processed texts
    """
    return [process_legal_text(text, **kwargs) for text in texts] 