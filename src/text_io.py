from pathlib import Path

from app_logging import log_warning

_UTF8_BOM = b"\xef\xbb\xbf"
_UTF16_LE_BOM = b"\xff\xfe"
_UTF16_BE_BOM = b"\xfe\xff"
_UTF32_LE_BOM = b"\xff\xfe\x00\x00"
_UTF32_BE_BOM = b"\x00\x00\xfe\xff"

def read_text_file(file_path: str) -> str:
    raw = Path(file_path).read_bytes()

    if raw.startswith(_UTF32_LE_BOM) or raw.startswith(_UTF32_BE_BOM):
        return raw.decode("utf-32")
    if raw.startswith(_UTF8_BOM):
        return raw.decode("utf-8-sig")
    if raw.startswith(_UTF16_LE_BOM) or raw.startswith(_UTF16_BE_BOM):
        return raw.decode("utf-16")

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        pass

    for encoding in ("cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            log_warning(
                f"Se utilizó encoding alternativo: {encoding}",
                operation="read_text_file",
                file_path=str(file_path)
            )
            return text
        except UnicodeDecodeError:
            continue

    text = raw.decode("utf-8", errors="replace")
    log_warning(
        "Se utilizó UTF-8 con reemplazo de caracteres inválidos.",
        operation="read_text_file",
        file_path=str(file_path)
    )
    return text
