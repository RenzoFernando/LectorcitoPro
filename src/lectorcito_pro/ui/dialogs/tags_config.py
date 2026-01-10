from __future__ import annotations

import copy
import customtkinter as ctk

from .base import BaseDialog, COLORS
from ..components.molecules.tag_pills import TagPillsEditor


class TagsConfigDialog(BaseDialog):
    """Diálogo para editar tags (carpetas/extensiones excluidas/incluidas, etc.).

    Mantiene el contrato:
    - `result` devuelve (folders_list, files_list) o None.
    - Cada lista es una lista de dicts: {"nombre": str, "estado": "activo|inactivo"}.
    """

    def __init__(
        self,
        parent,
        title: str,
        folders_prompt: str,
        initial_folders: list,
        files_prompt: str,
        initial_files: list,
    ):
        super().__init__(parent, title)

        self.folders_list = copy.deepcopy(initial_folders)
        self.files_list = copy.deepcopy(initial_files)

        self.main_frame = ctk.CTkFrame(self, corner_radius=12)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.folders_editor = TagPillsEditor(
            self.main_frame,
            prompt=folders_prompt,
            tag_list=self.folders_list,
            placeholder="Escribir y presionar Enter para añadir...",
        )
        self.folders_editor.grid(row=0, column=0, sticky="nsew")

        self.files_editor = TagPillsEditor(
            self.main_frame,
            prompt=files_prompt,
            tag_list=self.files_list,
            placeholder="Escribir y presionar Enter para añadir...",
        )
        self.files_editor.grid(row=1, column=0, sticky="nsew", pady=(15, 0))

        # Botones
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(20, 0), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        ok_button = ctk.CTkButton(
            button_frame,
            text="Guardar Cambios",
            command=self._on_ok,
            fg_color=COLORS["button"]["green"],
            hover_color=COLORS["button_hover"]["green_h"],
        )
        ok_button.grid(row=0, column=0, padx=5, sticky="e")

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancelar",
            command=self._on_cancel,
            fg_color=COLORS["button"]["red"],
            hover_color=COLORS["button_hover"]["red_h"],
        )
        cancel_button.grid(row=0, column=1, padx=5, sticky="w")

        # Redibujo inicial (por si el ancho se calcula tarde)
        self.after(150, self._initial_redraw)

    def _initial_redraw(self):
        if not self.winfo_exists():
            return
        try:
            self.folders_editor.redraw()
            self.files_editor.redraw()
        except Exception:
            pass

    def _on_ok(self, event=None):
        self.result = (self.folders_list, self.files_list)
        super()._on_ok(event)

    @classmethod
    def get_input(cls, parent, title, folders_prompt, initial_folders, files_prompt, initial_files):
        dialog = cls(parent, title, folders_prompt, initial_folders, files_prompt, initial_files)
        parent.wait_window(dialog)
        return dialog.result
