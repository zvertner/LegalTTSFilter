"""
Module for NLP-based text cleaning using spaCy.

This module leverages spaCy for text processing tasks like tokenization,
sentence boundary detection, and provides custom pipelines to simplify
legal text for TTS applications.
"""
import re
from typing import List, Dict, Union, Optional, Callable, Any
import spacy
from spacy.language import Language
from spacy.tokens import Doc, Token


def load_spacy_model(model_name: str = "en_core_web_sm") -> Language:
    """
    Load a spaCy language model.
    
    Args:
        model_name: Name of the spaCy model to load
        
    Returns:
        Loaded spaCy language model
        
    Raises:
        ValueError: If the model can't be loaded
    """
    try:
        return spacy.load(model_name)
    except OSError:
        raise ValueError(
            f"Model '{model_name}' not found. You may need to download it using: "
            f"python -m spacy download {model_name}"
        )


def clean_text(text: str, model: Union[str, Language] = "en_core_web_sm", 
               remove_stopwords: bool = True, 
               remove_punctuation: bool = True,
               normalize_whitespace: bool = True,
               custom_patterns: Optional[List[Dict]] = None) -> str:
    """
    Clean text using spaCy processing.
    
    Args:
        text: The legal text to clean
        model: spaCy language model name or loaded model instance
        remove_stopwords: Whether to remove stopwords
        remove_punctuation: Whether to remove punctuation
        normalize_whitespace: Whether to normalize whitespace
        custom_patterns: List of custom regex patterns to remove, each as a dict with 'pattern' and 'replacement' keys
        
    Returns:
        Cleaned text
    """
    # Load the spaCy model if a string is provided
    nlp = model if isinstance(model, Language) else load_spacy_model(model)
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Apply cleaning based on parameters
    cleaned_text = _apply_token_filters(doc, remove_stopwords, remove_punctuation)
    
    # Normalize whitespace if requested
    if normalize_whitespace:
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
    # Apply custom regex patterns if provided
    if custom_patterns:
        for pattern_info in custom_patterns:
            pattern = pattern_info['pattern']
            replacement = pattern_info.get('replacement', '')
            cleaned_text = re.sub(pattern, replacement, cleaned_text)
    
    return cleaned_text


def _apply_token_filters(doc: Doc, remove_stopwords: bool, remove_punctuation: bool) -> str:
    """
    Apply token-level filters based on specified parameters.
    
    Args:
        doc: spaCy Doc object
        remove_stopwords: Whether to remove stopwords
        remove_punctuation: Whether to remove punctuation
        
    Returns:
        Text with specified tokens removed
    """
    # Filter tokens based on criteria
    filtered_tokens = []
    for token in doc:
        # Skip token if it's a stopword and we're removing stopwords
        if remove_stopwords and token.is_stop:
            continue
            
        # Skip token if it's punctuation and we're removing punctuation
        if remove_punctuation and token.is_punct:
            continue
            
        # Add space before token if it's not punctuation or at the start
        if token.i > 0 and not doc[token.i-1].is_punct:
            filtered_tokens.append(' ')
            
        # Add the token text
        filtered_tokens.append(token.text)
    
    # Join and return the filtered tokens
    return ''.join(filtered_tokens).strip()


def remove_legal_jargon(text: str, model: Union[str, Language] = "en_core_web_sm",
                       jargon_list: Optional[List[str]] = None) -> str:
    """
    Remove common legal jargon and phrases that might disrupt TTS flow.
    
    Args:
        text: The legal text to process
        model: spaCy language model name or loaded model instance
        jargon_list: Optional list of additional jargon terms to remove
        
    Returns:
        Text with legal jargon removed or simplified
    """
    # Load the spaCy model if a string is provided
    nlp = model if isinstance(model, Language) else load_spacy_model(model)
    
    # Default list of legal jargon patterns to remove or simplify
    default_patterns = [
        # Remove Latin terms commonly used in legal documents
        {'pattern': r'\b(inter alia|prima facie|de facto|de jure|amicus curiae)\b', 'replacement': ''},
        # Remove procedural phrases
        {'pattern': r'\bhereinafter\s+referred\s+to\s+as\b', 'replacement': ''},
        # Remove common header/footer elements
        {'pattern': r'^\s*CONFIDENTIAL\s*$', 'replacement': ''},
        {'pattern': r'^\s*Page \d+ of \d+\s*$', 'replacement': ''},
        # Replace versus abbreviations
        {'pattern': r'\bv\.\s', 'replacement': ' versus '},
        # Remove parenthetical citations
        {'pattern': r'\([^)]*\d+\s*[A-Za-z\.]+\s*\d+[^)]*\)', 'replacement': ''},
    ]
    
    # Add user-provided jargon terms if any
    if jargon_list:
        pattern = r'\b(' + '|'.join(re.escape(term) for term in jargon_list) + r')\b'
        default_patterns.append({'pattern': pattern, 'replacement': ''})
    
    # Clean the text using the patterns
    return clean_text(text, model=nlp, custom_patterns=default_patterns)


def optimize_sentence_boundaries(text: str, model: Union[str, Language] = "en_core_web_sm") -> str:
    """
    Optimize text for TTS by enhancing sentence boundaries and structure.
    
    This function improves the text for TTS applications by:
    1. Ensuring proper sentence segmentation
    2. Adding appropriate punctuation for pauses
    3. Standardizing spacing between sentences
    
    Args:
        text: Text to optimize for TTS
        model: spaCy language model name or loaded model instance
        
    Returns:
        Text with optimized sentence boundaries for TTS
    """
    # Load the spaCy model if a string is provided
    nlp = model if isinstance(model, Language) else load_spacy_model(model)
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Extract sentences and clean them individually
    sentences = []
    for sent in doc.sents:
        # Get the sentence text and strip whitespace
        sent_text = sent.text.strip()
        
        # Skip empty sentences
        if not sent_text:
            continue
            
        # Ensure the sentence ends with appropriate punctuation
        if not sent_text[-1] in ['.', '!', '?']:
            sent_text += '.'
            
        # Add the cleaned sentence
        sentences.append(sent_text)
    
    # Join sentences with proper spacing
    result = ' '.join(sentences)
    
    # Normalize spacing around punctuation for better TTS parsing
    result = re.sub(r'\s+([.,;:!?])', r'\1', result)  # Remove space before punctuation
    result = re.sub(r'([.,;:!?])([^\s\d"])', r'\1 \2', result)  # Add space after punctuation
    
    return result


def create_custom_cleaner(cleaning_functions: List[Callable[[str], str]]) -> Callable[[str], str]:
    """
    Create a custom text cleaner by composing multiple cleaning functions.
    
    Args:
        cleaning_functions: List of cleaning functions to apply
        
    Returns:
        A function that applies all the specified cleaning functions in sequence
    """
    def custom_cleaner(text: str) -> str:
        result = text
        for func in cleaning_functions:
            result = func(result)
        return result
    
    return custom_cleaner 