import customtkinter as ctk


def set_theme(theme_name: str) -> None:
    """Setea tema global de CustomTkinter (Light/Dark/System)."""
    try:
        ctk.set_appearance_mode(theme_name)
    except Exception:
        # No romper ejecución por un tema inválido; la vista maneja su tema internamente.
        pass
