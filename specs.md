# Legal Text Filter for TTS Optimization

## 1. Project Overview

**Purpose:**
Develop a Python application that processes caselaw documents to remove legal citations and extraneous text elements that can interfere with a smooth text-to-speech (TTS) experience.

**Primary Goals:**

- **Input:** Accept raw legal documents.
- **Processing:** Clean the text by removing citations and simplifying legalese.
- **Output:** Produce TTS-friendly text.
- **Testing:** Provide basic unit tests and an example usage script.

**Stakeholders:**

- **Lawyers:** Legal professionals who need to quickly review and comprehend large volumes of case law documents.
- **Law Students:** Students who need to study and analyze legal texts for educational purposes.
- **Blind Lawyers:** Legal professionals with visual impairments who rely on screen readers and TTS technology to access and review legal documents.
- **Blind Law Students:** Students with visual impairments who need accessible formats of legal texts for their studies.

## 2. Core Features

- **Input Handling:**
  - Load legal text documents from local files or other sources.

- **Citation Identification & Handling:**
  - Integrate the `eyecite` library to **identify** the location and metadata of US legal citations.
  - Implement logic to **remove or replace** identified citations based on configuration.

- **NLP-based Text Cleaning:**
  - Utilize `spaCy` for core NLP tasks (tokenization, sentence boundary detection).
  - Implement **custom NLP rules** (e.g., regex, spaCy Matchers) within the pipeline to filter specific legal jargon, procedural text, or formatting artifacts not handled by `eyecite` or standard models.

- **TTS Optimization:**
  - Format the final text so that it is clear and natural for text-to-speech engines.

- **Testing and Documentation:**
  - Include unit tests for all modules and a main script demonstrating end-to-end processing.

## 3. Libraries & Dependencies

- **`eyecite`**
  - Repository: `freelawproject/eyecite`
  - Role: Extraction of legal citations from text (primarily US-focused; results require separate processing for removal/replacement).

- **`spaCy`**
  - Official Website: https://spacy.io
  - Repository: `explosion/spaCy`
  - Role: Text parsing, tokenization, sentence boundary detection, and enabling custom rule-based cleaning. (Requires careful application and potentially customization for legal text nuances).

- **(Optional) Regex, unittest/pytest**
  - For custom filtering and testing.

- **Python Version:** Recommended Python 3.10+

## 4. Project Structure

```
LegalTTSFilter/
├── input_handler.py       # Module to load raw legal text.
├── citation_filter.py     # Module using eyecite to extract and remove citations.
├── nlp_cleaner.py         # Module using spaCy for additional text cleaning.
├── tts_preparator.py      # Module that formats the processed text for TTS.
├── main.py                # Example script tying all modules together.
├── tests/
│   ├── test_citation_filter.py
│   ├── test_nlp_cleaner.py
│   └── test_input_handler.py
└── README.md              # Project overview and instructions.
```

## 5. Coding Conventions

- **Style Guide:**
  - Adhere to PEP 8 guidelines for Python code.

- **Comments & Documentation:**
  - Use clear, descriptive comments in code.
  - Include module-level docstrings to explain the purpose and usage of each module.
  - Annotate function signatures with type hints (e.g., `def filter_citations(text: str) -> str:`).
  - **Function Comments:** Each function should have a docstring that explains:
    - What the function does (purpose)
    - Parameters and their expected types/formats
    - Return values and their types
    - Exceptions that might be raised
    - Examples of usage for complex functions
    - Algorithm details or performance considerations where relevant
  - **Class Comments:** Each class should have a docstring that explains:
    - The purpose and responsibility of the class
    - Important attributes and their meanings
    - Any inheritance or composition relationships
    - Examples of instantiation and common usage patterns
  - **Code Logic Comments:** For complex code sections:
    - Explain the "why" behind the implementation, not just the "what"
    - Describe algorithm choices and any performance implications
    - Document any edge cases or special handling
    - Note any limitations or assumptions made
    - Clarify any non-obvious dependencies between variables or operations
  - **Avoid Redundant Comments:** Don't comment on code that is self-explanatory (e.g., `# Increment counter` for `counter += 1`).
  - **Keep Comments Updated:** Ensure comments stay in sync with code changes.

- **File Naming:**
  - Use lowercase and underscores (input_handler.py, citation_filter.py) for Python modules.

- **Naming Conventions:**
  - **Variables:** Use lowercase with underscores (snake_case) for all variables (e.g., `raw_text`, `citation_count`).
  - **Functions:** Use lowercase with underscores (snake_case) for function names (e.g., `extract_citations()`, `clean_text()`).
  - **Classes:** Use CapWords/PascalCase for class names (e.g., `CitationExtractor`, `TextCleaner`).
  - **Constants:** Use uppercase with underscores for constants (e.g., `MAX_CITATIONS`, `DEFAULT_MODEL`).
  - **Private Members:** Prefix with a single underscore for "internal use" variables and functions (e.g., `_process_text()`, `_raw_data`).
  - **Boolean Variables:** Use prefixes like "is_", "has_", or "should_" for boolean variables (e.g., `is_citation`, `has_errors`).
  - **Collections:** Use plural nouns for collections/iterables (e.g., `citations`, `documents`, `patterns`).

- **Version Control:**
  - Maintain frequent commits, descriptive commit messages, and use branches for major features.

## 6. Configurable Parameters

- **Input Parameters:**
  - File path or text string for raw legal documents.

- **Citation Handling Strategy:**
  - Option to completely remove citations.
  - Option to replace citations with a placeholder (e.g., "[CITATION]").

- **spaCy Processing Options:**
  - Model selection (e.g., "en_core_web_sm").
  - Configuration for **custom cleaning rules** (e.g., enabling/disabling specific regex patterns, custom entity removal).
  - Standard options like stopword removal or punctuation filters.

- **Output Settings:**
  - Format to be TTS-friendly (e.g., ensuring clear sentence boundaries, proper capitalization).
  - Option to save output to a file

## 7. Example Workflow

1.  **`input_handler.py`:**
    - Reads in the legal document.

2.  **`citation_filter.py`:**
    - Uses `eyecite` to **find** the locations of legal citations in the text.
    - Applies the configured strategy (remove or replace) to modify the text based on `eyecite`'s findings.

3.  **`nlp_cleaner.py`:**
    - Processes the citation-modified text using `spaCy` for tokenization and sentence splitting.
    - Applies **custom rules** (regex, matchers) to further remove or normalize unwanted tokens, phrases, or symbols specific to legal documents.

4.  **`tts_preparator.py`:**
    - Formats the cleaned text (e.g., ensuring proper sentence structure, handling abbreviations) to optimize readability for a TTS engine.

5. **main.py:**
   - Chains these processes together and outputs the final, TTS-optimized text.

6. **Tests:**
   - Run unit tests using pytest or unittest to verify each module's functionality. 