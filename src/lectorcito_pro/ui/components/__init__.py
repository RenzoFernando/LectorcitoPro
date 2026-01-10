"""UI Components (Atomic Design).

Esta capa permite construir la UI en piezas reutilizables:
- atoms
- molecules
- organisms
- pages

La ventana principal usa estos componentes para mantener el código escalable.
"""

from .pages.home_page import HomePage
from .organisms.header import Header
from .organisms.footer import Footer
from .organisms.progress_panel import ProgressPanel
from .molecules.sidebar import LeftSidebar, RightSidebar
from .molecules.tag_pills import TagPillsEditor
