import customtkinter as ctk
import os
from tkinter import filedialog
from PIL import Image
from utils import resource_path

# Paleta de colores centralizada para consistencia en los diálogos.
COLORS = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"blue_h": "#3073A8", "green_h": "#2FA047", "red_h": "#A03031"},
    "sidebar_hover": {"light": "#3C3C3C", "dark": "#DCDCDC"},
    "progress_colors": {"start": "#3B8ED0", "mid": "#F9A825", "done": "#4CAF50"},
    "list_item": {"selected_bg": "#3B8ED0", "normal_bg": "transparent"}
}

MESSAGE_AUTO_CLOSE_SECONDS = 5

# Clase base para todos los diálogos con animaciones de entrada y salida.
class BaseDialog(ctk.CTkToplevel):

    # Configura la ventana base del diálogo (título, posición, etc.).
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.resizable(False, False)
        self.attributes("-alpha", 0.0)

        # --- Flags de cierre seguro ---
        self._closing_grab_released = False

        # --- Escape robusto (funciona aunque un widget "se coma" el evento) ---
        # Creamos un bindtag único para este diálogo y lo ponemos primero en todos los widgets hijos.
        self._escape_bindtag = f"__esc_close_{id(self)}"
        try:
            # Se ejecuta antes que el bind de clase del widget (por eso ahora sí funciona siempre).
            self.bind_class(self._escape_bindtag, "<Escape>", self._on_escape_key, add="+")
        except Exception:
            # Fallback por si algo raro ocurre con bind_class (muy poco probable).
            self.bind("<Escape>", self._on_escape_key, add="+")

        # Instala el bindtag en el toplevel y todos los hijos cuando ya existan.
        self.bind("<Map>", self._install_escape_bindtags, add="+")
        self.after(120, self._install_escape_bindtags)
        self.after(350, self._install_escape_bindtags)

        # Intenta establecer el icono de la ventana heredado de la ventana padre.
        def _set_icon():
            try:
                if hasattr(parent, '_icon_path') and parent._icon_path and os.path.exists(parent._icon_path):
                    self.iconbitmap(parent._icon_path)
            except Exception as e:
                print(f"Error al establecer el icono de la sub-ventana: {e}")

        # Se restaura el tiempo original para cargar el icono.
        self.after(200, _set_icon)

        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)

        # La lógica de centrado ahora se llama con un retardo para garantizar que
        # la ventana tenga sus dimensiones finales antes de calcular la posición.
        self.after(100, self._center_and_fade_in)

    # ---------------------------
    # Escape: cierre tipo "X"
    # ---------------------------
    def _on_escape_key(self, event=None):
        self._close_with_fade_out()
        return "break"

    def _install_escape_bindtags(self, event=None):
        """Inserta el bindtag de Escape al inicio de bindtags en este diálogo y todos sus hijos."""
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        def apply_tag(widget):
            try:
                tags = list(widget.bindtags())
            except Exception:
                return

            if self._escape_bindtag not in tags:
                # Lo ponemos primero para que se ejecute ANTES que el bind de clase del widget.
                tags.insert(0, self._escape_bindtag)
                try:
                    widget.bindtags(tuple(tags))
                except Exception:
                    pass

            # Recorre hijos
            try:
                for child in widget.winfo_children():
                    apply_tag(child)
            except Exception:
                pass

        apply_tag(self)

    # ---------------------------
    # Animaciones / Posicionamiento
    # ---------------------------

    # Rutina que centra la ventana y luego inicia la animación.
    def _center_and_fade_in(self):
        try:
            self.grab_set()
            self._center_window()

            # --- NUEVO: activar y enfocar la subventana (Windows a veces no da foco solo) ---
            def _activate():
                try:
                    if not self.winfo_exists():
                        return

                    # asegurar que esté visible y arriba
                    try:
                        self.deiconify()
                    except Exception:
                        pass

                    # traer al frente y forzar foco
                    try:
                        self.lift()
                    except Exception:
                        pass

                    try:
                        self.focus_force()
                        self.focus_set()
                    except Exception:
                        pass

                    # Truco típico en Windows: toggle -topmost por un instante para que el SO la "active"
                    try:
                        self.attributes("-topmost", True)
                        self.after(10, lambda: self.winfo_exists() and self.attributes("-topmost", False))
                    except Exception:
                        pass

                except Exception:
                    pass

            # Haz varios intentos cortos (Windows puede ignorar el primero)
            _activate()
            self.after(40, _activate)
            self.after(140, _activate)

            self._fade_in()

        except Exception:
            # Si la ventana se cierra antes de que este método se ejecute,
            # puede ocurrir un error. Es seguro ignorarlo.
            pass

    # Centra el diálogo con respecto a la ventana principal.
    def _center_window(self):
        self.update_idletasks()
        parent_x = self.master.winfo_x()
        parent_y = self.master.winfo_y()
        parent_width = self.master.winfo_width()
        parent_height = self.master.winfo_height()

        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()

        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2

        self.geometry(f"+{x}+{y}")

    # Anima la aparición gradual del diálogo.
    def _fade_in(self):
        alpha = self.attributes("-alpha")
        if alpha < 1:
            alpha = min(alpha + 0.1, 1.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._fade_in)

    # Anima la desaparición gradual del diálogo y lo destruye.
    def _close_with_fade_out(self, event=None):
        # Libera el grab solo una vez (evita errores si se llama varias veces).
        if not self._closing_grab_released:
            try:
                self.grab_release()
            except Exception:
                pass
            self._closing_grab_released = True

        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha = max(alpha - 0.1, 0.0)
            self.attributes("-alpha", alpha)
            self.after(15, self._close_with_fade_out)
        else:
            self.destroy()

    # Maneja el evento de confirmación (botón OK, Enter).
    def _on_ok(self, event=None):
        self._close_with_fade_out()

    # Maneja el evento de cancelación.
    def _on_cancel(self, event=None):
        self.result = None
        self._close_with_fade_out()


# Diálogo simple para mostrar un mensaje con un botón de "OK".
class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)

        # --- Timer de autocierre ---
        self._auto_close_after_id = None
        self._schedule_auto_close()

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(
            main_frame,
            text=message,
            wraplength=350,
            justify="center",
            font=("Segoe UI", 13)
        ).pack(fill="x", pady=(0, 20))

        ok_button = ctk.CTkButton(
            main_frame,
            text="OK",
            width=100,
            command=self._on_ok,
            fg_color=COLORS["button"]["blue"],
            hover_color=COLORS["button_hover"]["blue_h"],
        )
        ok_button.pack(pady=(0, 10))
        ok_button.focus_set()

        self.bind("<Return>", self._on_ok)

    # ---------------------------
    # Auto-cierre
    # ---------------------------
    def _schedule_auto_close(self):
        """Programa el autocierre según MESSAGE_AUTO_CLOSE_SECONDS."""
        self._cancel_auto_close()

        try:
            seconds = float(MESSAGE_AUTO_CLOSE_SECONDS)
        except Exception:
            seconds = 0.0

        if seconds <= 0:
            return

        ms = max(1, int(seconds * 1000))
        self._auto_close_after_id = self.after(ms, self._auto_close)

    def _cancel_auto_close(self):
        """Cancela el autocierre si estaba programado."""
        if self._auto_close_after_id is None:
            return
        try:
            self.after_cancel(self._auto_close_after_id)
        except Exception:
            pass
        self._auto_close_after_id = None

    def _auto_close(self):
        """Cierra el diálogo si sigue abierto y nadie lo cerró manualmente."""
        self._auto_close_after_id = None
        try:
            if not self.winfo_exists():
                return
        except Exception:
            return

        # No marcar como OK; solo cerrar.
        self.result = None
        self._close_with_fade_out()

    # ---------------------------
    # Overrides para limpiar timer
    # ---------------------------
    def _close_with_fade_out(self, event=None):
        # Si el usuario cierra con X/Esc o el OK, cancelamos el timer.
        self._cancel_auto_close()
        return super()._close_with_fade_out(event)

    def _on_ok(self, event=None):
        self._cancel_auto_close()
        self.result = True
        super()._on_ok(event)


# Diálogo de confirmación con opciones "Sí" y "No".
class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, justify="center", font=("Segoe UI", 13)).pack(fill="x",
                                                                                                             pady=(0,
                                                                                                                   20))
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.pack()

        ctk.CTkButton(button_frame, text="Sí", width=100, command=self._on_yes, fg_color=COLORS['button']['green'],
                      hover_color=COLORS['button_hover']['green_h']).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="No", width=100, command=self._on_no, fg_color=COLORS['button']['red'],
                      hover_color=COLORS['button_hover']['red_h']).pack(side="left", padx=10)

    def _on_yes(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_no(self, event=None): self.result = False; self._close_with_fade_out()

    # Método de clase para mostrar el diálogo y esperar una respuesta.
    @classmethod
    def ask(cls, parent, title, message):
        dialog = cls(parent, title, message)
        parent.wait_window(dialog)
        return dialog.result


# Diálogo que presenta dos opciones personalizables.
class ChoiceDialog(BaseDialog):
    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value, self.option2_value = option1_value, option2_value
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        ctk.CTkLabel(main_frame, text=message, wraplength=350, font=("Segoe UI", 13)).pack(fill="x", pady=(0, 20))
        ctk.CTkButton(main_frame, text=option1_text, width=220, command=self._on_option1,
                      fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h']).pack(pady=5)
        ctk.CTkButton(main_frame, text=option2_text, width=220, command=self._on_option2,
                      fg_color=COLORS['button']['blue'], hover_color=COLORS['button_hover']['blue_h']).pack(pady=5)

    def _on_option1(self): self.result = self.option1_value; super()._on_ok()

    def _on_option2(self): self.result = self.option2_value; super()._on_ok()

    # Método de clase para mostrar el diálogo y devolver el valor de la opción elegida.
    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
        parent.wait_window(dialog)
        return dialog.result


# Diálogo para seleccionar, ordenar y eliminar múltiples rutas de carpetas.
class SelectFoldersDialog(BaseDialog):
    def __init__(self, parent, title):
        super().__init__(parent, title)
        self.geometry("500x400")
        self.selected_paths = []
        self._parent = parent
        self.list_item_widgets = []
        self.currently_selected_index = -1

        # Construcción de la interfaz del diálogo.
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(expand=True, fill="both", padx=15, pady=15)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        ctk.CTkButton(top_frame, text=self._parent._tr("dlg_multi_add"), command=self._add_folder).pack(side="left")

        list_area_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        list_area_frame.grid(row=1, column=0, sticky="nsew")
        list_area_frame.grid_columnconfigure(0, weight=1)
        list_area_frame.grid_rowconfigure(0, weight=1)

        self.scrollable_frame = ctk.CTkScrollableFrame(list_area_frame,
                                                       label_text=self._parent._tr("dlg_multi_list_title"))
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")

        reorder_button_frame = ctk.CTkFrame(list_area_frame, fg_color="transparent")
        reorder_button_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        ctk.CTkButton(reorder_button_frame, text="▲", width=30, command=self._move_up).pack(pady=2)
        ctk.CTkButton(reorder_button_frame, text="▼", width=30, command=self._move_down).pack(pady=2)
        ctk.CTkButton(reorder_button_frame, text="✕", width=30, command=self._remove_selected_folder,
                      fg_color=COLORS['button']['red'], hover_color=COLORS['button_hover']['red_h']).pack(pady=(10, 2))

        bottom_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_button_frame.grid(row=2, column=0, sticky="e", pady=(15, 0))
        ctk.CTkButton(bottom_button_frame, text=self._parent._tr("btn_cancel"), command=self._on_cancel,
                      fg_color=COLORS['button']['red'], hover_color=COLORS['button_hover']['red_h']).pack(side="left",
                                                                                                          padx=10)
        ctk.CTkButton(bottom_button_frame, text=self._parent._tr("dlg_multi_process"), command=self._on_process,
                      fg_color=COLORS['button']['green'], hover_color=COLORS['button_hover']['green_h']).pack(
            side="left")

        self._update_folder_list()

    # Redibuja la lista de carpetas seleccionadas.
    def _update_folder_list(self):
        for widget in self.list_item_widgets: widget.destroy()
        self.list_item_widgets.clear()

        if not self.selected_paths:
            label = ctk.CTkLabel(self.scrollable_frame, text=self._parent._tr("dlg_multi_empty"), text_color="gray")
            label.pack(pady=10)
            self.list_item_widgets.append(label)
        else:
            for i, path in enumerate(self.selected_paths):
                is_selected = (i == self.currently_selected_index)
                fg_color = COLORS['list_item']['selected_bg'] if is_selected else COLORS['list_item']['normal_bg']

                item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=fg_color, corner_radius=6)
                item_frame.pack(fill="x", padx=5, pady=3)
                label = ctk.CTkLabel(item_frame, text=f"{i + 1}. {path}", anchor="w", compound="left", padx=10,
                                     font=("Segoe UI", 10))
                label.pack(fill="x")

                item_frame.bind("<Button-1>", lambda e, index=i: self._on_item_select(index))
                label.bind("<Button-1>", lambda e, index=i: self._on_item_select(index))
                self.list_item_widgets.append(item_frame)

    # Maneja la selección de un elemento en la lista.
    def _on_item_select(self, index):
        self.currently_selected_index = index
        self._update_folder_list()

    # Añade una nueva carpeta a la lista.
    def _add_folder(self):
        path = filedialog.askdirectory(title=self._parent._tr("dlg_multi_add_title"))
        if path and path not in self.selected_paths:
            self.selected_paths.append(path)
            self.currently_selected_index = len(self.selected_paths) - 1
            self._update_folder_list()

    # Elimina la carpeta actualmente seleccionada.
    def _remove_selected_folder(self):
        if 0 <= self.currently_selected_index < len(self.selected_paths):
            self.selected_paths.pop(self.currently_selected_index)
            self.currently_selected_index = -1
            self._update_folder_list()

    # Mueve la carpeta seleccionada una posición hacia arriba.
    def _move_up(self):
        if 0 < self.currently_selected_index < len(self.selected_paths):
            idx = self.currently_selected_index
            self.selected_paths[idx], self.selected_paths[idx - 1] = self.selected_paths[idx - 1], self.selected_paths[
                idx]
            self.currently_selected_index -= 1
            self._update_folder_list()

    # Mueve la carpeta seleccionada una posición hacia abajo.
    def _move_down(self):
        if -1 <= self.currently_selected_index < len(self.selected_paths) - 1:
            idx = self.currently_selected_index
            self.selected_paths[idx], self.selected_paths[idx + 1] = self.selected_paths[idx + 1], self.selected_paths[
                idx]
            self.currently_selected_index += 1
            self._update_folder_list()

    # Confirma la selección de carpetas y cierra el diálogo.
    def _on_process(self):
        if self.selected_paths:
            self.result = self.selected_paths
        else:
            self.result = None
        self._close_with_fade_out()

    # Método de clase para mostrar el diálogo y devolver la lista de rutas.
    @classmethod
    def ask(cls, parent, title):
        dialog = cls(parent, title)
        parent.wait_window(dialog)
        return dialog.result


# Diálogo para mostrar una imagen infográfica con scroll.
class InfographicDialog(BaseDialog):
    def __init__(self, parent, title: str, image_path: str):
        # Se pasa 'title' al constructor de la clase base para corregir el error.
        super().__init__(parent, title)

        try:
            # Establece un tamaño predeterminado para la ventana
            self.geometry("575x400")

            # Crea el marco con scroll para la imagen
            scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
            scroll_frame.pack(expand=True, fill="both", padx=10, pady=10)

            # Carga, redimensiona y muestra la imagen
            pil_image_original = Image.open(image_path)
            original_width, original_height = pil_image_original.size
            target_width = 525
            ratio = target_width / original_width
            target_height = int(original_height * ratio)

            pil_image_resized = pil_image_original.resize((target_width, target_height), Image.Resampling.LANCZOS)

            self.infographic_image = ctk.CTkImage(
                light_image=pil_image_resized,
                dark_image=pil_image_resized,
                size=(target_width, target_height)
            )

            image_label = ctk.CTkLabel(scroll_frame, image=self.infographic_image, text="")
            image_label.pack(expand=True)

        except Exception as e:
            # Si la creación falla, se muestra un error y el diálogo se autodestruye.
            parent.show_message("error_title", f"{parent._tr('msg_error_generic')}\n\n{e}")
            # Se usa 'after' para asegurar que el mensaje se muestre antes de destruir la ventana.
            self.after(50, self.destroy)
