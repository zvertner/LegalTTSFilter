"""
Module for preparing text for Text-to-Speech (TTS) systems.

This module handles final formatting of cleaned text to ensure
optimal compatibility with TTS engines.
"""
import re
import os
import string
from typing import Dict, List, Optional, Union, Set


def prepare_for_tts(text: str, abbreviation_dict: Optional[Dict[str, str]] = None,
                   normalize_numbers: bool = True, 
                   add_sentence_pauses: bool = True,
                   remove_digits: bool = False,
                   remove_urls: bool = False,
                   use_dictionary_filter: bool = False,
                   custom_dictionary_path: Optional[str] = None) -> str:
    """
    Prepare text for TTS by applying various optimizations.
    
    Args:
        text: The text to prepare for TTS
        abbreviation_dict: Optional dictionary mapping abbreviations to their expanded forms
        normalize_numbers: Whether to convert numbers to their word form
        add_sentence_pauses: Whether to ensure sentences have proper pause markers
        remove_digits: Whether to remove all digits (0-9) from the text
        remove_urls: Whether to remove URLs (links starting with https:) from the text
        use_dictionary_filter: Whether to use a dictionary filter to keep only recognized words
        custom_dictionary_path: Optional path to a custom dictionary file with one word per line
        
    Returns:
        Text optimized for TTS systems
    """
    result = text
    
    # Expand abbreviations if a dictionary is provided
    if abbreviation_dict:
        result = expand_abbreviations(result, abbreviation_dict)
    
    # Normalize numbers if requested
    if normalize_numbers:
        result = normalize_numeric_text(result)
    
    # Remove all digits if requested
    if remove_digits:
        result = remove_all_digits(result)
    
    # Remove URLs if requested
    if remove_urls:
        result = remove_all_urls(result)
    
    # Apply dictionary filter if requested - pass remove_digits to ensure consistency
    if use_dictionary_filter:
        result = apply_dictionary_filter(result, custom_dictionary_path, remove_digits)
    
    # Add appropriate pauses between sentences if requested
    if add_sentence_pauses:
        result = ensure_sentence_pauses(result)
    
    # Final cleanup
    result = finalize_tts_text(result)
    
    return result


def expand_abbreviations(text: str, abbreviation_dict: Dict[str, str]) -> str:
    """
    Expand abbreviations to their full forms.
    
    Args:
        text: The text containing abbreviations
        abbreviation_dict: Dictionary mapping abbreviations to their expanded forms
        
    Returns:
        Text with abbreviations expanded
    """
    result = text
    
    # Sort abbreviations by length (longest first) to avoid partial matches
    sorted_abbrevs = sorted(abbreviation_dict.keys(), key=len, reverse=True)
    
    for abbrev in sorted_abbrevs:
        # Use word boundaries to avoid replacing substrings of words
        pattern = r'\b' + re.escape(abbrev) + r'\b'
        result = re.sub(pattern, abbreviation_dict[abbrev], result)
    
    return result


def normalize_numeric_text(text: str) -> str:
    """
    Convert numeric expressions to TTS-friendly formats.
    
    Args:
        text: The text containing numbers
        
    Returns:
        Text with numbers normalized
    """
    result = text
    
    # Replace numeric ranges with TTS-friendly format
    # For example: "Sections 1-5" -> "Sections 1 to 5"
    result = re.sub(r'(\d+)-(\d+)', r'\1 to \2', result)
    
    # Format legal code sections for better TTS reading
    # For example: "§ 123.45" -> "Section 123 point 45"
    result = re.sub(r'§\s*(\d+)\.(\d+)', r'Section \1 point \2', result)
    result = re.sub(r'§\s*(\d+)', r'Section \1', result)
    
    # Format dates consistently for TTS
    # MM/DD/YYYY -> Month DD, YYYY
    date_pattern = r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b'
    date_matches = re.finditer(date_pattern, result)
    
    # Process in reverse to avoid index shifts
    matches = list(date_matches)
    for match in reversed(matches):
        month, day, year = match.groups()
        month_names = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        try:
            month_name = month_names[int(month) - 1]
            replacement = f"{month_name} {int(day)}, {year}"
            result = result[:match.start()] + replacement + result[match.end():]
        except (ValueError, IndexError):
            # If month is invalid, leave as is
            pass
    
    return result


def ensure_sentence_pauses(text: str) -> str:
    """
    Ensure that sentence boundaries have appropriate pause markers.
    
    Args:
        text: The text to process
        
    Returns:
        Text with proper sentence boundaries for TTS
    """
    # Add period if text doesn't end with a sentence-ending punctuation
    if text and not re.search(r'[.!?]$', text):
        text += '.'
    
    # Ensure space after sentence-ending punctuation
    text = re.sub(r'([.!?])([^"\'\s\]):])', r'\1 \2', text)
    
    # Ensure proper spacing around punctuation for better TTS parsing
    text = re.sub(r'\s+([.,;:!?])', r'\1', text)
    
    return text


def finalize_tts_text(text: str) -> str:
    """
    Perform final cleanup on text to ensure it's ready for TTS.
    
    Args:
        text: The text to finalize
        
    Returns:
        Text ready for TTS systems
    """
    result = text
    
    # Remove excess whitespace
    result = re.sub(r'\s+', ' ', result).strip()
    
    # Replace multiple consecutive punctuation with a single instance
    result = re.sub(r'([.!?]){2,}', r'\1', result)
    
    # Ensure no double spaces
    while '  ' in result:
        result = result.replace('  ', ' ')
    
    return result


def create_ssml_output(text: str, add_breaks: bool = True) -> str:
    """
    Format text as SSML (Speech Synthesis Markup Language) for TTS systems that support it.
    
    Args:
        text: The text to convert to SSML
        add_breaks: Whether to add prosodic breaks at sentence boundaries
        
    Returns:
        Text formatted as SSML
    """
    # Escape XML characters
    escaped_text = (text.replace('&', '&amp;')
                    .replace('<', '&lt;')
                    .replace('>', '&gt;')
                    .replace('"', '&quot;')
                    .replace("'", '&apos;'))
    
    # Add sentence breaks if requested
    if add_breaks:
        # Add breaks after sentence-ending punctuation
        escaped_text = re.sub(r'([.!?])\s+', r'\1<break strength="medium"/> ', escaped_text)
    
    # Wrap in SSML tags
    ssml = f'<speak>{escaped_text}</speak>'
    
    return ssml


def remove_all_digits(text: str) -> str:
    """
    Remove all numeric digits (0-9) from text while preserving structure.
    
    This function handles various formats of numbers including:
    - Simple digits (1, 2, 3)
    - Formatted numbers (1,000 or 1.5 million)
    - Numbers in dates (January 1, 2023)
    - Numbers in section references (Section 123)
    - Ordinals (1st, 2nd, 3rd)
    
    Args:
        text: The text to process
        
    Returns:
        Text with all digits removed
    """
    # Handle specific cases where digits appear in common patterns
    
    # First, handle ordinals by replacing with non-digit version
    text = re.sub(r'\b(\d+)(st|nd|rd|th)\b', r'number\1', text)
    
    # Handle section and paragraph references
    text = re.sub(r'\b[Ss]ection\s+\d+', 'section number', text)
    text = re.sub(r'\b[Pp]aragraph\s+\d+', 'paragraph number', text)
    
    # Handle page references
    text = re.sub(r'\b[Pp]age\s+\d+', 'page number', text)
    
    # Handle years and dates
    text = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d+,\s+\d+\b', 
                 r'\1 date', text)
    text = re.sub(r'\b\d{4}\b', 'year', text)
    
    # Handle dollar amounts
    text = re.sub(r'\$\d[\d,.]*', 'dollar amount', text)
    
    # Handle percentage values
    text = re.sub(r'\b\d[\d,.]*\s*%', 'percentage value', text)
    
    # Finally, remove all remaining digits
    return re.sub(r'[0-9]', '', text)


def remove_all_urls(text: str) -> str:
    """
    Remove all URLs and web references from the text.
    
    Args:
        text: The text containing URLs to remove
        
    Returns:
        Text with all URLs and web references removed
    """
    patterns = [
        # Standard URLs
        r'https?://\S+',
        r'www\.\S+',
        
        # Google Scholar case citations
        r'\("https?.*?scholar.*?case\?.*?"\)',
        r'\("https?.*?google.*?scholar.*?"\)',
        
        # Citation URLs with spaces
        r'\("[^"]*https?\s*:\s*/+\s*scholar\s*\.\s*google\s*\.\s*com[^"]*"\)',
        r'\("[^"]*=\s*proximate\+cause\+cases[^"]*"\)',
        
        # Legal citation URLs, allowing for spaces or broken formatting
        r'https?\s*:?\s*//?\s*scholar\s*\.\s*google\s*\.\s*com\s*[^"\s,;:!?]*',
        
        # Common domains without protocol
        r'\b[a-zA-Z0-9][a-zA-Z0-9-]*\.[a-zA-Z]{2,}\b',
    ]
    
    result = text
    
    # First pass: remove all parenthesized quotes containing URLs or citation fragments
    result = re.sub(r'\([^)]*"[^"]*https?[^"]*"[^)]*\)', '', result)
    result = re.sub(r'\([^)]*"[^"]*google[^"]*"[^)]*\)', '', result)
    result = re.sub(r'\([^)]*"[^"]*scholar[^"]*"[^)]*\)', '', result)
    
    # Apply each pattern
    for pattern in patterns:
        result = re.sub(pattern, '', result)
    
    # Clean up consecutive spaces created by removing URLs
    result = re.sub(r'\s+', ' ', result)
    
    return result.strip()


def apply_dictionary_filter(text: str, custom_dictionary_path: Optional[str] = None,
                            remove_digits: bool = False) -> str:
    """
    Filter text to keep only recognized words from a dictionary.
    
    This removes URLs, citations, and other non-word text that might
    disrupt TTS processing, while preserving natural English.
    
    Args:
        text: The text to filter
        custom_dictionary_path: Optional path to a custom dictionary file with one word per line
        remove_digits: Whether to remove all digits from the text
        
    Returns:
        Text with only dictionary words and essential punctuation
    """
    # First, aggressively remove all URLs and web references
    text = remove_all_urls(text)
    
    # Remove all digits if requested
    if remove_digits:
        text = remove_all_digits(text)
    
    # Load dictionary words
    word_set = _load_dictionary(custom_dictionary_path)
    
    # First, normalize spacing to help with tokenization
    text = re.sub(r'\s+', ' ', text)
    
    # Pre-process to break up unnaturally long concatenated words
    # This helps with cases like "BiancoBrandiJonesRudy" where multiple names are joined
    text = _break_concatenated_words(text, word_set)
    
    # Split into sentences to better preserve context
    sentences = re.split(r'([.!?])', text)
    filtered_sentences = []
    
    for i in range(0, len(sentences), 2):
        sentence = sentences[i]
        # Add the punctuation if it exists
        if i + 1 < len(sentences):
            sentence += sentences[i + 1]
        
        # Remove non-alphanumeric sequences that aren't valid words
        sentence = re.sub(r'[^\s\w.,;:!?\'"-]+', ' ', sentence)
        
        # Tokenize to handle contractions and hyphenated words properly
        tokens = re.findall(r'\b[\w\'\-]+\b|[.,;:!?]', sentence)
        filtered_tokens = []
        
        for token in tokens:
            # Always keep punctuation
            if token in '.,;:!?':
                filtered_tokens.append(token)
                continue
                
            # Skip tokens that contain digits if remove_digits is enabled
            if remove_digits and re.search(r'[0-9]', token):
                continue
                
            # Skip extremely long tokens that are unlikely to be valid words
            if len(token) > 20:
                continue
                
            # Check if word is in dictionary (original or lowercase form)
            token_lower = token.lower()
            if token_lower in word_set or token in word_set:
                filtered_tokens.append(token)
                continue
            
            # Special handling for contractions
            if "'" in token and (
                token_lower.replace("'", "") in word_set or
                token_lower.replace("'s", "") in word_set or
                token_lower.replace("'t", "") in word_set or
                token_lower.replace("'ve", "") in word_set or
                token_lower.replace("'re", "") in word_set or
                token_lower.replace("'ll", "") in word_set or
                token_lower.replace("'d", "") in word_set
            ):
                filtered_tokens.append(token)
                continue
                
            # Specialized handling for hyphenated words
            if "-" in token:
                parts = token.split("-")
                if all(part.lower() in word_set for part in parts if part):
                    filtered_tokens.append(token)
                    continue
            
            # Keep single letters (often used as references in legal documents)
            if len(token) == 1 and token.isalpha():
                filtered_tokens.append(token)
                continue
            
            # Keep common legal abbreviations not already in dictionary
            if token_lower in {'v', 'vs', 'etc', 'ie', 'eg', 'co', 'inc', 'llc', 'llp', 'jr', 'sr', 'no', 'id', 'op'}:
                filtered_tokens.append(token)
                continue
        
        # Join tokens with proper spacing
        filtered_sentence = ' '.join(filtered_tokens)
        # Clean up spaces before punctuation
        filtered_sentence = re.sub(r'\s+([.,;:!?])', r'\1', filtered_sentence)
        filtered_sentences.append(filtered_sentence)
    
    # Join sentences into the final text
    result = ' '.join(filtered_sentences)
    
    # Final cleanup of any multiple spaces
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def _break_concatenated_words(text: str, word_set: Set[str]) -> str:
    """
    Break up unnaturally long concatenated words that would cause TTS to spell them.
    
    This helps with cases like "BiancoBrandiJonesRudy" where multiple words
    (often names in legal documents) are concatenated without spaces.
    
    Args:
        text: The text to process
        word_set: Dictionary of valid words to use for word boundary detection
        
    Returns:
        Text with long concatenated words broken into component words where possible
    """
    # First pass: detect long words that might be concatenated
    # Lower threshold to catch more concatenated words (was 15)
    words = re.findall(r'\b[A-Za-z]{12,}\b', text)
    
    for long_word in words:
        # Skip if the word is somehow in our dictionary already
        if long_word.lower() in word_set:
            continue
            
        # Try to break it up by looking for case transitions (camelCase)
        potential_breaks = []
        
        # Find camelCase transitions (lowercase to uppercase)
        for i in range(1, len(long_word)):
            if long_word[i-1].islower() and long_word[i].isupper():
                potential_breaks.append(i)
        
        # Look for common name patterns (e.g., capitalized words)
        # This helps with concatenated proper names like "BiancoBrandiJones"
        if not potential_breaks or len(long_word) > 20:
            # Scan for capital letters not at the start
            for i in range(1, len(long_word)):
                if long_word[i].isupper():
                    potential_breaks.append(i)
        
        # If still no breaks found, try to find known words within the string
        if not potential_breaks:
            i = 0
            while i < len(long_word):
                # Try different word lengths, prioritizing longer matches
                for length in range(min(12, len(long_word) - i), 2, -1):
                    substring = long_word[i:i+length]
                    if substring.lower() in word_set:
                        if i + length < len(long_word):
                            potential_breaks.append(i + length)
                        i += length
                        break
                else:
                    i += 1  # No match found, move forward by one character
        
        # Add a special case for common name endings
        if len(long_word) > 5:
            for ending in ["son", "ton", "ley", "man", "ard", "ner", "ter", "ing", "ford", "berg", "burg"]:
                end_pos = long_word.lower().rfind(ending)
                if end_pos > 0 and end_pos + len(ending) == len(long_word):
                    potential_breaks.append(end_pos)
        
        # If we found potential break points, insert spaces
        if potential_breaks:
            new_word = ""
            last_break = 0
            for break_point in sorted(potential_breaks):
                new_word += long_word[last_break:break_point] + " "
                last_break = break_point
            new_word += long_word[last_break:]
            
            # Replace the original word with the spaced version
            text = text.replace(long_word, new_word.strip())
        # Fallback for exceptionally long words that still weren't broken
        # Break every 5-6 characters as a last resort to prevent TTS spelling
        elif len(long_word) > 25:
            # Break every 5-6 characters for very long words
            new_word = ""
            for i in range(0, len(long_word), 5):
                new_word += long_word[i:i+5] + " "
            text = text.replace(long_word, new_word.strip())
    
    return text


def _load_dictionary(custom_dictionary_path: Optional[str] = None) -> Set[str]:
    """
    Load a comprehensive dictionary of English words and legal terms from multiple sources.
    
    Args:
        custom_dictionary_path: Optional path to a custom dictionary file with one word per line
        
    Returns:
        Set of lowercase English words and legal terms
    """
    # Initialize with our built-in dictionaries
    word_set = set()
    
    # 1. Start with our built-in basic English dictionary
    word_set.update(_load_basic_english())
    
    # 2. Add legal terms from Black's Law Dictionary and other common legal terminology
    word_set.update(_load_blacks_legal_dictionary())
    
    # 3. Try to load system dictionaries from common locations
    system_dictionaries = [
        '/usr/share/dict/words',           # Common Unix/Linux/macOS
        '/usr/dict/words',                 # Alternative Unix location
        '/usr/share/dict/american-english', # Debian/Ubuntu
        '/usr/share/dict/british-english',  # Debian/Ubuntu British
        'C:/Windows/Temp/words.txt',       # Possible Windows location if manually installed
    ]
    
    for dict_path in system_dictionaries:
        try:
            if os.path.exists(dict_path):
                with open(dict_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        word = line.strip().lower()
                        if word:
                            word_set.add(word)
                print(f"Loaded system dictionary: {dict_path}")
                break  # Stop after finding one valid dictionary
        except Exception as e:
            print(f"Error loading dictionary {dict_path}: {e}")
            continue
    
    # 4. Load NLTK's words corpus if available
    try:
        import nltk
        from nltk.corpus import words as nltk_words
        try:
            # Try to download if not already downloaded
            nltk.download('words', quiet=True)
            word_list = nltk_words.words()
            word_set.update(word.lower() for word in word_list)
            print("Loaded NLTK words corpus")
        except Exception as e:
            print(f"Could not load NLTK words corpus: {e}")
    except ImportError:
        # NLTK not installed, just continue
        pass
    
    # 5. Load user's custom dictionary if provided
    if custom_dictionary_path and os.path.exists(custom_dictionary_path):
        try:
            with open(custom_dictionary_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    word = line.strip().lower()
                    if word:
                        word_set.add(word)
            print(f"Loaded custom dictionary: {custom_dictionary_path}")
        except Exception as e:
            print(f"Error loading custom dictionary {custom_dictionary_path}: {e}")
    
    # 6. Add common contractions and their variations
    contractions = _load_contractions()
    word_set.update(contractions)
    
    return word_set


def _load_basic_english() -> Set[str]:
    """
    Load a comprehensive list of common English words as a fallback.
    
    Returns:
        Set of common English words
    """
    # This is a significantly expanded list of common English words
    # to provide better coverage when a system dictionary isn't available
    return {
        # Original basic words
        'a', 'about', 'all', 'also', 'and', 'as', 'at', 'be', 'because', 'but',
        'by', 'can', 'come', 'could', 'day', 'do', 'even', 'find', 'first', 'for',
        'from', 'get', 'give', 'go', 'have', 'he', 'her', 'here', 'him', 'his',
        'how', 'i', 'if', 'in', 'into', 'it', 'its', 'just', 'know', 'like',
        'look', 'make', 'man', 'many', 'me', 'more', 'my', 'new', 'no', 'not',
        'now', 'of', 'on', 'one', 'only', 'or', 'other', 'our', 'out', 'people',
        'say', 'see', 'she', 'so', 'some', 'take', 'tell', 'than', 'that', 'the',
        'their', 'them', 'then', 'there', 'these', 'they', 'thing', 'think', 'this',
        'those', 'time', 'to', 'two', 'up', 'use', 'very', 'want', 'way', 'we',
        'well', 'what', 'when', 'which', 'who', 'will', 'with', 'would', 'year', 'you',
        'your',
        
        # Additional common English words
        'ability', 'able', 'above', 'accept', 'according', 'account', 'across', 'act', 
        'action', 'activity', 'actually', 'add', 'address', 'administration', 'admit', 
        'adult', 'affect', 'after', 'again', 'against', 'age', 'agency', 'agent', 
        'ago', 'agree', 'agreement', 'ahead', 'air', 'allow', 'almost', 'alone', 
        'along', 'already', 'although', 'always', 'american', 'among', 'amount', 
        'analysis', 'animal', 'another', 'answer', 'any', 'anyone', 'anything', 
        'appear', 'apply', 'approach', 'area', 'argue', 'arm', 'around', 'arrive', 
        'art', 'article', 'artist', 'ask', 'assume', 'attention', 'attorney', 'audience', 
        'author', 'authority', 'available', 'avoid', 'away', 'baby', 'back', 'bad', 
        'bag', 'ball', 'bank', 'bar', 'base', 'beat', 'beautiful', 'become', 'bed', 
        'before', 'begin', 'behavior', 'behind', 'believe', 'benefit', 'best', 'better', 
        'between', 'beyond', 'big', 'bill', 'billion', 'bit', 'black', 'blood', 'blue', 
        'board', 'body', 'book', 'born', 'both', 'box', 'boy', 'break', 'bring', 
        'brother', 'budget', 'build', 'building', 'business', 'call', 'camera', 'campaign', 
        'cancer', 'candidate', 'capital', 'car', 'card', 'care', 'career', 'carry', 
        'case', 'catch', 'cause', 'cell', 'center', 'central', 'century', 'certain', 
        'certainly', 'chair', 'challenge', 'chance', 'change', 'character', 'charge', 
        'check', 'child', 'choice', 'choose', 'church', 'citizen', 'city', 'civil', 
        'claim', 'class', 'clear', 'clearly', 'close', 'coach', 'cold', 'collection', 
        'college', 'color', 'commercial', 'common', 'community', 'company', 'compare', 
        'computer', 'concern', 'condition', 'conference', 'consider', 'consumer', 
        'contain', 'continue', 'control', 'cost', 'country', 'couple', 'course', 
        'court', 'cover', 'create', 'crime', 'cultural', 'culture', 'cup', 'current', 
        'customer', 'cut', 'dark', 'data', 'daughter', 'dead', 'deal', 'death', 
        'debate', 'decade', 'decide', 'decision', 'deep', 'defense', 'degree', 
        'democratic', 'describe', 'design', 'despite', 'detail', 'determine', 'develop', 
        'development', 'die', 'difference', 'different', 'difficult', 'dinner', 
        'direction', 'director', 'discover', 'discuss', 'discussion', 'disease', 
        'doctor', 'dog', 'door', 'down', 'draw', 'dream', 'drive', 'drop', 'drug', 
        'during', 'each', 'early', 'east', 'easy', 'eat', 'economic', 'economy', 
        'edge', 'education', 'effect', 'effort', 'eight', 'either', 'election', 
        'else', 'employee', 'end', 'energy', 'enjoy', 'enough', 'enter', 'entire', 
        'environment', 'environmental', 'especially', 'establish', 'even', 'evening', 
        'event', 'ever', 'every', 'everybody', 'everyone', 'everything', 'evidence', 
        'exactly', 'example', 'executive', 'exist', 'expect', 'experience', 'expert', 
        'explain', 'eye', 'face', 'fact', 'factor', 'fail', 'fall', 'family', 'far', 
        'fast', 'father', 'fear', 'federal', 'feel', 'feeling', 'few', 'field', 'fight', 
        'figure', 'fill', 'film', 'final', 'finally', 'financial', 'fine', 'finger', 
        'finish', 'fire', 'firm', 'five', 'floor', 'fly', 'focus', 'follow', 'food', 
        'foot', 'force', 'foreign', 'forget', 'form', 'former', 'forward', 'four', 
        'free', 'friend', 'front', 'full', 'fund', 'future', 'game', 'garden', 'gas', 
        'general', 'generation', 'girl', 'give', 'glass', 'global', 'goal', 'good', 
        'government', 'great', 'green', 'ground', 'group', 'grow', 'growth', 'guess', 
        'gun', 'guy', 'hair', 'half', 'hand', 'hang', 'happen', 'happy', 'hard', 
        'hardly', 'head', 'health', 'hear', 'heart', 'heat', 'heavy', 'help', 'herself', 
        'high', 'himself', 'history', 'hit', 'hold', 'home', 'hope', 'hospital', 
        'hot', 'hotel', 'hour', 'house', 'however', 'huge', 'human', 'hundred', 
        'husband', 'idea', 'identify', 'image', 'imagine', 'impact', 'important', 
        'improve', 'include', 'including', 'increase', 'indeed', 'indicate', 'individual', 
        'industry', 'information', 'inside', 'instead', 'institution', 'interest', 
        'interesting', 'international', 'interview', 'investment', 'involve', 'issue', 
        'item', 'itself', 'job', 'join', 'journal', 'journey', 'joy', 'judge', 'jump', 
        'key', 'kid', 'kill', 'kind', 'kitchen', 'knowledge', 'land', 'language', 
        'large', 'last', 'late', 'later', 'laugh', 'law', 'lawyer', 'lay', 'lead', 
        'leader', 'learn', 'least', 'leave', 'left', 'leg', 'legal', 'less', 'let', 
        'letter', 'level', 'lie', 'life', 'light', 'likely', 'line', 'list', 'listen', 
        'little', 'live', 'local', 'long', 'lose', 'loss', 'lot', 'love', 'low', 'machine', 
        'magazine', 'main', 'maintain', 'major', 'majority', 'manage', 'management', 
        'manager', 'market', 'marriage', 'material', 'matter', 'may', 'maybe', 'mean', 
        'measure', 'media', 'medical', 'meet', 'meeting', 'member', 'memory', 'mention', 
        'message', 'method', 'middle', 'might', 'military', 'million', 'mind', 'minute', 
        'miss', 'mission', 'model', 'modern', 'moment', 'money', 'month', 'moral', 
        'morning', 'most', 'mother', 'mouth', 'move', 'movement', 'movie', 'much', 
        'music', 'must', 'myself', 'name', 'nation', 'national', 'natural', 'nature', 
        'near', 'nearly', 'necessary', 'need', 'network', 'never', 'news', 'newspaper', 
        'next', 'nice', 'night', 'none', 'north', 'note', 'nothing', 'notice', 'number', 
        'occur', 'off', 'offer', 'office', 'officer', 'official', 'often', 'oil', 
        'ok', 'old', 'once', 'open', 'operation', 'opportunity', 'option', 'order', 
        'organization', 'others', 'outside', 'over', 'own', 'owner', 'page', 'pain', 
        'painting', 'paper', 'parent', 'part', 'participant', 'particular', 'particularly', 
        'partner', 'party', 'pass', 'past', 'patient', 'pattern', 'pay', 'peace', 
        'person', 'personal', 'phone', 'physical', 'pick', 'picture', 'piece', 'place', 
        'plan', 'plant', 'play', 'player', 'pm', 'point', 'police', 'policy', 'political', 
        'politics', 'poor', 'popular', 'population', 'position', 'positive', 'possible', 
        'power', 'practice', 'prepare', 'present', 'president', 'pressure', 'pretty', 
        'prevent', 'price', 'private', 'probably', 'problem', 'process', 'produce', 
        'product', 'production', 'professional', 'professor', 'program', 'project', 
        'property', 'protect', 'prove', 'provide', 'public', 'pull', 'purpose', 'push', 
        'put', 'quality', 'question', 'quickly', 'quite', 'race', 'radio', 'raise', 
        'range', 'rate', 'rather', 'reach', 'read', 'ready', 'real', 'reality', 'realize', 
        'really', 'reason', 'receive', 'recent', 'recently', 'recognize', 'record', 
        'red', 'reduce', 'reflect', 'region', 'relate', 'relationship', 'religious', 
        'remain', 'remember', 'remove', 'report', 'represent', 'republican', 'require', 
        'research', 'resource', 'respond', 'response', 'responsibility', 'rest', 
        'result', 'return', 'reveal', 'rich', 'right', 'rise', 'risk', 'road', 'rock', 
        'role', 'room', 'rule', 'run', 'safe', 'same', 'save', 'scene', 'school', 
        'science', 'scientist', 'score', 'sea', 'season', 'seat', 'second', 'section', 
        'security', 'seek', 'seem', 'sell', 'send', 'senior', 'sense', 'series', 
        'serious', 'serve', 'service', 'set', 'seven', 'several', 'sex', 'sexual', 
        'shake', 'share', 'shoot', 'short', 'shot', 'should', 'shoulder', 'show', 
        'side', 'sign', 'significant', 'similar', 'simple', 'simply', 'since', 'sing', 
        'single', 'sister', 'sit', 'site', 'situation', 'six', 'size', 'skill', 'skin', 
        'small', 'smile', 'social', 'society', 'soldier', 'solution', 'solve', 'someone', 
        'something', 'sometimes', 'son', 'song', 'soon', 'sort', 'sound', 'source', 
        'south', 'southern', 'space', 'speak', 'special', 'specific', 'speech', 'spend', 
        'sport', 'spring', 'staff', 'stage', 'stand', 'standard', 'star', 'start', 
        'state', 'statement', 'station', 'stay', 'step', 'still', 'stock', 'stop', 
        'store', 'story', 'strategy', 'street', 'strong', 'structure', 'student', 
        'study', 'stuff', 'style', 'subject', 'success', 'successful', 'such', 
        'suddenly', 'suffer', 'suggest', 'summer', 'support', 'sure', 'surface', 
        'system', 'table', 'talk', 'task', 'tax', 'teach', 'teacher', 'team', 
        'technology', 'television', 'ten', 'term', 'test', 'text', 'thank', 'theory', 
        'though', 'thought', 'thousand', 'threat', 'three', 'through', 'throughout', 
        'throw', 'thus', 'today', 'together', 'tomorrow', 'tonight', 'too', 'top', 
        'total', 'tough', 'toward', 'town', 'trade', 'traditional', 'training', 
        'travel', 'treat', 'treatment', 'tree', 'trial', 'trip', 'trouble', 'true', 
        'truth', 'try', 'turn', 'tv', 'type', 'under', 'understand', 'unit', 'until', 
        'upon', 'usually', 'value', 'various', 'vehicle', 'view', 'violence', 'visit', 
        'voice', 'vote', 'wait', 'walk', 'wall', 'war', 'watch', 'water', 'weapon', 
        'wear', 'week', 'weight', 'welcome', 'west', 'western', 'whatever', 'whether', 
        'while', 'white', 'whole', 'whom', 'whose', 'why', 'wide', 'wife', 'win', 
        'wind', 'window', 'wish', 'within', 'without', 'woman', 'wonder', 'word', 
        'work', 'worker', 'world', 'worry', 'write', 'writer', 'wrong', 'yard', 'yeah', 
        'yesterday', 'yet', 'young', 'yourself'
    }


def _load_blacks_legal_dictionary() -> Set[str]:
    """
    Load legal terms from Black's Law Dictionary and other legal sources.
    
    Returns:
        Set of common legal terms (lowercase)
    """
    # This is a subset of important terms from Black's Law Dictionary
    # and other common legal terminology
    return {
        # Court-related terms
        'court', 'courts', 'judge', 'judges', 'justice', 'justices', 'jury', 'juror',
        'jurors', 'bench', 'tribunal', 'panel', 'magistrate', 'courthouse', 'chambers',
        'appellant', 'appellee', 'petitioner', 'respondent', 'plaintiff', 'plaintiffs',
        'defendant', 'defendants', 'prosecutor', 'prosecution', 'defense', 'counsel',
        'attorney', 'attorneys', 'lawyer', 'lawyers', 'advocate', 'advocates', 'solicitor',
        'barrister', 'esquire', 'clerk', 'bailiff', 'docket', 'venue', 'jurisdiction',
        'courtroom', 'chief', 'associate', 'senior', 'junior', 'presiding', 'sitting',
        'retired', 'appointed', 'elected', 'district', 'circuit', 'supreme', 'appellate',
        'federal', 'state', 'local', 'municipal', 'magistrate', 'commissioner',
        'chancellor', 'referee', 'arbitrator', 'mediator', 'ombudsman', 'prothonotary',
        
        # Case-related terms
        'case', 'cases', 'matter', 'matters', 'action', 'suit', 'petition', 'appeal',
        'trial', 'hearing', 'proceeding', 'proceedings', 'litigation', 'dispute',
        'lawsuit', 'claim', 'complaint', 'motion', 'pleading', 'brief', 'argument',
        'testimony', 'evidence', 'exhibit', 'deposition', 'interrogatory', 'discovery',
        'subpoena', 'warrant', 'injunction', 'order', 'ruling', 'finding', 'verdict',
        'judgment', 'opinion', 'decision', 'decree', 'settlement', 'dismissal', 'acquittal',
        'conviction', 'sentence', 'damages', 'remedy', 'relief', 'compensation', 'restitution',
        'writ', 'mandamus', 'certiorari', 'habeas', 'corpus', 'prohibition', 'quo', 'warranto',
        'supersedeas', 'attachment', 'garnishment', 'foreclosure', 'ejectment', 'replevin',
        'interpleader', 'declaratory', 'adjudication', 'demurrer', 'vacate', 'remand',
        'remittitur', 'reconsideration', 'rehearing', 'retrial', 'mistrial', 'nolle',
        'prosequi', 'reprieve', 'pardon', 'commutation', 'laches', 'estoppel', 'collateral',
        
        # Legal concepts
        'law', 'legal', 'illegal', 'jurisprudence', 'precedent', 'authority', 'statute',
        'statutory', 'legislation', 'regulation', 'rule', 'code', 'constitution', 'constitutional',
        'unconstitutional', 'amendment', 'provision', 'clause', 'section', 'subsection',
        'paragraph', 'article', 'title', 'chapter', 'act', 'bill', 'ordinance', 'treaty',
        'common', 'civil', 'criminal', 'procedural', 'substantive', 'public', 'private',
        'domestic', 'international', 'transnational', 'federal', 'national', 'state',
        'municipal', 'administrative', 'regulatory', 'commercial', 'corporate', 'tax',
        'property', 'contract', 'tort', 'trust', 'estate', 'family', 'bankruptcy',
        'environmental', 'labor', 'employment', 'maritime', 'admiralty', 'immigration',
        'intellectual', 'patent', 'copyright', 'trademark', 'antitrust', 'securities',
        
        # Legal principles
        'right', 'rights', 'duty', 'obligation', 'liability', 'negligence', 'tort',
        'breach', 'contract', 'agreement', 'covenant', 'property', 'possession', 'ownership',
        'title', 'interest', 'lien', 'equity', 'trust', 'estate', 'will', 'testament',
        'inheritance', 'bequest', 'devise', 'probate', 'intestate', 'bankruptcy', 'insolvency',
        'due', 'process', 'equal', 'protection', 'freedom', 'speech', 'religion', 'press',
        'assembly', 'privacy', 'search', 'seizure', 'warrant', 'reasonable', 'suspicion',
        'probable', 'cause', 'self', 'incrimination', 'double', 'jeopardy', 'speedy',
        'trial', 'confrontation', 'counsel', 'bail', 'cruel', 'unusual', 'punishment',
        'proportionality', 'restitution', 'causation', 'foreseeability', 'remoteness',
        'novus', 'actus', 'interveniens', 'contributory', 'comparative', 'strict',
        'vicarious', 'joint', 'several', 'joint', 'severally', 'indemnity', 'contribution',
        'subrogation', 'offset', 'recoupment', 'setoff', 'satisfaction', 'accord',
        
        # Criminal law
        'crime', 'criminal', 'felony', 'misdemeanor', 'offense', 'violation',
        'infraction', 'indictment', 'charge', 'arrest', 'detention', 'bail', 'parole',
        'probation', 'custody', 'imprisonment', 'homicide', 'murder', 'manslaughter',
        'assault', 'battery', 'rape', 'robbery', 'burglary', 'theft', 'larceny',
        'fraud', 'forgery', 'perjury', 'bribery', 'extortion', 'conspiracy',
        'accomplice', 'accessory', 'principal', 'attempt', 'solicitation', 'mens',
        'rea', 'actus', 'reus', 'intent', 'motive', 'malice', 'aforethought', 'premeditation',
        'deliberation', 'recklessness', 'negligence', 'guilty', 'innocent', 'insanity',
        'diminished', 'capacity', 'intoxication', 'duress', 'necessity', 'entrapment',
        'alibi', 'self', 'defense', 'justification', 'excuse', 'mitigation',
        
        # Legal standards
        'reasonable', 'prudent', 'preponderance', 'burden', 'proof', 'beyond',
        'doubt', 'clear', 'convincing', 'hearsay', 'admissible', 'inadmissible',
        'relevant', 'material', 'competent', 'credible', 'presumption', 'inference',
        'standard', 'review', 'novo', 'clearly', 'erroneous', 'substantial', 'evidence',
        'abuse', 'discretion', 'manifest', 'error', 'plain', 'harmless', 'prejudicial',
        'prima', 'facie', 'presumptive', 'rebuttable', 'conclusive', 'judicial', 'notice',
        'foundation', 'authentication', 'chain', 'custody', 'expert', 'lay', 'opinion',
        'demonstrative', 'circumstantial', 'direct', 'corroborative', 'exculpatory',
        'inculpatory', 'impeachment', 'rehabilitative', 'cumulative', 'best', 'evidence',
        'parol', 'testimonial', 'documentary', 'physical', 'real', 'documentary',
        
        # Legal process terms
        'file', 'filed', 'filing', 'serve', 'served', 'service', 'notice', 'summons',
        'appear', 'appearance', 'default', 'contest', 'stipulate', 'stipulation',
        'mediation', 'arbitration', 'judicial', 'extrajudicial', 'administrative',
        'procedure', 'proceedings', 'pretrial', 'trial', 'posttrial', 'voir', 'dire',
        'opening', 'statement', 'closing', 'argument', 'deliberation', 'verdict',
        'sentencing', 'scheduling', 'continuance', 'adjournment', 'recess', 'sidebar',
        'chambers', 'contempt', 'sanction', 'disposition', 'final', 'interlocutory',
        'provisional', 'temporary', 'preliminary', 'permanent', 'interim', 'alternative',
        'dispute', 'resolution', 'negotiation', 'settlement', 'compromise', 'release',
        'confidentiality', 'privilege', 'attorney', 'client', 'work', 'product',
        
        # Legal relationship terms
        'party', 'parties', 'privity', 'agent', 'principal', 'fiduciary', 'guardian',
        'ward', 'minor', 'infant', 'spouse', 'marriage', 'divorce', 'custody',
        'adoption', 'guardian', 'grantor', 'grantee', 'trustor', 'trustee', 'beneficiary',
        'lessor', 'lessee', 'landlord', 'tenant', 'licensor', 'licensee',
        'bailor', 'bailee', 'vendor', 'vendee', 'mortgagor', 'mortgagee', 'pledgor',
        'pledgee', 'assignor', 'assignee', 'donor', 'donee', 'testator', 'testatrix',
        'intestate', 'heir', 'devisee', 'legatee', 'executor', 'executrix', 'administrator',
        'administratrix', 'decedent', 'descendant', 'ancestor', 'consanguinity', 'affinity',
        'spouse', 'partner', 'shareholder', 'stockholder', 'director', 'officer',
        'incorporator', 'promoter', 'member', 'manager', 'partner', 'general', 'limited',
        
        # Citation terms
        'cite', 'cited', 'citing', 'citation', 'citations', 'authority', 'footnote',
        'supra', 'infra', 'herein', 'aforementioned', 'aforesaid', 'pursuant', 'versus',
        'foregoing', 'hereby', 'whereby', 'notwithstanding', 'prima', 'facie',
        'id', 'ibid', 'op', 'cit', 'loc', 'passim', 'contra', 'but', 'see', 'compare',
        'cf', 'accord', 'see', 'generally', 'annotated', 'annotation', 'supplement',
        'reporter', 'digest', 'treatise', 'restatement', 'hornbook', 'casebook',
        'per', 'curiam', 'seriatim', 'sub', 'nom', 'sub', 'silentio', 'en', 'banc',
        'in', 'chambers', 'slip', 'opinion', 'unpublished', 'headnote', 'syllabus',
        
        # Court hierarchy
        'supreme', 'appellate', 'district', 'circuit', 'federal', 'state', 'municipal',
        'superior', 'inferior', 'probate', 'chancery', 'admiralty', 'bankruptcy',
        'court', 'appeals', 'claims', 'international', 'justice', 'high', 'intermediate',
        'trial', 'juvenile', 'family', 'surrogate', 'orphans', 'tax', 'land', 'water',
        'maritime', 'military', 'tribunal', 'commission', 'board', 'panel', 'authority',
        
        # Common Latin legal terms
        'amicus', 'curiae', 'certiorari', 'habeas', 'corpus', 'mandamus', 'prima',
        'facie', 'res', 'judicata', 'stare', 'decisis', 'ratio', 'decidendi', 'obiter',
        'dictum', 'inter', 'alia', 'sua', 'sponte', 'mens', 'rea', 'actus', 'reus',
        'ab', 'initio', 'de', 'facto', 'de', 'jure', 'ex', 'parte', 'ex', 'post',
        'pro', 'se', 'bona', 'fide', 'quid', 'pro', 'quo', 'subpoena', 'duces', 'tecum',
        'voir', 'dire', 'locus', 'standi', 'modus', 'operandi', 'caveat', 'emptor',
        'audi', 'alteram', 'partem', 'nemo', 'judex', 'causa', 'sui', 'lex', 'loci',
        'lex', 'fori', 'lex', 'mercatoria', 'in', 'personam', 'in', 'rem', 'locus',
        'delicti', 'forum', 'non', 'conveniens', 'res', 'gestae', 'res', 'ipsa',
        'loquitur', 'corpus', 'delicti', 'animus', 'possidendi', 'animus', 'revertendi',
        'ejusdem', 'generis', 'expressio', 'unius', 'exclusio', 'alterius', 'noscitur',
        'sociis', 'pari', 'materia', 'casus', 'omissus', 'nulla', 'poena', 'sine',
        'lege', 'ignorantia', 'legis', 'neminem', 'excusat', 'non', 'compos', 'mentis',
        
        # Common legal abbreviations
        'corp', 'co', 'inc', 'llc', 'llp', 'ltd', 'esq', 'jr', 'sr', 'etc', 'ie', 'eg',
        'viz', 're', 'ibid', 'id', 'op', 'cit', 'et', 'al', 'seq', 'ff', 'cf', 'vs',
        'v', 'no', 'nos', 'al', 'app', 'supp', 'ed', 'rev', 'civ', 'crim', 'proc',
        'adm', 'admin', 'ann', 'ch', 'const', 'dist', 'div', 'evid', 'jud', 'juris',
        'liab', 'prop', 'stat', 'subst', 'ucc', 'cf', 
        
        # Standard legal phraseology
        'cause', 'action', 'standard', 'review', 'due', 'process', 'equal', 'protection',
        'good', 'faith', 'bad', 'faith', 'public', 'policy', 'reasonable', 'doubt',
        'proximate', 'cause', 'efficient', 'intervening', 'superseding', 'joint', 'several',
        'capacity', 'immunity', 'privilege', 'class', 'standing', 'moot', 'ripeness',
        'justiciable', 'diversity', 'jurisdiction', 'summary', 'directed', 'remand',
        'remanded', 'reversed', 'vacated', 'affirmed', 'overruled', 'distinguished',
        'concurring', 'dissenting', 'majority', 'plurality', 'per', 'curiam',
        'balance', 'interests', 'adequate', 'remedy', 'compelling', 'interest',
        'substantial', 'factor', 'heightened', 'scrutiny', 'rational', 'basis',
        'intermediate', 'strict', 'scrutiny', 'narrowly', 'tailored', 'least',
        'restrictive', 'means', 'slippery', 'slope', 'chilling', 'effect', 'facial',
        'challenge', 'applied', 'challenge', 'overbroad', 'vague', 'content',
        'neutral', 'time', 'place', 'manner', 'restriction', 'forum', 'public',
        
        # Specific areas of law
        'tort', 'contract', 'property', 'criminal', 'civil', 'constitutional', 'administrative',
        'environmental', 'corporate', 'bankruptcy', 'tax', 'immigration', 'intellectual', 'patent',
        'copyright', 'trademark', 'family', 'labor', 'employment', 'maritime', 'admiralty',
        'international', 'commercial', 'antitrust', 'securities', 'insurance', 
        'telecommunications', 'energy', 'healthcare', 'medical', 'malpractice', 'consumer',
        'protection', 'products', 'liability', 'entertainment', 'sports', 'disability',
        'elder', 'veterans', 'education', 'transportation', 'aviation', 'banking',
        'finance', 'real', 'estate', 'construction', 'landlord', 'tenant', 'zoning',
        'planning', 'eminent', 'domain', 'condemnation', 'foreclosure', 'eviction',
        
        # Insurance-specific terms
        'policy', 'coverage', 'insurer', 'insured', 'premium', 'claim', 'exclusion',
        'deductible', 'liability', 'indemnity', 'peril', 'risk', 'loss', 'casualty',
        'fire', 'accident', 'occurrence', 'proximate', 'allrisk', 'earthquake',
        'flood', 'homeowners', 'automobile', 'commercial', 'health', 'life', 'disability',
        'marine', 'title', 'errors', 'omissions', 'malpractice', 'workers', 'compensation',
        'umbrella', 'excess', 'reinsurance', 'surety', 'bond', 'fidelity', 'guaranty',
        'actuarial', 'underwrite', 'underwriting', 'premium', 'rider', 'endorsement',
        'declaration', 'conditions', 'warranties', 'representations', 'cancellation',
        'rescission', 'reformation', 'renewal', 'lapse', 'reinstatement', 'surrender',
        'assignment', 'third', 'party', 'beneficiary', 'proceeds', 'coinsurance',
        'occurrence', 'claims', 'made', 'notice', 'defense', 'settlement', 'reservation',
        'rights', 'duty', 'defend', 'indemnify', 'subrogation', 'exhaustion', 'primary',
        'secondary', 'self', 'insured', 'retention', 'captive', 'mutual', 'stock',
        'adjuster', 'adjustment', 'appraisal', 'arbitration', 'bad', 'faith',

        # Common state and federal entities 
        'california', 'cal', 'new', 'york', 'texas', 'florida', 'illinois',
        'pennsylvania', 'ohio', 'michigan', 'georgia', 'carolina', 'jersey',
        'virginia', 'washington', 'massachusetts', 'indiana', 'arizona', 'tennessee',
        'missouri', 'maryland', 'wisconsin', 'minnesota', 'colorado', 'alabama',
        'louisiana', 'kentucky', 'oregon', 'oklahoma', 'connecticut', 'iowa',
        'mississippi', 'arkansas', 'kansas', 'utah', 'nevada', 'mexico', 'nebraska',
        'idaho', 'hawaii', 'maine', 'hampshire', 'rhode', 'montana', 'delaware',
        'dakota', 'alaska', 'wyoming', 'vermont', 'north', 'south', 'west', 'east',
        'orleans', 'angeles', 'francisco', 'diego', 'antonio', 'jose', 'worth',
        'district', 'columbia', 'dc', 'commonwealth', 'territory', 'united', 'states',
        'america', 'usa', 'us', 'federal', 'state', 'county', 'city', 'municipal',
        'bureau', 'department', 'agency', 'commission', 'board', 'office', 'treasury',
        'commerce', 'justice', 'defense', 'interior', 'agriculture', 'labor', 'health',
        'human', 'services', 'housing', 'urban', 'development', 'transportation',
        'energy', 'education', 'veterans', 'affairs', 'homeland', 'security',
        
        # Additional legal terms for understanding case citations
        'dissent', 'dissenting', 'concur', 'concurring', 'plurality', 'majority',
        'opinion', 'supra', 'infra', 'et', 'seq', 'seq', 'ibid', 'id', 'cir',
        'app', 'supp', 'rptr', 'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        'jan', 'feb', 'mar', 'apr', 'jun', 'jul', 'aug', 'sep', 'sept', 'oct', 'nov', 'dec',
        '1st', '2nd', '2d', '3rd', '3d', '4th', '5th', '6th', '7th', '8th', '9th', '10th',
        '11th', 'dc', 'fed', 'ala', 'ariz', 'ark', 'alr', 'atl', 'am', 'bankr', 'bl',
        'bna', 'cal', 'colo', 'conn', 'del', 'fla', 'ga', 'haw', 'idaho', 'ill', 'ind',
        'iowa', 'kan', 'ky', 'la', 'me', 'md', 'mass', 'mich', 'minn', 'miss', 'mo',
        'mont', 'neb', 'nev', 'nh', 'nj', 'nm', 'ny', 'nc', 'nd', 'ohio', 'okla', 'or',
        'pa', 'ri', 'sc', 'sd', 'tenn', 'tex', 'utah', 'vt', 'va', 'wash', 'wva', 'wis',
        'wyo', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o',
        'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
    }


def _load_contractions() -> Set[str]:
    """
    Load common English contractions to ensure they're preserved in the filtered text.
    
    Returns:
        Set of common English contractions
    """
    return {
        # Common contractions
        "aren't", "can't", "couldn't", "didn't", "doesn't", "don't", "hadn't",
        "hasn't", "haven't", "he'd", "he'll", "he's", "i'd", "i'll", "i'm", "i've",
        "isn't", "it's", "let's", "mustn't", "shan't", "she'd", "she'll", "she's",
        "shouldn't", "that's", "there's", "they'd", "they'll", "they're", "they've",
        "we'd", "we'll", "we're", "we've", "weren't", "what'll", "what're", "what's",
        "what've", "where's", "who'd", "who'll", "who're", "who's", "who've", "won't",
        "wouldn't", "you'd", "you'll", "you're", "you've",
        
        # Possessive forms
        "president's", "government's", "country's", "world's", "company's", "family's",
        "student's", "teacher's", "children's", "parent's", "people's", "america's",
        "year's", "day's", "state's", "man's", "woman's", "nation's", "city's",
        "child's", "group's", "team's", "school's", "friend's", "father's", "mother's",
        "doctor's", "patient's", "client's", "customer's", "author's", "reader's",
        "writer's", "book's", "game's", "player's", "season's", "winter's", "summer's",
        "spring's", "fall's", "court's", "judge's", "jury's", "lawyer's", "defendant's",
        "plaintiff's", "witness's", "victim's", "society's", "industry's", "business's",
        "employer's", "employee's", "worker's", "manager's", "leader's", "officer's",
        "police's", "community's", "neighbor's", "dog's", "cat's", "bird's", "car's",
        "house's", "home's", "building's", "room's", "door's", "window's", "computer's",
        "phone's", "system's", "program's", "plan's", "idea's", "thought's", "mind's",
        "heart's", "body's", "head's", "eye's", "hand's", "foot's", "voice's", "face's",
        "president's", "minister's", "mayor's", "senator's", "congressman's", "congresswoman's",
        "governor's", "king's", "queen's", "prince's", "princess's", "army's", "navy's",
        "soldier's", "general's", "captain's", "ship's", "plane's", "train's", "driver's",
        "passenger's", "artist's", "musician's", "actor's", "actress's", "director's",
        "producer's", "journalist's", "reporter's", "editor's", "photographer's",
    } 