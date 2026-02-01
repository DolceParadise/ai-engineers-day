"""Language detection utilities for multi-lingual support."""

import re
from typing import Tuple
from langdetect import detect, LangDetectException
from datasets.languages import languages


def is_hinglish(text: str) -> bool:
    """
    Detect if the text contains a mix of Hindi (Devanagari script) and English (Latin script).
    
    Args:
        text: The input text to analyze
        
    Returns:
        True if both Devanagari and Latin scripts are present, False otherwise
    """
    has_hindi = bool(re.search(r'[\u0900-\u097F]', text))
    has_english = bool(re.search(r'[a-zA-Z]', text))
    return has_hindi and has_english


def is_romanized_hinglish(text: str) -> bool:
    """
    Detect romanized Hinglish (Hindi written in Latin script mixed with English).
    
    Args:
        text: The input text to analyze
        
    Returns:
        True if at least 2 Hinglish keywords are found, False otherwise
    """
    hinglish_keywords = [
        'mein', 'main', 'hai', 'hain', 'kya', 'kaise', 'ke', 'ki',
        'aur', 'ka', 'ko', 'se', 'par', 'liye', 'chahiye', 'chahie',
        'karna', 'hona', 'tha', 'thi', 'the', 'ho', 'kare', 'karo',
        'nahi', 'nahin', 'kyun', 'kyu', 'kab', 'kahan', 'yahan', 'vahan',
        'mujhe', 'tumhe', 'humne', 'unhe', 'iske', 'uske',
        'fasal', 'kheti', 'barish', 'mausam', 'pani'
    ]

    text_lower = text.lower()
    matches = sum(1 for keyword in hinglish_keywords if keyword in text_lower)
    return matches >= 2


def detect_user_language(text: str) -> Tuple[str, str]:
    """
    Detect the user's language from input text.
    
    Special handling for Hinglish (Hindi+English mix) and romanized variations.
    
    Args:
        text: The input text to analyze
        
    Returns:
        Tuple of (language_code, language_name)
    """
    # Check if it's Hinglish with Devanagari script
    if is_hinglish(text):
        return 'hi-en', 'Hinglish (Hindi and English)'

    # Check if it's romanized Hinglish
    if is_romanized_hinglish(text):
        return 'hi-en', 'Hinglish (Hindi and English)'

    try:
        detected_code = detect(text)

        # Handle commonly confused language detections
        if detected_code in ['tl', 'sw', 'id', 'so']:
            has_hindi = bool(re.search(r'[\u0900-\u097F]', text))
            if has_hindi:
                return 'hi', 'Hindi'
            if is_romanized_hinglish(text):
                return 'hi-en', 'Hinglish (Hindi and English)'
            return 'en', 'English'

        # Verify Hindi detection
        if detected_code == 'hi':
            has_hindi_script = bool(re.search(r'[\u0900-\u097F]', text))
            if not has_hindi_script:
                if is_romanized_hinglish(text):
                    return 'hi-en', 'Hinglish (Hindi and English)'
                return 'en', 'English'

        language_name = languages.get(detected_code, 'English')
        return detected_code, language_name

    except LangDetectException:
        if is_romanized_hinglish(text):
            return 'hi-en', 'Hinglish (Hindi and English)'
        return 'en', 'English'
