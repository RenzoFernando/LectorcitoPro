import customtkinter as ctk


# Crea un tooltip personalizado y estilizado para widgets.
class CustomTooltip:

    # Inicializa el tooltip y lo asocia a un widget.
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.x = self.y = 0

        # Asocia los eventos del ratón para mostrar y ocultar el tooltip.
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)

    # Se ejecuta cuando el cursor entra en el widget.
    def enter(self, event=None):
        self.schedule_tooltip()

    # Se ejecuta cuando el cursor sale del widget.
    def leave(self, event=None):
        self.hide_tooltip()

    # Programa la aparición del tooltip después de un breve retraso.
    def schedule_tooltip(self):
        self.id = self.widget.after(500, self.show_tooltip)

    # Crea y muestra la ventana del tooltip.
    def show_tooltip(self, event=None):
        if self.tooltip_window:
            return

        x = self.widget.winfo_pointerx() + 15
        y = self.widget.winfo_pointery() + 10

        # Crea una ventana sin bordes.
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)

        # Técnica para lograr bordes redondeados en ventanas sin marco.
        transparent_color = '#E532F1'
        self.tooltip_window.configure(fg_color=transparent_color)
        self.tooltip_window.wm_attributes("-transparentcolor", transparent_color)

        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", "true")
        self.tooltip_window.attributes("-alpha", 0)

        # Adapta el color del tooltip al tema actual de la aplicación.
        current_theme = ctk.get_appearance_mode()
        if current_theme == "Dark":
            bg_color = "#323232"
            text_color = "#D3D3D3"
        else:
            bg_color = "#F5F5F5"
            text_color = "#2E2E2E"

        # Frame principal que contiene el texto del tooltip.
        frame = ctk.CTkFrame(self.tooltip_window,
                             fg_color=bg_color,
                             border_width=0,
                             corner_radius=14)
        frame.pack()

        label = ctk.CTkLabel(frame,
                             text=self.text,
                             font=("Segoe UI", 9, "normal"),
                             text_color=text_color,
                             wraplength=220,
                             justify="center")
        label.pack(padx=10, pady=5)

        # Inicia la animación de aparición.
        self.fade_in()

    # Oculta y destruye la ventana del tooltip.
    def hide_tooltip(self):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

    # Anima la aparición gradual del tooltip.
    def fade_in(self):
        if not self.tooltip_window or not self.tooltip_window.winfo_exists():
            return

        alpha = self.tooltip_window.attributes("-alpha")
        if alpha < 0.95:
            alpha = min(alpha + 0.1, 0.95)
            self.tooltip_window.attributes("-alpha", alpha)
            self.tooltip_window.after(15, self.fade_in)