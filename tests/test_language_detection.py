#!/usr/bin/env python3
"""
Test script to verify language detection for various inputs including Hinglish
"""

import re
from langdetect import detect, LangDetectException

# Copy the language detection functions from main.py
def is_hinglish(text: str) -> bool:
    """
    Detect if the text contains a mix of Hindi (Devanagari script) and English (Latin script)
    Returns True if both scripts are present, indicating Hinglish
    """
    # Check for Devanagari script (Hindi)
    has_hindi = bool(re.search(r'[\u0900-\u097F]', text))
    # Check for Latin script (English)
    has_english = bool(re.search(r'[a-zA-Z]', text))
    return has_hindi and has_english

def is_romanized_hinglish(text: str) -> bool:
    """
    Detect romanized Hinglish (Hindi written in Latin script mixed with English)
    Looks for common Hindi words written in Latin script
    """
    # Common Hinglish words/patterns (romanized Hindi)
    hinglish_keywords = [
        'mein', 'main', 'hai', 'hain', 'kya', 'kaise', 'ke', 'ki', 
        'aur', 'ka', 'ko', 'se', 'par', 'liye', 'chahiye', 'chahie',
        'karna', 'hona', 'tha', 'thi', 'the', 'ho', 'kare', 'karo',
        'nahi', 'nahin', 'kyun', 'kyu', 'kab', 'kahan', 'yahan', 'vahan',
        'mujhe', 'tumhe', 'humne', 'unhe', 'iske', 'uske',
        'fasal', 'kheti', 'barish', 'mausam', 'pani'
    ]
    
    text_lower = text.lower()
    # Check if text contains multiple Hinglish keywords
    matches = sum(1 for keyword in hinglish_keywords if keyword in text_lower)
    return matches >= 2  # At least 2 Hinglish words

def detect_user_language(text: str) -> tuple[str, str]:
    """
    Detect the user's language from input text.
    Returns: (language_code, language_name)
    Special handling for Hinglish (Hindi+English mix)
    """
    # Language mapping
    languages = {
        'en': 'English',
        'hi': 'Hindi',
        'tl': 'Filipino (Tagalog)',
        'es': 'Spanish',
        'fr': 'French',
        # Add more as needed
    }
    
    # First check if it's Hinglish with Devanagari script
    if is_hinglish(text):
        return 'hi-en', 'Hinglish (Hindi and English)'
    
    # Check if it's romanized Hinglish (no Devanagari but Hindi words in Latin)
    if is_romanized_hinglish(text):
        return 'hi-en', 'Hinglish (Hindi and English)'
    
    try:
        detected_code = detect(text)
        
        # If detected as Tagalog/Filipino, Swahili, or Indonesian, it might be romanized Hinglish
        # These languages are commonly confused with romanized Hindi
        if detected_code in ['tl', 'sw', 'id', 'so']:
            # Check if there are any Hindi characters
            has_hindi = bool(re.search(r'[\u0900-\u097F]', text))
            if has_hindi:
                return 'hi', 'Hindi'
            # Check for romanized Hinglish patterns
            if is_romanized_hinglish(text):
                return 'hi-en', 'Hinglish (Hindi and English)'
            # Otherwise default to English as these are often misdetections
            return 'en', 'English'
        
        # For Hindi detection, verify it's actually Hindi
        if detected_code == 'hi':
            has_hindi_script = bool(re.search(r'[\u0900-\u097F]', text))
            if not has_hindi_script:
                # No Hindi script but detected as Hindi - probably English or romanized Hinglish
                if is_romanized_hinglish(text):
                    return 'hi-en', 'Hinglish (Hindi and English)'
                return 'en', 'English'
        
        language_name = languages.get(detected_code, 'English')
        return detected_code, language_name
        
    except LangDetectException:
        # If detection fails, check for romanized Hinglish
        if is_romanized_hinglish(text):
            return 'hi-en', 'Hinglish (Hindi and English)'
        # Otherwise default to English
        return 'en', 'English'


# Test cases
test_cases = [
    # Hinglish examples
    "Siwan mein mustard ki fasal ke liye kya karna chahiye?",
    "मुझे Siwan में mustard farming के बारे में बताओ",
    "What are the best practices for गेहूं की खेती in Bihar?",
    
    # Pure Hindi
    "सिवान में सरसों की खेती के लिए क्या करना चाहिए?",
    
    # Pure English
    "What are the climate problems in Siwan for mustard farming?",
    
    # Other potentially confusing cases
    "Tell me about climate in Siwan",
    "मौसम कैसा है आज"
]

print("=" * 80)
print("Language Detection Test Results")
print("=" * 80)

# Define patterns outside f-strings to avoid backslash issues
hindi_pattern = r'[\u0900-\u097F]'
english_pattern = r'[a-zA-Z]'

for test_text in test_cases:
    print(f"\nTest Input: {test_text}")
    has_hindi = bool(re.search(hindi_pattern, test_text))
    has_english = bool(re.search(english_pattern, test_text))
    print(f"  Has Hindi script: {has_hindi}")
    print(f"  Has English script: {has_english}")
    
    try:
        raw_detect = detect(test_text)
        print(f"  Raw langdetect: {raw_detect}")
    except Exception as e:
        print(f"  Raw langdetect: Error - {e}")
    
    code, name = detect_user_language(test_text)
    print(f"  ✓ Detected: {code} - {name}")

print("\n" + "=" * 80)
print("Test complete!")
print("=" * 80)
