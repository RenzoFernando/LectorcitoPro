from core.constants import COLORS


def toggle_theme(current_theme: str) -> str:
    return "Dark" if current_theme == "Light" else "Light"


def get_sidebar_colors(is_light: bool) -> tuple[str, str]:
    btn_fg_color = COLORS["dark"]["bg"] if is_light else COLORS["light"]["bg"]
    btn_hover_color = COLORS["sidebar_hover"]["light"] if is_light else COLORS["sidebar_hover"]["dark"]
    return btn_fg_color, btn_hover_color
