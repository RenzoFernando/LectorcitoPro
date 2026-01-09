from __future__ import annotations

"""Compatibilidad con versiones anteriores.

En versiones anteriores del proyecto, `resource_path` vivía en `utils.py`.
En la arquitectura actual, la fuente de verdad está en `lectorcito_pro.core.paths`.

Este módulo re-exporta la función para no romper imports antiguos.
"""

from .core.paths import resource_path  # noqa: F401
