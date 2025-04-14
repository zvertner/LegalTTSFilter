# Legal Text Filter for TTS Optimization

## Project Overview

This project provides a Python application designed to process legal documents, specifically caselaw, to enhance their compatibility with text-to-speech (TTS) systems. It filters out legal citations and other extraneous text elements (like headers, footers, or procedural boilerplate) that can disrupt the fluency and clarity of synthesized speech, producing a cleaner text output suitable for TTS engines.

## Features

*   **Input Handling:** Reads legal text from local files (TXT, RTF, RTFD) or string inputs.
*   **Citation Filtering:** Utilizes the `eyecite` library to accurately identify US legal citations.
*   **Configurable Citation Handling:** Offers options to either completely remove citations or replace them with a simple placeholder (e.g., `[CITATION]`).
*   **NLP-based Cleaning:** Leverages `spaCy` for robust text processing, including tokenization and sentence boundary detection.
*   **Custom Cleaning Rules:** Implements customizable rules (regex, spaCy matchers) to remove additional non-essential text often found in legal documents.
*   **TTS-Optimized Output:** Formats the final text to improve flow and naturalness when read by TTS systems.
*   **Digit Removal:** Option to remove all numeric digits (0-9) from the final output for improved TTS clarity.
*   **URL Removal:** Option to remove all URLs (links starting with http: or https:) from the final output.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/zzvertigo/LegalTTSFilter.git
    cd LegalTTSFilter
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # venv\Scripts\activate
    # On macOS/Linux
    # source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    # You may also need to download a spaCy model:
    # python -m spacy download en_core_web_sm
    ```

## Usage

*(This section assumes a main script `main.py` is implemented as per the project structure)*

**Command-line execution (Example):**

```bash
python main.py --input-file path/to/your/legal_document.txt --output-file path/to/cleaned_document.txt --citation-strategy remove
```

**Additional Options:**

```bash
# Remove all digits from the final output
python main.py --input-file path/to/legal_document.txt --remove-digits

# Remove all URLs from the final output
python main.py --input-file path/to/legal_document.txt --remove-urls

# Use multiple filters together
python main.py --input-file path/to/legal_document.txt --remove-digits --remove-urls --citation-strategy replace
```

**Basic Python usage (Example):**

```python
from input_handler import load_text
from citation_filter import filter_citations
from nlp_cleaner import clean_text
from tts_preparator import prepare_for_tts

# Load text
raw_text = load_text("path/to/your/legal_document.txt")

# Process text
citation_filtered_text = filter_citations(raw_text, strategy="remove") # or 'replace'
nlp_cleaned_text = clean_text(citation_filtered_text, model="en_core_web_sm")
final_text = prepare_for_tts(nlp_cleaned_text, remove_digits=True, remove_urls=True)  # Remove digits and URLs

# Use the final_text with your TTS system
print(final_text)
```

*See `main.py` or specific module documentation for more detailed usage and configuration options.*

## Contributing

Contributions are welcome! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes and commit them (`git commit -m 'Add some feature'`).
4.  Push to the branch (`git push origin feature/your-feature-name`).
5.  Open a Pull Request.

Please ensure your code adheres to PEP 8 guidelines and includes relevant tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 