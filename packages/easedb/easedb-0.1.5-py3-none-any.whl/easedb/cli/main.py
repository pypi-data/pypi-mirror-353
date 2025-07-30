import argparse
import sys
from .utils import load_language
from .commands import run_cli_menu

def main(lang_code='en'):
    """
    Main entry point for the Easedb CLI.
    
    Args:
        lang_code (str, optional): Language code. Defaults to 'en'.
    """
    # Load language translations
    lang = load_language(lang_code)
    
    # Run the CLI menu
    run_cli_menu(lang)

if __name__ == "__main__":
    # Allow language selection via environment variable or default to English
    language = 'en'
    
    # Check if a language is specified via command-line argument
    if len(sys.argv) > 1:
        language = sys.argv[1]
    
    main(language)
