import customtkinter as ctk
import copy
import os
from tkinter import filedialog
from file_rules import file_rules_conflict, matches_file_rule, normalize_file_rule, normalize_file_tag_list
from view.dialogs import BaseDialog, _get_color_tuple, _style_button
from view.ui_constants import COLORS


# =============================================================================
# DIALOGO DE CONFIGURACION DE ETIQUETAS
# =============================================================================

class TagsConfigDialog(BaseDialog):

    def __init__(self, parent, title: str,
                 folders_prompt: str | None, initial_folders: list | None,
                 files_prompt: str, initial_files: list,
                 allow_autodetect: bool = False,
                 excluded_folders: list = None,
                 excluded_files: list = None,
                 media_extensions: list = None,
                 forbidden_items: set = None):
        super().__init__(parent, title)

        self.single_mode = (folders_prompt is None)
        self.allow_autodetect = allow_autodetect

        self.excluded_folders = excluded_folders if excluded_folders else []
        self.excluded_files = normalize_file_tag_list(excluded_files if excluded_files else [])
        self.media_extensions = [normalize_file_rule(ext) for ext in media_extensions] if media_extensions else []
        self.forbidden_items = {normalize_file_rule(item) for item in forbidden_items} if forbidden_items else set()

        self.folders_list = copy.deepcopy(initial_folders) if initial_folders is not None else []
        self.files_list = normalize_file_tag_list(initial_files)
        self._parent = parent

        blue_btn = COLORS['button']['blue']
        self.tag_colors = {
            "activo": {"fg": blue_btn["bg"], "hover": blue_btn["hover"], "text": "#FFFFFF"},
            "inactivo": {"fg": "#6c757d", "hover": "#5a6268", "text": "#FFFFFF"}
        }

        self.tag_font = ctk.CTkFont(family="Segoe UI", size=11)

        self.geometry("600x550")
        self.main_frame = self._create_card_frame()
        self.main_frame.grid_columnconfigure(0, weight=1)

        text_color = _get_color_tuple("text")

        if self.single_mode:
            self._create_tag_section(0, files_prompt, "files", text_color)
            self.main_frame.grid_rowconfigure(1, weight=1)
        else:
            self._create_tag_section(0, folders_prompt, "folders", text_color)
            self._create_tag_section(1, files_prompt, "files", text_color)
            self.main_frame.grid_rowconfigure(1, weight=1)
            self.main_frame.grid_rowconfigure(4, weight=1)

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
        path = filedialog.askdirectory(title=self._parent._tr("btn_autodetect"))
        if not path:
            return

        added_count = 0

        excl_folders_set = {t["nombre"] for t in self.excluded_folders if t["estado"] == "activo"}
        excl_files_rules = [t["nombre"] for t in self.excluded_files if t["estado"] == "activo"]
        media_rules = list(self.media_extensions)
        current_file_rules = [t["nombre"] for t in self.files_list]

        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in excl_folders_set]

                for filename in files:
                    if matches_file_rule(filename, excl_files_rules):
                        continue

                    _, ext = os.path.splitext(filename)
                    ext = normalize_file_rule(ext)

                    if not ext:
                        continue
                    if matches_file_rule(filename, media_rules):
                        continue
                    if matches_file_rule(filename, current_file_rules):
                        continue

                    self.files_list.append({"nombre": ext, "estado": "activo"})
                    current_file_rules.append(ext)
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

        tag_to_check = raw_val if is_folder else normalize_file_rule(raw_val)

        if any(
            file_rules_conflict(t["nombre"], tag_to_check) if not is_folder else t["nombre"] == tag_to_check
            for t in tag_list
        ):
            entry.delete(0, "end")
            return

        if not is_folder and any(file_rules_conflict(item, tag_to_check) for item in self.forbidden_items):
            self._parent.show_message("error_title", "msg_tag_conflict", tag_to_check)
            entry.delete(0, "end")
            return

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
        self.files_list = normalize_file_tag_list(self.files_list)
        if self.single_mode:
            self.result = (None, self.files_list)
        else:
            self.result = (self.folders_list, self.files_list)
        super()._on_ok(event)

    @classmethod
    def get_input(cls, parent, title, folders_prompt, initial_folders, files_prompt, initial_files,
                  allow_autodetect=False, excluded_folders=None, excluded_files=None, media_extensions=None,
                  forbidden_items=None):
        dialog = cls(parent, title, folders_prompt, initial_folders, files_prompt, initial_files,
                     allow_autodetect, excluded_folders, excluded_files, media_extensions,
                     forbidden_items)
        parent.wait_window(dialog)
        return dialog.result
