import os
import json
import sys

def load_language(lang_code='en'):
    """
    Load language translations from JSON file.
    
    Args:
        lang_code (str, optional): Language code. Defaults to 'en'.
    
    Returns:
        dict: Loaded language translations
    """
    # Determine the path to the language file
    base_path = os.path.dirname(os.path.abspath(__file__))
    lang_file_path = os.path.join(base_path, 'i18n', f'{lang_code}.json')
    
    try:
        with open(lang_file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[WARNING] Language file for '{lang_code}' not found. Falling back to English.")
        # Fallback to English
        fallback_path = os.path.join(base_path, 'i18n', 'en.json')
        try:
            with open(fallback_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("[ERROR] Default English language file not found.")
            # Return a minimal dictionary to prevent KeyError
            return {
                "title": "EaseDB CLI",
                "create_database": "Create Database",
                "start_database": "Start Database",
                "stop_database": "Stop Database", 
                "delete_database": "Delete Database",
                "install_docker": "Install Docker",
                "exit": "Exit",
                "choose_option": "Enter your choice: ",
                "invalid_option": "Invalid option, please try again.",
                "goodbye": "Goodbye!"
            }
    except json.JSONDecodeError:
        print(f"[ERROR] Invalid JSON in language file: {lang_file_path}")
        # Return a minimal dictionary to prevent KeyError
        return {
            "title": "EaseDB CLI",
            "create_database": "Create Database",
            "start_database": "Start Database",
            "stop_database": "Stop Database", 
            "delete_database": "Delete Database",
            "install_docker": "Install Docker",
            "exit": "Exit",
            "choose_option": "Enter your choice: ",
            "invalid_option": "Invalid option, please try again.",
            "goodbye": "Goodbye!"
        }
