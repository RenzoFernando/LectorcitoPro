def safe_title(text: str | None) -> str:
    return text.strip().title() if text is not None else ""
