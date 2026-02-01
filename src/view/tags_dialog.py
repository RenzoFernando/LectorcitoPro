import customtkinter as ctk
import copy
import os
from tkinter import filedialog
from view.dialogs import BaseDialog, _get_color_tuple, _style_button
from view.ui_constants import COLORS


# Diálogo para gestionar listas de etiquetas (carpetas, extensiones, etc.).
class TagsConfigDialog(BaseDialog):

    def __init__(self, parent, title: str,
                 folders_prompt: str | None, initial_folders: list | None,
                 files_prompt: str, initial_files: list,
                 allow_autodetect: bool = False,
                 excluded_folders: list = None,
                 excluded_files: list = None,
                 media_extensions: list = None,
                 forbidden_items: set = None):  # NUEVO: Lista de prohibidos
        super().__init__(parent, title)

        # Detectamos si es modo "Solo Archivos"
        self.single_mode = (folders_prompt is None)
        self.allow_autodetect = allow_autodetect

        # GUARDAMOS LAS LISTAS DE EXCLUSIÓN Y MULTIMEDIA PARA LA AUTODETECCIÓN
        self.excluded_folders = excluded_folders if excluded_folders else []
        self.excluded_files = excluded_files if excluded_files else []
        self.media_extensions = media_extensions if media_extensions else []

        # NUEVO: Set de items prohibidos (para evitar conflictos de prioridad)
        self.forbidden_items = forbidden_items if forbidden_items else set()

        self.folders_list = copy.deepcopy(initial_folders) if initial_folders is not None else []
        self.files_list = copy.deepcopy(initial_files)
        self._parent = parent

        # Accedemos a la estructura nueva de botones
        blue_btn = COLORS['button']['blue']
        self.tag_colors = {
            "activo": {"fg": blue_btn["bg"], "hover": blue_btn["hover"], "text": "#FFFFFF"},
            "inactivo": {"fg": "#6c757d", "hover": "#5a6268", "text": "#FFFFFF"}
        }

        self.tag_font = ctk.CTkFont(family="Segoe UI", size=11)

        # AJUSTE DE GEOMETRÍA
        self.geometry("600x550")

        # Tarjeta principal
        self.main_frame = self._create_card_frame()
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Creación de las secciones
        text_color = _get_color_tuple("text")

        if self.single_mode:
            # MODO UNIFICADO
            self._create_tag_section(0, files_prompt, "files", text_color)
            self.main_frame.grid_rowconfigure(1, weight=1)
        else:
            # MODO ESTÁNDAR
            self._create_tag_section(0, folders_prompt, "folders", text_color)
            self._create_tag_section(1, files_prompt, "files", text_color)
            self.main_frame.grid_rowconfigure(1, weight=1)
            self.main_frame.grid_rowconfigure(4, weight=1)

        # --- SECCIÓN DE ACCIONES (Botones) ---
        separator = ctk.CTkFrame(self.main_frame, height=1, fg_color=_get_color_tuple("separator_line"))
        separator.grid(row=6, column=0, sticky="ew", padx=0, pady=(10, 0))

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=7, column=0, pady=(15, 15), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        txt_save = parent._tr("btn_save_changes") if hasattr(parent, "_tr") else "Guardar Cambios"
        txt_cancel = parent._tr("btn_cancel_simple") if hasattr(parent, "_tr") else "Cancelar"

        ok_button = ctk.CTkButton(button_frame, text=txt_save, command=self._on_ok)
        _style_button(ok_button, "green")
        ok_button.configure(width=140)
        ok_button.grid(row=0, column=0, padx=10, sticky="e")

        cancel_button = ctk.CTkButton(button_frame, text=txt_cancel, command=self._on_cancel)
        _style_button(cancel_button, "red")
        cancel_button.configure(width=100)
        cancel_button.grid(row=0, column=1, padx=10, sticky="w")

        self.update_idletasks()
        self.after(500, self.redraw_all_tags)

    def _create_tag_section(self, section_index, prompt, section_id, text_color):
        base_row = section_index * 3
        ctk.CTkLabel(self.main_frame, text=prompt, font=("Segoe UI", 12, "bold"), text_color=text_color).grid(
            row=base_row, column=0,
            sticky="w", pady=(10, 2), padx=20)

        scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            label_text="",
            fg_color=_get_color_tuple("inner_area"),
            border_width=1,
            border_color=_get_color_tuple("card_border")
        )
        scroll_frame.grid(row=base_row + 1, column=0, sticky="nsew", padx=20)

        # Frame contenedor para Input + Botón Autodetectar
        input_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        input_container.grid(row=base_row + 2, column=0, sticky="ew", pady=(5, 0), padx=20)

        ph_text = self._parent._tr("placeholder_tags") if hasattr(self._parent, "_tr") else "Escribir..."

        entry = ctk.CTkEntry(input_container, placeholder_text=ph_text)
        entry.pack(side="left", fill="x", expand=True)

        if section_id == "folders":
            self.folders_scroll_frame = scroll_frame
            entry.bind("<Return>", lambda event: self._add_tag(entry, self.folders_list, is_folder=True))
        else:
            self.files_scroll_frame = scroll_frame
            entry.bind("<Return>", lambda event: self._add_tag(entry, self.files_list, is_folder=False))

            if self.allow_autodetect:
                txt_auto = self._parent._tr("btn_autodetect") if hasattr(self._parent, "_tr") else "Autodetectar"
                btn_auto = ctk.CTkButton(
                    input_container,
                    text=txt_auto,
                    width=80,
                    height=28,
                    command=self._on_autodetect
                )
                _style_button(btn_auto, "blue")
                btn_auto.pack(side="left", padx=(8, 0))

    def _on_autodetect(self):
        """Escanea respetando exclusiones y multimedia."""
        path = filedialog.askdirectory(title=self._parent._tr("btn_autodetect"))
        if not path:
            return

        added_count = 0

        # 1. Preparar conjuntos de exclusión (Solo los activos)
        excl_folders_set = {t["nombre"] for t in self.excluded_folders if t["estado"] == "activo"}
        excl_files_set = {t["nombre"] for t in self.excluded_files if t["estado"] == "activo"}

        # 2. Extensiones multimedia (ya vienen como lista de strings)
        media_set = {ext.lower() for ext in self.media_extensions}

        # 3. Extensiones que ya tengo en la lista actual (para no duplicar)
        current_exts = {t["nombre"].lower() for t in self.files_list}

        try:
            for root, dirs, files in os.walk(path):
                # A. Filtrar directorios excluidos para que os.walk NO entre en ellos
                # Modificamos dirs in-place para podar el árbol
                dirs[:] = [d for d in dirs if d not in excl_folders_set]

                for filename in files:
                    # B. Si el archivo está excluido por nombre completo, ignorar
                    if filename in excl_files_set:
                        continue

                    _, ext = os.path.splitext(filename)
                    ext = ext.lower()

                    if not ext: continue

                    # C. Si es multimedia, ignorar
                    if ext in media_set:
                        continue

                    # D. Si ya la tengo, ignorar
                    if ext in current_exts:
                        continue

                    # Agregamos
                    self.files_list.append({"nombre": ext, "estado": "activo"})
                    current_exts.add(ext)
                    added_count += 1

            self.redraw_all_tags()

            if added_count > 0:
                self._parent.show_message("info_title", "msg_autodetect_result", str(added_count))
            else:
                self._parent.show_message("info_title", "msg_autodetect_none")

        except Exception as e:
            print(f"Error autodetectando: {e}")
            self._parent.show_message("error_title", "msg_error_generic")

    def redraw_all_tags(self):
        if not self.winfo_exists(): return
        if not self.single_mode:
            self._redraw_tags_in_frame(self.folders_scroll_frame, self.folders_list)

        self._redraw_tags_in_frame(self.files_scroll_frame, self.files_list)

    def _redraw_tags_in_frame(self, frame, tag_list):
        for widget in frame.winfo_children(): widget.destroy()
        if not frame.winfo_exists(): return
        frame.update_idletasks()

        container_width = frame.winfo_width() - 30

        row_container = ctk.CTkFrame(frame, fg_color="transparent")
        row_container.pack(fill="x", anchor="nw")
        current_row = ctk.CTkFrame(row_container, fg_color="transparent")
        current_row.pack(fill="x", anchor="w", pady=(0, 5))
        current_row_width = 0

        PILL_FIXED_WIDTH = 75
        SPACE_BETWEEN_PILLS = 5

        for index, tag_data in enumerate(tag_list):
            text_width = self.tag_font.measure(tag_data["nombre"])
            pill_width = text_width + PILL_FIXED_WIDTH

            if current_row_width > 0 and (current_row_width + pill_width) > container_width:
                current_row = ctk.CTkFrame(row_container, fg_color="transparent")
                current_row.pack(fill="x", anchor="w", pady=(0, 5))
                current_row_width = 0

            pill_frame = self._create_pill_frame(current_row, tag_data, index, tag_list)
            pill_frame.pack(side="left", padx=(0, SPACE_BETWEEN_PILLS))
            current_row_width += pill_width + SPACE_BETWEEN_PILLS

    def _create_pill_frame(self, parent, tag_data, index, tag_list):
        tag_name, tag_state = tag_data["nombre"], tag_data["estado"]
        colors = self.tag_colors[tag_state]

        pill_frame = ctk.CTkFrame(parent, fg_color=colors["fg"], border_width=0, corner_radius=14)

        label = ctk.CTkLabel(pill_frame, text=tag_name, text_color=colors["text"], font=self.tag_font)
        label.pack(side="left", padx=(10, 4), pady=2)

        close_button = ctk.CTkButton(pill_frame, text="✕", width=20, height=20, corner_radius=10,
                                     text_color=colors["text"], fg_color="transparent", hover_color=colors["hover"],
                                     command=lambda i=index, l=tag_list: self._delete_tag(i, l))

        close_button.pack(side="right", padx=(0, 6), pady=2)
        pill_frame.bind("<Button-1>", lambda e, i=index, l=tag_list: self._toggle_tag_state(e, i, l))
        label.bind("<Button-1>", lambda e, i=index, l=tag_list: self._toggle_tag_state(e, i, l))
        return pill_frame

    def _add_tag(self, entry, tag_list, is_folder=False):
        raw_val = entry.get().strip()
        if not raw_val:
            return

        # Normalización automática si es archivo (añadir punto)
        if not is_folder and not raw_val.startswith("."):
            tag_to_check = f".{raw_val}"
        else:
            tag_to_check = raw_val

        # VALIDACIÓN 1: Verificar si ya existe en la lista actual
        if any(t["nombre"] == tag_to_check for t in tag_list):
            entry.delete(0, "end")
            return

        # VALIDACIÓN 2: Verificar Conflictos de Prioridad (Ver/No Ver vs Multimedia)
        if tag_to_check in self.forbidden_items:
            # Bloqueamos y mostramos error
            self._parent.show_message("error_title", "msg_tag_conflict", tag_to_check)
            entry.delete(0, "end")
            return

        # Si pasa validaciones, agregamos
        tag_list.append({"nombre": tag_to_check, "estado": "activo"})
        entry.delete(0, "end")
        self.redraw_all_tags()

    def _delete_tag(self, index, tag_list):
        if index < len(tag_list):
            tag_list.pop(index)
            self.redraw_all_tags()

    def _toggle_tag_state(self, event, index, tag_list):
        if index < len(tag_list):
            current_state = tag_list[index]["estado"]
            tag_list[index]["estado"] = "inactivo" if current_state == "activo" else "activo"
            self.redraw_all_tags()

    def _on_ok(self, event=None):
        if self.single_mode:
            self.result = (None, self.files_list)
        else:
            self.result = (self.folders_list, self.files_list)
        super()._on_ok(event)

    @classmethod
    def get_input(cls, parent, title, folders_prompt, initial_folders, files_prompt, initial_files,
                  allow_autodetect=False, excluded_folders=None, excluded_files=None, media_extensions=None,
                  forbidden_items=None):  # NUEVO ARGUMENTO

        dialog = cls(parent, title, folders_prompt, initial_folders, files_prompt, initial_files,
                     allow_autodetect, excluded_folders, excluded_files, media_extensions,
                     forbidden_items)  # Pasamos el argumento
        parent.wait_window(dialog)
        return dialog.result