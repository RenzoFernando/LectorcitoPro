def safe_title(text: str | None) -> str:
    """Return a title-cased string, safely handling None or empty inputs."""
    if not text:
        return ""
    return text.strip().title()
