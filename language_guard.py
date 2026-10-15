"""Fast script validation; semantic language checks belong to SpellingAgent."""
import unicodedata
ERROR = 'אפשר לכתוב רק בעברית או באנגלית. Please use Hebrew or English only.'

def validate_script(text):
    for c in unicodedata.normalize('NFC', text):
        category=unicodedata.category(c)
        if category.startswith('L'):
            if not ('a' <= c.lower() <= 'z' or 'HEBREW' in unicodedata.name(c,'')):
                raise ValueError(ERROR)
        elif category.startswith('M'):
            if not ('HEBREW' in unicodedata.name(c,'') or ord(c) in (0xFE0E,0xFE0F,0x20E3)):
                raise ValueError(ERROR)
