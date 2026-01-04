def safe_title(text: str) -> str:
    return text.strip().title() if isinstance(text, str) else ""
