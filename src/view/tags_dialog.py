
import customtkinter as ctk
import copy
import os
from tkinter import filedialog
from file_rules import file_rules_conflict, matches_file_rule, normalize_file_rule, normalize_file_tag_list
from view.dialogs import BaseDialog, _get_color_tuple, _style_button, _style_checkbox, _style_entry, _style_scrollable
from view.ui_constants import COLORS, mix_color

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
                 forbidden_items: set = None,
                 extra_checkbox_text: str | None = None,
                 extra_checkbox_value: bool = False,
                 persistent: bool = False,
                 defer_show: bool = False):
        super().__init__(parent, title, persistent=persistent, defer_show=defer_show)

        self.single_mode = (folders_prompt is None)
        self.allow_autodetect = allow_autodetect

        self.excluded_folders = excluded_folders if excluded_folders else []
        self.excluded_files = normalize_file_tag_list(excluded_files if excluded_files else [])
        self.media_extensions = [normalize_file_rule(ext) for ext in media_extensions] if media_extensions else []
        self.forbidden_items = {normalize_file_rule(item) for item in forbidden_items} if forbidden_items else set()
        self.extra_checkbox_text = extra_checkbox_text
        self.extra_checkbox_value = bool(extra_checkbox_value)

        self.folders_prompt = folders_prompt
        self.files_prompt = files_prompt
        self.folders_list = copy.deepcopy(initial_folders) if initial_folders is not None else []
        self.files_list = normalize_file_tag_list(initial_files)
        self._parent = parent
        self._layout_retry_after_id = None
        self._layout_retry_count = 0
        self._resize_after_id = None
        self._last_window_size = None
        self._last_layout_widths = None

        self.tag_colors = self._build_tag_colors()

        self.tag_font = ctk.CTkFont(family="Segoe UI", size=11)

        self.geometry("600x550")
        self.main_frame = self._create_card_frame()
        self.main_frame.grid_columnconfigure(0, weight=1)

        text_color = _get_color_tuple("text")

        self.lbl_folders_prompt = None
        self.lbl_files_prompt = None
        self.folders_entry = None
        self.files_entry = None
        self.btn_auto = None
        self.extra_checkbox = None
        self.extra_checkbox_var = None

        if self.single_mode:
            self._create_tag_section(0, files_prompt, "files", text_color)
            self.main_frame.grid_rowconfigure(1, weight=1)
        else:
            self._create_tag_section(0, folders_prompt, "folders", text_color)
            self._create_tag_section(1, files_prompt, "files", text_color)
            self.main_frame.grid_rowconfigure(1, weight=1)
            self.main_frame.grid_rowconfigure(4, weight=1)

        separator_row = 6
        button_row = 7

        if self.extra_checkbox_text:
            self.extra_checkbox_var = ctk.BooleanVar(value=self.extra_checkbox_value)
            self.extra_checkbox = ctk.CTkCheckBox(
                self.main_frame,
                text=self.extra_checkbox_text,
                variable=self.extra_checkbox_var,
                onvalue=True,
                offvalue=False
            )
            _style_checkbox(self.extra_checkbox)
            self.extra_checkbox.grid(row=6, column=0, sticky="w", padx=20, pady=(10, 0))
            separator_row = 7
            button_row = 8

        separator = ctk.CTkFrame(self.main_frame, height=1, fg_color=_get_color_tuple("separator_line"))
        separator.grid(row=separator_row, column=0, sticky="ew", padx=0, pady=(10, 0))

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=button_row, column=0, pady=(15, 10), sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        txt_ok = self._parent._tr("btn_ok") if hasattr(self._parent, "_tr") else "Aceptar"
        txt_cancel = self._parent._tr("btn_cancel_simple") if hasattr(self._parent, "_tr") else "Cancelar"

        self.ok_button = ctk.CTkButton(button_frame, text=txt_ok, command=self._on_ok)
        _style_button(self.ok_button, "green")
        self.ok_button.configure(width=100)
        self.ok_button.grid(row=0, column=0, padx=10, sticky="e")

        self.cancel_button = ctk.CTkButton(button_frame, text=txt_cancel, command=self._on_cancel)
        _style_button(self.cancel_button, "red")
        self.cancel_button.configure(width=100)
        self.cancel_button.grid(row=0, column=1, padx=10, sticky="w")

        self.bind("<Configure>", self._on_window_configure)

        self.update_idletasks()
        self._schedule_layout_refresh(reset=True)

    def refresh_texts(self):
        try:
            self.title(self.current_title)
        except Exception:
            pass
        ph_text = self._parent._tr("placeholder_tags") if hasattr(self._parent, "_tr") else "Escribir..."
        if self.lbl_folders_prompt is not None:
            self.lbl_folders_prompt.configure(text=self.folders_prompt)
        if self.lbl_files_prompt is not None:
            self.lbl_files_prompt.configure(text=self.files_prompt)
        if self.folders_entry is not None:
            self.folders_entry.configure(placeholder_text=ph_text)
        if self.files_entry is not None:
            self.files_entry.configure(placeholder_text=ph_text)
        if self.btn_auto is not None:
            self.btn_auto.configure(text=self._parent._tr("btn_autodetect") if hasattr(self._parent, "_tr") else "Autodetectar")
        if self.extra_checkbox is not None:
            self.extra_checkbox.configure(text=self.extra_checkbox_text or "")
        self.ok_button.configure(text=self._parent._tr("btn_ok") if hasattr(self._parent, "_tr") else "Aceptar")
        self.cancel_button.configure(text=self._parent._tr("btn_cancel_simple") if hasattr(self._parent, "_tr") else "Cancelar")

    def load_state(self, title, folders_prompt, initial_folders, files_prompt, initial_files,
                   allow_autodetect=False, excluded_folders=None, excluded_files=None, media_extensions=None,
                   forbidden_items=None, extra_checkbox_text=None, extra_checkbox_value=False):
        self.current_title = title
        self.folders_prompt = folders_prompt
        self.files_prompt = files_prompt
        self.allow_autodetect = allow_autodetect
        self.excluded_folders = excluded_folders if excluded_folders else []
        self.excluded_files = normalize_file_tag_list(excluded_files if excluded_files else [])
        self.media_extensions = [normalize_file_rule(ext) for ext in media_extensions] if media_extensions else []
        self.forbidden_items = {normalize_file_rule(item) for item in forbidden_items} if forbidden_items else set()
        self.extra_checkbox_text = extra_checkbox_text
        self.extra_checkbox_value = bool(extra_checkbox_value)
        self.folders_list = copy.deepcopy(initial_folders) if initial_folders is not None else []
        self.files_list = normalize_file_tag_list(initial_files)
        self.result = None
        self._last_layout_widths = None
        self._last_window_size = None
        if self.folders_entry is not None:
            self.folders_entry.delete(0, "end")
        if self.files_entry is not None:
            self.files_entry.delete(0, "end")
        if self.extra_checkbox is not None and self.extra_checkbox_var is not None:
            self.extra_checkbox_var.set(self.extra_checkbox_value)
        self.refresh_texts()
        self._schedule_layout_refresh(reset=True)

    def present(self):
        super().present()
        self._schedule_layout_refresh(reset=True)
        try:
            if self.files_entry is not None:
                self.files_entry.focus_set()
            elif self.folders_entry is not None:
                self.folders_entry.focus_set()
        except Exception:
            pass

    def _cancel_layout_refresh(self):
        if self._layout_retry_after_id is not None:
            try:
                self.after_cancel(self._layout_retry_after_id)
            except Exception:
                pass
            self._layout_retry_after_id = None

    def _schedule_layout_refresh(self, reset=False, delay=0):
        if reset:
            self._layout_retry_count = 0
        self._cancel_layout_refresh()
        try:
            self._layout_retry_after_id = self.after(delay, self._refresh_layout_when_ready)
        except Exception:
            self._layout_retry_after_id = None

    def _on_window_configure(self, event=None):
        if event is not None and event.widget is not self:
            return
        try:
            size = (
                max(1, int(getattr(event, "width", self.winfo_width()))),
                max(1, int(getattr(event, "height", self.winfo_height())))
            )
        except Exception:
            size = (max(1, int(self.winfo_width())), max(1, int(self.winfo_height())))
        if size == self._last_window_size:
            return
        self._last_window_size = size
        if self._resize_after_id is not None:
            try:
                self.after_cancel(self._resize_after_id)
            except Exception:
                pass
        try:
            self._resize_after_id = self.after(30, self._schedule_layout_refresh)
        except Exception:
            self._resize_after_id = None

    def _get_container_width(self, frame):
        widths = []
        try:
            widths.append(int(frame.winfo_width()) - 34)
        except Exception:
            pass
        try:
            widths.append(int(frame.winfo_reqwidth()) - 34)
        except Exception:
            pass
        try:
            widths.append(int(self.main_frame.winfo_width()) - 60)
        except Exception:
            pass
        try:
            widths.append(int(self.winfo_width()) - 80)
        except Exception:
            pass
        widths = [w for w in widths if w > 0]
        return max(widths) if widths else 0

    def _refresh_layout_when_ready(self):
        self._layout_retry_after_id = None
        if not self.winfo_exists():
            return
        try:
            self.update_idletasks()
        except Exception:
            pass
        widths = []
        if not self.single_mode:
            widths.append(self._get_container_width(self.folders_scroll_frame))
        widths.append(self._get_container_width(self.files_scroll_frame))
        ready = bool(widths) and min(widths) >= 220
        widths_key = tuple(widths)
        if not ready and self._layout_retry_count < 8:
            self._layout_retry_count += 1
            self._schedule_layout_refresh(delay=40)
            return
        if ready and widths_key == self._last_layout_widths:
            return
        self._last_layout_widths = widths_key if ready else None
        self.redraw_all_tags()
        if self._layout_retry_count < 2:
            self._layout_retry_count += 1
            self._schedule_layout_refresh(delay=40)

    def _build_tag_colors(self):
        blue_btn = COLORS['button']['blue']
        bg_panel = _get_color_tuple("bg_panel")
        border_subtle = _get_color_tuple("border_subtle")
        text_secondary = _get_color_tuple("text_secondary")

        inactive_fg = (
            mix_color(bg_panel[0], text_secondary[0], 0.12),
            mix_color(bg_panel[1], "#FFFFFF", 0.08)
        )
        inactive_border = (
            mix_color(border_subtle[0], text_secondary[0], 0.30),
            mix_color(border_subtle[1], "#FFFFFF", 0.22)
        )
        inactive_hover = (
            mix_color(inactive_fg[0], text_secondary[0], 0.12),
            mix_color(inactive_fg[1], "#FFFFFF", 0.10)
        )

        return {
            "activo": {
                "fg": blue_btn["bg"],
                "hover": blue_btn["hover"],
                "text": COLORS["light"]["text_on_accent"],
                "border": blue_btn["bg"],
                "border_width": 0
            },
            "inactivo": {
                "fg": inactive_fg,
                "hover": inactive_hover,
                "text": text_secondary,
                "border": inactive_border,
                "border_width": 1
            }
        }

    def _create_tag_section(self, section_index, prompt, section_id, text_color):
        base_row = section_index * 3
        label = ctk.CTkLabel(self.main_frame, text=prompt, font=("Segoe UI", 12, "bold"), text_color=text_color)
        label.grid(
            row=base_row, column=0,
            sticky="w", pady=(10, 2), padx=20)
        if section_id == "folders":
            self.lbl_folders_prompt = label
        else:
            self.lbl_files_prompt = label

        scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            label_text="",
            fg_color=_get_color_tuple("inner_area"),
            border_width=1,
            border_color=_get_color_tuple("card_border")
        )
        _style_scrollable(scroll_frame)
        scroll_frame.grid(row=base_row + 1, column=0, sticky="nsew", padx=20)

        input_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        input_container.grid(row=base_row + 2, column=0, sticky="ew", pady=(5, 0), padx=20)

        ph_text = self._parent._tr("placeholder_tags") if hasattr(self._parent, "_tr") else "Escribir..."

        entry = ctk.CTkEntry(input_container, placeholder_text=ph_text)
        _style_entry(entry)
        entry.pack(side="left", fill="x", expand=True)

        if section_id == "folders":
            self.folders_scroll_frame = scroll_frame
            self.folders_entry = entry
            entry.bind("<Return>", lambda event: self._add_tag(entry, self.folders_list, is_folder=True))
        else:
            self.files_scroll_frame = scroll_frame
            self.files_entry = entry
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
                self.btn_auto = btn_auto

    def _on_autodetect(self):
        path = filedialog.askdirectory(title=self._parent._tr("btn_autodetect"))
        if not path:
            return

        added_count = 0

        excl_folders_set = {t["nombre"] for t in self.excluded_folders if t["estado"] == "activo"}
        excl_files_rules = [t["nombre"] for t in self.excluded_files if t["estado"] == "activo"]
        media_rules = list(self.media_extensions)
        current_file_rules = [t["nombre"] for t in self.files_list]
        added_extensions = []
        seen_extensions = set()

        try:
            if self.btn_auto is not None:
                self.btn_auto.configure(state="disabled")
            self.ok_button.configure(state="disabled")
            self.cancel_button.configure(state="disabled")
            if self.folders_entry is not None:
                self.folders_entry.configure(state="disabled")
            if self.files_entry is not None:
                self.files_entry.configure(state="disabled")
        except Exception:
            pass

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
                    if ext in seen_extensions:
                        continue
                    if matches_file_rule(filename, media_rules):
                        continue
                    if matches_file_rule(filename, current_file_rules):
                        continue

                    seen_extensions.add(ext)
                    current_file_rules.append(ext)
                    added_extensions.append(ext)
                    added_count += 1

            if added_extensions:
                self.files_list.extend({"nombre": ext, "estado": "activo"} for ext in added_extensions)
                self._last_layout_widths = None
                self.redraw_all_tags()
                self._parent.show_message("info_title", "msg_autodetect_result", str(added_count))
            else:
                self._parent.show_message("info_title", "msg_autodetect_none")

        except Exception as e:
            print(f"Error autodetectando: {e}")
            self._parent.show_message("error_title", "msg_error_generic")
        finally:
            try:
                if self.btn_auto is not None:
                    self.btn_auto.configure(state="normal")
                self.ok_button.configure(state="normal")
                self.cancel_button.configure(state="normal")
                if self.folders_entry is not None:
                    self.folders_entry.configure(state="normal")
                if self.files_entry is not None:
                    self.files_entry.configure(state="normal")
            except Exception:
                pass

    def redraw_all_tags(self):
        if not self.winfo_exists(): return
        if not self.single_mode:
            self._redraw_tags_in_frame(self.folders_scroll_frame, self.folders_list)

        self._redraw_tags_in_frame(self.files_scroll_frame, self.files_list)

    def _redraw_tags_in_frame(self, frame, tag_list):
        for widget in frame.winfo_children(): widget.destroy()
        if not frame.winfo_exists(): return
        frame.update_idletasks()

        container_width = self._get_container_width(frame)
        if container_width < 220:
            return

        row_container = ctk.CTkFrame(frame, fg_color="transparent")
        row_container.pack(fill="x", anchor="nw")
        current_row = ctk.CTkFrame(row_container, fg_color="transparent")
        current_row.pack(fill="x", anchor="w", pady=(0, 5))
        current_row_width = 0

        space_between_pills = 6
        wrap_safety_px = 16

        for index, tag_data in enumerate(tag_list):
            pill_frame = self._create_pill_frame(current_row, tag_data, index, tag_list)
            pill_frame.pack(side="left", padx=(0, space_between_pills))
            pill_frame.update_idletasks()

            pill_width = max(pill_frame.winfo_reqwidth(), pill_frame.winfo_width()) + wrap_safety_px

            if current_row_width > 0 and (current_row_width + pill_width) > container_width:
                pill_frame.destroy()
                current_row = ctk.CTkFrame(row_container, fg_color="transparent")
                current_row.pack(fill="x", anchor="w", pady=(0, 5))

                pill_frame = self._create_pill_frame(current_row, tag_data, index, tag_list)
                pill_frame.pack(side="left", padx=(0, space_between_pills))
                pill_frame.update_idletasks()
                pill_width = max(pill_frame.winfo_reqwidth(), pill_frame.winfo_width()) + wrap_safety_px
                current_row_width = 0

            current_row_width += pill_width + space_between_pills

    def _create_pill_frame(self, parent, tag_data, index, tag_list):
        tag_name, tag_state = tag_data["nombre"], tag_data["estado"]
        colors = self.tag_colors[tag_state]

        pill_frame = ctk.CTkFrame(parent, fg_color=colors["fg"], border_color=colors.get("border", colors["fg"]), border_width=colors.get("border_width", 0), corner_radius=14)

        label = ctk.CTkLabel(pill_frame, text=tag_name, text_color=colors["text"], font=self.tag_font)
        label.pack(side="left", padx=(10, 4), pady=2)

        close_button = ctk.CTkButton(
            pill_frame,
            text="✕",
            width=20,
            height=20,
            corner_radius=10,
            text_color=colors["text"],
            fg_color="transparent",
            hover_color=colors["hover"],
            command=lambda i=index, l=tag_list: self._delete_tag(i, l)
        )

        close_button.pack(side="right", padx=(0, 8), pady=3)
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
        self._last_layout_widths = None
        self.redraw_all_tags()

    def _delete_tag(self, index, tag_list):
        if index < len(tag_list):
            tag_list.pop(index)
            self._last_layout_widths = None
            self.redraw_all_tags()

    def _toggle_tag_state(self, event, index, tag_list):
        if index < len(tag_list):
            current_state = tag_list[index]["estado"]
            tag_list[index]["estado"] = "inactivo" if current_state == "activo" else "activo"
            self._last_layout_widths = None
            self.redraw_all_tags()

    def _on_ok(self, event=None):
        self.files_list = normalize_file_tag_list(self.files_list)
        if self.single_mode:
            self.result = (None, self.files_list)
        else:
            if self.extra_checkbox is not None and self.extra_checkbox_var is not None:
                self.result = (self.folders_list, self.files_list, bool(self.extra_checkbox_var.get()))
            else:
                self.result = (self.folders_list, self.files_list)
        super()._on_ok(event)

    @classmethod
    def get_input(cls, parent, title, folders_prompt, initial_folders, files_prompt, initial_files,
                  allow_autodetect=False, excluded_folders=None, excluded_files=None, media_extensions=None,
                  forbidden_items=None, extra_checkbox_text=None, extra_checkbox_value=False):
        dialog = None
        try:
            dialog = cls(parent, title, folders_prompt, initial_folders, files_prompt, initial_files,
                         allow_autodetect, excluded_folders, excluded_files, media_extensions,
                         forbidden_items, extra_checkbox_text, extra_checkbox_value)
            parent.wait_window(dialog)
            return dialog.result
        except Exception:
            try:
                if hasattr(parent, "restore_ui_from_modal"):
                    parent.restore_ui_from_modal()
            except Exception:
                pass
            return None
        finally:
            if dialog is not None:
                try:
                    if dialog.winfo_exists():
                        dialog.destroy()
                except Exception:
                    pass
