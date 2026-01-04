def safe_title(text: str | None) -> str:
    if not text:
        return ""
    return text.strip().title()
