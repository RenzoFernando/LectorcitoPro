from __future__ import annotations

from ....i18n.locale import toggle_language as _toggle_language


def toggle_language(current_lang: str) -> str:
    """Alterna entre 'es' y 'en'.

    Se delega a `i18n.locale.toggle_language` para centralizar la regla.
    """
    return _toggle_language(current_lang)
