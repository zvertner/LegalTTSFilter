"""
Module for filtering legal citations from text.

This module uses the eyecite library to identify and remove legal case citations,
with a focus on removing case names for better text-to-speech compatibility.
"""                                     
from typing import Dict, List, Optional, Tuple, Any
import re

# Import eyecite components
from eyecite import get_citations, annotate_citations
from eyecite.models import FullCaseCitation, ShortCaseCitation, SupraCitation, IdCitation


def identify_citations(text: str) -> List[Dict[str, Any]]:
    """
    Identify citations in text and return detailed information about them.
    
    This function enhances the eyecite library's citation detection with additional
    metadata and improved handling of case names. It detects both the citation
    and any associated case names that precede it.
    
    Args:
        text: The legal text to analyze
        
    Returns:
        List of citation dictionaries with span, text, and type information
    """
    if not text:
        return []
    
    try:
        # Get citations from eyecite
        citations = get_citations(text)
        
        # Convert to a more usable format with extra metadata
        result = []
        for citation in citations:
            # Skip citations without valid span information
            if not citation.span() or None in citation.span():
                continue
                
            start, end = citation.span()
            citation_text = text[start:end]
            
            # Get citation type
            if isinstance(citation, FullCaseCitation):
                citation_type = "full"
            elif isinstance(citation, ShortCaseCitation):
                citation_type = "short"
            elif isinstance(citation, SupraCitation):
                citation_type = "supra"
            elif isinstance(citation, IdCitation):
                citation_type = "id"
            else:
                citation_type = "unknown"
                
            # Extract case name if possible (looking at text before the citation)
            case_name = None
            case_name_span = None
            
            prefix_text = text[:start]
            
            # Multiple case name patterns
            case_patterns = [
                # Standard "Name v. Name" pattern - matches both single and multiple word names
                r'((?:[A-Z][a-zA-Z\']*(?:\s+[A-Z][a-zA-Z\']*)*)\s+(?:v\.?|vs\.?|versus)\s+(?:[A-Z][a-zA-Z\']*(?:\s+[A-Z][a-zA-Z\']*)*)),?\s*$',
                
                # Pattern for "In re Name" format
                r'(In\s+re\s+(?:[A-Z][a-zA-Z\']*(?:\s+[A-Z][a-zA-Z\']*)*)),?\s*$',
                
                # Pattern for "Ex parte Name" format
                r'(Ex\s+parte\s+(?:[A-Z][a-zA-Z\']*(?:\s+[A-Z][a-zA-Z\']*)*)),?\s*$',
                
                # Pattern for case name after phrases like "in the case of" or "the court in"
                r'(?:in|of|by|from|see|citing|in\s+the\s+case\s+of|the\s+court\s+in)\s+((?:[A-Z][a-zA-Z\']*(?:\s+[A-Z][a-zA-Z\']*)*)\s+(?:v\.?|vs\.?|versus)\s+(?:[A-Z][a-zA-Z\']*(?:\s+[A-Z][a-zA-Z\']*)*)),?\s*$'
            ]
            
            for pattern in case_patterns:
                match = re.search(pattern, prefix_text, re.IGNORECASE)
                if match:
                    case_name = match.group(1)
                    case_name_span = (match.start(1), match.end(1))
                    break
            
            # Create citation entry with all metadata
            citation_entry = {
                "span": (start, end),
                "text": citation_text,
                "type": citation_type,
                "case_name": case_name,
                "case_name_span": case_name_span,
                "original_citation": citation
            }
            
            result.append(citation_entry)
            
        return result
    
    except Exception as e:
        print(f"Error identifying citations: {e}")
        return []


def get_citation_statistics(text: str) -> Dict[str, Any]:
    """
    Collect comprehensive statistics about citations in the text.
    
    Args:
        text: The legal text to analyze
        
    Returns:
        Dictionary with citation statistics
    """
    if not text:
        return {"total_citations": 0}
    
    try:
        citations = get_citations(text)
        
        # Count by type
        full_citations = sum(1 for c in citations if isinstance(c, FullCaseCitation))
        short_citations = sum(1 for c in citations if isinstance(c, ShortCaseCitation))
        supra_citations = sum(1 for c in citations if isinstance(c, SupraCitation))
        id_citations = sum(1 for c in citations if isinstance(c, IdCitation))
        
        # Calculate citation density (citations per 1000 words)
        word_count = len(text.split())
        citation_density = (len(citations) / word_count) * 1000 if word_count > 0 else 0
        
        stats = {
            "total_citations": len(citations),
            "citation_types": {
                "full_case_citations": full_citations,
                "short_citations": short_citations,
                "supra_citations": supra_citations,
                "id_citations": id_citations
            },
            "citation_density": citation_density,
            "word_count": word_count
        }
        
        return stats
    except Exception as e:
        print(f"Error analyzing citations: {e}")
        return {"total_citations": 0, "error": str(e)}


def filter_citations(text: str, strategy: str = "remove", placeholder: str = "[CITATION]") -> str:
    """
    Filter citations from text using the specified strategy with enhanced case name detection.
    
    This function not only handles the citations themselves but can also detect and 
    remove or replace the case names that precede them, providing a cleaner output
    for text-to-speech applications.
    
    Args:
        text: The legal text to process
        strategy: Strategy for handling citations:
          - "remove": completely remove citations
          - "replace": replace with placeholder text
          - "remove_with_names": remove both citations and their case names
          - "names_only": remove only case names, keep citations
        placeholder: Placeholder text when using "replace" strategy
        
    Returns:
        Text with citations filtered according to the specified strategy
    """
    if not text:
        return ""
    
    # Validate strategy
    valid_strategies = ["remove", "replace", "remove_with_names", "names_only"]
    if strategy not in valid_strategies:
        raise ValueError(f"Invalid strategy '{strategy}'. Valid options are: {', '.join(valid_strategies)}")
    
    try:
        # Get detailed citation information using our enhanced identification
        citations = identify_citations(text)
        
        # Sort citations by their position in reverse order to avoid index shifting
        # during text modification
        citations.sort(key=lambda c: c["span"][0], reverse=True)
        
        # Process the text according to the chosen strategy
        result = text
        
        for citation in citations:
            citation_start, citation_end = citation["span"]
            case_name_span = citation["case_name_span"]
            
            # Apply the chosen strategy
            if strategy == "remove":
                # Remove just the citation
                result = result[:citation_start] + result[citation_end:]
                
            elif strategy == "replace":
                # Replace the citation with a placeholder
                result = result[:citation_start] + placeholder + result[citation_end:]
                
            elif strategy == "remove_with_names":
                # Remove both the citation and its case name if detected
                if case_name_span:
                    case_name_start, case_name_end = case_name_span
                    # First remove the citation
                    result = result[:citation_start] + result[citation_end:]
                    # Then remove the case name, adjusting for the removed citation
                    result = result[:case_name_start] + result[case_name_end:]
                else:
                    # Just remove the citation if no case name detected
                    result = result[:citation_start] + result[citation_end:]
                    
            elif strategy == "names_only":
                # Remove only the case name, keep the citation
                if case_name_span:
                    case_name_start, case_name_end = case_name_span
                    result = result[:case_name_start] + result[case_name_end:]
        
        # Clean up any resulting issues from citation removal
        # Remove double spaces
        result = re.sub(r'\s{2,}', ' ', result)
        # Fix any punctuation issues like ", ," or ". ."
        result = re.sub(r',\s*,', ',', result)
        result = re.sub(r'\.\s*\.', '.', result)
        # Fix any isolated parentheses that might remain
        result = re.sub(r'\(\s*\)', '', result)
        result = re.sub(r'\[\s*\]', '', result)
        
        return result
    
    except Exception as e:
        print(f"Error filtering citations: {e}")
        return text  # Return original text if an error occurs


def remove_case_names(text: str) -> str:
    """
    Remove case names from text while preserving the rest of the citation.
    
    Args:
        text: The legal text to process
        
    Returns:
        Text with case names removed but citation details preserved
    """
    return filter_citations(text, strategy="names_only")


def remove_case_citations(text: str) -> str:
    """
    Remove all case citations from the given text.
    
    This is a convenience function that calls filter_citations with remove strategy.
    
    Args:
        text: The legal text to process
        
    Returns:
        Text with case citations removed
    """
    return filter_citations(text, strategy="remove")


def replace_case_citations(text: str, placeholder: str = "[CITATION]") -> str:
    """
    Replace all case citations with a placeholder.
    
    This is a convenience function that calls filter_citations with replace strategy.
    
    Args:
        text: The legal text to process
        placeholder: Text to replace citations with
        
    Returns:
        Text with case citations replaced by the placeholder
    """
    return filter_citations(text, strategy="replace", placeholder=placeholder)


def remove_citations_with_names(text: str) -> str:
    """
    Remove both citations and their case names from the text.
    
    This function provides the most comprehensive citation cleaning for TTS,
    removing both the technical citation information and the case names.
    
    Args:
        text: The legal text to process
        
    Returns:
        Text with both case names and citations removed
    """
    return filter_citations(text, strategy="remove_with_names")


# Test case demonstrating functionality
if __name__ == "__main__":
    # Example legal text with various citation formats
    test_text = """
    The Supreme Court's decision in Brown v. Board of Education, 347 U.S. 483 (1954), 
    marked a turning point in American constitutional law. Later, in Roe v. Wade, 
    410 U.S. 113 (1973), the Court established a different precedent. The Court in 
    Citizens United v. Federal Election Commission, 558 U.S. 310 (2010), addressed 
    campaign finance. In parentheses (see Smith v. Jones, 123 F.3d 456 (2d Cir. 2000)).
    Reference with no space: Marbury v.Madison, 5 U.S. 137 (1803).
    """
    
    print("Original text:")
    print(test_text)
    print("\nCitation statistics:")
    stats = get_citation_statistics(test_text)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\nText with citations removed:")
    print(remove_case_citations(test_text))
    
    print("\nText with citations replaced:")
    print(replace_case_citations(test_text, "[LEGAL CITATION]"))
    
    print("\nText with only case names removed (citations preserved):")
    print(remove_case_names(test_text))
    
    print("\nText with both case names and citations removed:")
    print(remove_citations_with_names(test_text)) 