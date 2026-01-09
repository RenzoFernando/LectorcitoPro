from __future__ import annotations

"""Adaptador UI para settings.

La UI real sigue en `ui/app_window/bindings.py`.
Este módulo ofrece helpers para manipular el dict de configuración sin acoplarlo
a widgets específicos.
"""

from ..application.update_language import toggle_language
from ..application.update_theme import toggle_theme
from ..application.update_filters import normalize_extension_tags


class SettingsUIController:
    def toggle_theme(self, current_theme: str) -> str:
        return toggle_theme(current_theme)

    def toggle_language(self, current_lang: str) -> str:
        return toggle_language(current_lang)

    def normalize_extensions(self, tags: list[dict]) -> list[dict]:
        return normalize_extension_tags(tags)
