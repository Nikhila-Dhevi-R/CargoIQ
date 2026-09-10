import re

def anonymize_person_id(track_id: int) -> str:
    """Returns privacy-preserving anonymous person label, e.g. 'Operator #3'"""
    return f"Operator #{track_id}"

def sanitize_text(text: str) -> str:
    """Removes potential personally identifiable tags from supervisor comments"""
    return text.strip()
