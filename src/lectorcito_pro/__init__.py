from __future__ import annotations

import sys


def _alias(name: str, module) -> None:
    sys.modules.setdefault(name, module)


try:
    from .config import store as _config
    _alias("config", _config)
except Exception:
    pass

try:
    from . import utils as _utils
    _alias("utils", _utils)
except Exception:
    pass

try:
    from . import ui as _ui
    _alias("view", _ui)
except Exception:
    pass
