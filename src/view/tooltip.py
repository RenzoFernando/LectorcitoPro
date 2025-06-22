# src/view/tooltip.py

import customtkinter as ctk


class CustomTooltip:
    """
    Crea un tooltip mejorado y estilizado para cualquier widget de customtkinter.

    Este tooltip aparece con un retraso y una animación suave de entrada (fade-in),
    y su apariencia se adapta al tema claro/oscuro de la aplicación.

    Uso:
        my_button = ctk.CTkButton(master, text="Botón")
        CustomTooltip(my_button, text="Este es un tooltip útil.")
    """

    def __init__(self, widget, text: str):
        """
        Inicializa el tooltip.

        Args:
            widget: El widget al que se adjuntará el tooltip.
            text (str): El texto que mostrará el tooltip.
        """
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.id = None
        self.x = self.y = 0

        # Vincular los eventos de ratón al widget para mostrar/ocultar el tooltip.
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)  # Ocultar si se hace clic en el widget.

    def enter(self, event=None):
        """
        Se activa cuando el cursor del ratón entra en el área del widget.
        Programa la aparición del tooltip después de un breve retraso.
        """
        self.schedule_tooltip()

    def leave(self, event=None):
        """
        Se activa cuando el cursor del ratón sale del área del widget.
        Cancela la aparición programada del tooltip y lo oculta si ya es visible.
        """
        self.hide_tooltip()

    def schedule_tooltip(self):
        """Programa la función show_tooltip para que se ejecute después de 500ms."""
        self.id = self.widget.after(500, self.show_tooltip)

    def show_tooltip(self, event=None):
        """Crea y muestra la ventana del tooltip en la posición correcta con un diseño mejorado."""
        if self.tooltip_window:
            return

        # Posicionar el tooltip cerca del cursor
        x = self.widget.winfo_pointerx() + 15
        y = self.widget.winfo_pointery() + 10

        # Crear una ventana Toplevel sin decoraciones de sistema operativo
        self.tooltip_window = ctk.CTkToplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)

        # --- CORRECCIÓN DEL ERROR DE TRANSPARENCIA ---
        # 1. Definimos un color "chroma key" que será transparente.
        transparent_color = '#E532F1'  # Un color fucsia improbable.

        # 2. Configuramos la ventana para que use ese color de fondo.
        self.tooltip_window.configure(fg_color=transparent_color)

        # 3. Le decimos al gestor de ventanas que haga transparente ese color.
        self.tooltip_window.wm_attributes("-transparentcolor", transparent_color)

        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        self.tooltip_window.attributes("-topmost", "true")
        self.tooltip_window.attributes("-alpha", 0)  # Inicia transparente para el fade-in

        # --- Paleta de colores y diseño final refinado ---
        current_theme = ctk.get_appearance_mode()
        if current_theme == "Dark":
            bg_color = "#323232"  # Gris oscuro sutil
            text_color = "#D3D3D3"  # Texto gris claro para menor contraste y más comodidad
        else:
            bg_color = "#F5F5F5"  # Blanco hueso para un look suave
            text_color = "#2E2E2E"  # Gris muy oscuro en lugar de negro puro

        # Frame principal del tooltip con el nuevo diseño sin borde y más ajustado
        frame = ctk.CTkFrame(self.tooltip_window,
                             fg_color=bg_color,
                             border_width=0,  # Eliminamos el borde
                             corner_radius=14)  # Un radio que crea una forma de píldora perfecta
        frame.pack()

        # Etiqueta de texto con padding reducido para un ajuste más ceñido
        label = ctk.CTkLabel(frame,
                             text=self.text,
                             font=("Segoe UI", 9, "normal"),  # Fuente limpia y estándar
                             text_color=text_color,
                             wraplength=220,
                             justify="center")
        label.pack(padx=10, pady=5)  # Padding reducido para que sea más compacto

        # Iniciar la animación de fade-in
        self.fade_in()

    def hide_tooltip(self):
        """Cancela la aparición y destruye la ventana del tooltip si existe."""
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None

        if self.tooltip_window:
            # Se podría añadir un fade-out, pero para tooltips la desaparición instantánea es común.
            self.tooltip_window.destroy()
            self.tooltip_window = None

    def fade_in(self):
        """Realiza la animación de aparición gradual (fade-in)."""
        if not self.tooltip_window or not self.tooltip_window.winfo_exists():
            return

        alpha = self.tooltip_window.attributes("-alpha")
        if alpha < 0.95:  # Ligeramente menos de 1 para un look más suave
            alpha = min(alpha + 0.1, 0.95)
            self.tooltip_window.attributes("-alpha", alpha)
            self.tooltip_window.after(15, self.fade_in)
