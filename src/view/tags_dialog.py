import customtkinter as ctk
import copy
import os
from tkinter import filedialog
from file_rules import file_rules_conflict, matches_file_rule, normalize_file_rule, normalize_file_tag_list
from view.dialogs import BaseDialog, _get_color_tuple, _style_button, _style_checkbox, _style_entry, _style_scrollable
from view.ui_constants import FONT_FAMILY_PRIMARY, COLORS, mix_color, NEUTRAL_WHITE, TAGS_DIALOG_WIDTH, TAGS_DIALOG_HEIGHT, TAGS_DIALOG_TAG_FONT_SIZE, TAGS_DIALOG_EXTRA_CHECKBOX_PADX, TAGS_DIALOG_EXTRA_CHECKBOX_PADY, TAGS_DIALOG_SEPARATOR_HEIGHT, TAGS_DIALOG_SEPARATOR_PADY, TAGS_DIALOG_BUTTON_FRAME_PADY, TAGS_DIALOG_ACTION_BUTTON_WIDTH, TAGS_DIALOG_ACTION_BUTTON_PADX, TAGS_DIALOG_LAYOUT_REFRESH_DELAY_MS, TAGS_DIALOG_SECTION_LABEL_FONT_SIZE, TAGS_DIALOG_SECTION_LABEL_PADY, TAGS_DIALOG_SECTION_LABEL_PADX, TAGS_DIALOG_SCROLL_PADX, TAGS_DIALOG_SCROLL_BORDER_WIDTH, TAGS_DIALOG_INPUT_PADX, TAGS_DIALOG_INPUT_PADY, TAGS_DIALOG_AUTODETECT_BUTTON_WIDTH, TAGS_DIALOG_AUTODETECT_BUTTON_HEIGHT, TAGS_DIALOG_AUTODETECT_BUTTON_PADX, TAGS_DIALOG_ROW_PADY, TAGS_DIALOG_PILL_SPACING, TAGS_DIALOG_WRAP_SAFETY_PX, TAGS_DIALOG_PILL_RADIUS, TAGS_DIALOG_PILL_LABEL_PADX, TAGS_DIALOG_PILL_LABEL_PADY, TAGS_DIALOG_PILL_CLOSE_SIZE, TAGS_DIALOG_PILL_CLOSE_RADIUS, TAGS_DIALOG_PILL_CLOSE_PADX, TAGS_DIALOG_PILL_CLOSE_PADY, DIALOG_BUTTON_FONT_SIZE
from i18n.translations import translate_default
from app_logging import log_error

# =============================================================================
# DIALOGO DE CONFIGURACION DE ETIQUETAS
# ============================================================================= 

def _tr_text(parent, key: str, *args):
    tr_callable = getattr(parent, "_tr", None)
    if callable(tr_callable):
        try:
            return tr_callable(key, *args)
        except Exception:
            pass
    return translate_default(key, *args)

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
        self._mousewheel_targets = {}

        self.tag_colors = self._build_tag_colors()

        self.tag_font = ctk.CTkFont(family=FONT_FAMILY_PRIMARY, size=TAGS_DIALOG_TAG_FONT_SIZE)

        self.geometry(f"{TAGS_DIALOG_WIDTH}x{TAGS_DIALOG_HEIGHT}")
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
            self.extra_checkbox.grid(row=6, column=0, sticky="w", padx=TAGS_DIALOG_EXTRA_CHECKBOX_PADX, pady=TAGS_DIALOG_EXTRA_CHECKBOX_PADY)
            separator_row = 7
            button_row = 8

        separator = ctk.CTkFrame(self.main_frame, height=TAGS_DIALOG_SEPARATOR_HEIGHT, fg_color=_get_color_tuple("separator_line"))
        separator.grid(row=separator_row, column=0, sticky="ew", padx=0, pady=TAGS_DIALOG_SEPARATOR_PADY)

        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.grid(row=button_row, column=0, pady=TAGS_DIALOG_BUTTON_FRAME_PADY, sticky="ew")
        button_frame.grid_columnconfigure((0, 1), weight=1)

        txt_ok = _tr_text(self._parent, "btn_ok")
        txt_cancel = _tr_text(self._parent, "btn_cancel_simple")

        self.ok_button = ctk.CTkButton(button_frame, text=txt_ok, command=self._on_ok)
        _style_button(self.ok_button, "green")
        self.ok_button.configure(width=TAGS_DIALOG_ACTION_BUTTON_WIDTH)
        self.ok_button.grid(row=0, column=0, padx=TAGS_DIALOG_ACTION_BUTTON_PADX, sticky="e")

        self.cancel_button = ctk.CTkButton(button_frame, text=txt_cancel, command=self._on_cancel)
        _style_button(self.cancel_button, "red")
        self.cancel_button.configure(width=TAGS_DIALOG_ACTION_BUTTON_WIDTH)
        self.cancel_button.grid(row=0, column=1, padx=TAGS_DIALOG_ACTION_BUTTON_PADX, sticky="w")

        self.bind("<Configure>", self._on_window_configure)

        self.update_idletasks()
        self._schedule_layout_refresh(reset=True)

    def _get_scroll_canvas(self, scroll_frame):
        try:
            return getattr(scroll_frame, "_parent_canvas", None)
        except Exception:
            return None

    def _bind_mousewheel_recursive(self, widget, scroll_frame):
        if widget is None:
            return
        try:
            widget.bind("<MouseWheel>", lambda event, sf=scroll_frame: self._on_mousewheel_scroll(event, sf), add="+")
        except Exception:
            pass
        try:
            widget.bind("<Button-4>", lambda event, sf=scroll_frame: self._on_mousewheel_scroll(event, sf), add="+")
            widget.bind("<Button-5>", lambda event, sf=scroll_frame: self._on_mousewheel_scroll(event, sf), add="+")
        except Exception:
            pass
        try:
            for child in widget.winfo_children():
                self._bind_mousewheel_recursive(child, scroll_frame)
        except Exception:
            pass

    def _configure_mousewheel_for_scrollable(self, scroll_frame):
        if scroll_frame is None:
            return
        self._bind_mousewheel_recursive(scroll_frame, scroll_frame)
        canvas = self._get_scroll_canvas(scroll_frame)
        if canvas is not None:
            self._bind_mousewheel_recursive(canvas, scroll_frame)

    def _normalize_mousewheel_units(self, event):
        num = getattr(event, "num", None)
        if num == 4:
            return -3
        if num == 5:
            return 3
        delta = int(getattr(event, "delta", 0) or 0)
        if delta == 0:
            return 0
        step_count = max(1, int(abs(delta) / 120))
        return (-1 if delta > 0 else 1) * step_count * 3

    def _get_scroll_metrics(self, scroll_frame):
        canvas = self._get_scroll_canvas(scroll_frame)
        if canvas is None:
            return None, 0, 0, False
        try:
            canvas.update_idletasks()
        except Exception:
            pass
        bbox = None
        try:
            bbox = canvas.bbox("all")
        except Exception:
            bbox = None
        content_height = 0
        if bbox is not None:
            try:
                content_height = max(0, int(bbox[3]) - int(bbox[1]))
            except Exception:
                content_height = 0
        try:
            viewport_height = max(0, int(canvas.winfo_height()))
        except Exception:
            viewport_height = 0
        has_overflow = content_height > max(0, viewport_height - 2)
        return canvas, content_height, viewport_height, has_overflow

    def _clamp_scroll_position(self, scroll_frame, requested_view=None):
        canvas, _, _, has_overflow = self._get_scroll_metrics(scroll_frame)
        if canvas is None:
            return
        if not has_overflow:
            try:
                canvas.yview_moveto(0.0)
            except Exception:
                pass
            return
        if requested_view is None:
            try:
                first, _ = canvas.yview()
                target_view = float(first)
            except Exception:
                target_view = 0.0
        else:
            target_view = float(requested_view)
        try:
            canvas.yview_moveto(max(0.0, min(1.0, target_view)))
        except Exception:
            pass

    def _on_mousewheel_scroll(self, event, scroll_frame):
        canvas, _, _, has_overflow = self._get_scroll_metrics(scroll_frame)
        if canvas is None:
            return None
        if not has_overflow:
            self._clamp_scroll_position(scroll_frame, 0.0)
            return "break"
        units = self._normalize_mousewheel_units(event)
        if units == 0:
            return "break"
        try:
            first, last = canvas.yview()
        except Exception:
            first, last = 0.0, 1.0
        if (units < 0 and first <= 0.001) or (units > 0 and last >= 0.999):
            self._clamp_scroll_position(scroll_frame, first)
            return "break"
        try:
            canvas.yview_scroll(units, "units")
            self.after_idle(lambda sf=scroll_frame: self._refresh_scroll_visuals(sf))
        except Exception:
            pass
        return "break"

    def _refresh_scroll_visuals(self, scroll_frame):
        canvas = self._get_scroll_canvas(scroll_frame)
        if canvas is None:
            return
        try:
            bbox = canvas.bbox("all")
            canvas.configure(scrollregion=bbox if bbox is not None else (0, 0, 0, 0))
        except Exception:
            pass
        try:
            canvas.update_idletasks()
        except Exception:
            pass
        self._clamp_scroll_position(scroll_frame)

    def refresh_texts(self):
        try:
            self.title(self.current_title)
        except Exception:
            pass
        ph_text = _tr_text(self._parent, "placeholder_tags")
        if self.lbl_folders_prompt is not None:
            self.lbl_folders_prompt.configure(text=self.folders_prompt)
        if self.lbl_files_prompt is not None:
            self.lbl_files_prompt.configure(text=self.files_prompt)
        if self.folders_entry is not None:
            self.folders_entry.configure(placeholder_text=ph_text)
        if self.files_entry is not None:
            self.files_entry.configure(placeholder_text=ph_text)
        if self.btn_auto is not None:
            self.btn_auto.configure(text=_tr_text(self._parent, "btn_autodetect"))
        if self.extra_checkbox is not None:
            self.extra_checkbox.configure(text=self.extra_checkbox_text or "")
        self.ok_button.configure(text=_tr_text(self._parent, "btn_ok"))
        self.cancel_button.configure(text=_tr_text(self._parent, "btn_cancel_simple"))

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
            self._resize_after_id = self.after(TAGS_DIALOG_LAYOUT_REFRESH_DELAY_MS, self._schedule_layout_refresh)
        except Exception:
            self._resize_after_id = None

    def _get_container_width(self, frame):
        visible_widths = []
        fallback_widths = []
        canvas = self._get_scroll_canvas(frame)
        if canvas is not None:
            try:
                width = int(canvas.winfo_width()) - 12
                if width > 0:
                    visible_widths.append(width)
            except Exception:
                pass
            try:
                width = int(canvas.winfo_reqwidth()) - 12
                if width > 0:
                    fallback_widths.append(width)
            except Exception:
                pass
        try:
            width = int(frame.winfo_width()) - 16
            if width > 0:
                visible_widths.append(width)
        except Exception:
            pass
        try:
            width = int(frame.winfo_reqwidth()) - 16
            if width > 0:
                fallback_widths.append(width)
        except Exception:
            pass
        try:
            width = int(self.main_frame.winfo_width()) - 40
            if width > 0:
                visible_widths.append(width)
        except Exception:
            pass
        try:
            width = int(self.winfo_width()) - 56
            if width > 0:
                visible_widths.append(width)
        except Exception:
            pass
        if visible_widths:
            return min(visible_widths)
        if fallback_widths:
            return min(fallback_widths)
        return 0

    def _get_horizontal_padding_total(self, padding_value):
        if isinstance(padding_value, (tuple, list)):
            total = 0
            for item in padding_value[:2]:
                try:
                    total += int(item)
                except Exception:
                    pass
            return total
        try:
            return int(padding_value) * 2
        except Exception:
            return 0

    def _estimate_pill_width(self, tag_name):
        try:
            label_width = int(self.tag_font.measure(str(tag_name)))
        except Exception:
            label_width = max(8, int(len(str(tag_name)) * TAGS_DIALOG_TAG_FONT_SIZE * 0.72))
        label_width += self._get_horizontal_padding_total(TAGS_DIALOG_PILL_LABEL_PADX)
        close_width = TAGS_DIALOG_PILL_CLOSE_SIZE + self._get_horizontal_padding_total(TAGS_DIALOG_PILL_CLOSE_PADX)
        return label_width + close_width + 6

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
            mix_color(bg_panel[1], NEUTRAL_WHITE, 0.08)
        )
        inactive_border = (
            mix_color(border_subtle[0], text_secondary[0], 0.30),
            mix_color(border_subtle[1], NEUTRAL_WHITE, 0.22)
        )
        inactive_hover = (
            mix_color(inactive_fg[0], text_secondary[0], 0.12),
            mix_color(inactive_fg[1], NEUTRAL_WHITE, 0.10)
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
        label = ctk.CTkLabel(self.main_frame, text=prompt, font=(FONT_FAMILY_PRIMARY, TAGS_DIALOG_SECTION_LABEL_FONT_SIZE, "bold"), text_color=text_color)
        label.grid(
            row=base_row, column=0,
            sticky="w", pady=TAGS_DIALOG_SECTION_LABEL_PADY, padx=TAGS_DIALOG_SECTION_LABEL_PADX)
        if section_id == "folders":
            self.lbl_folders_prompt = label
        else:
            self.lbl_files_prompt = label

        scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            label_text="",
            fg_color=_get_color_tuple("inner_area"),
            border_width=TAGS_DIALOG_SCROLL_BORDER_WIDTH,
            border_color=_get_color_tuple("card_border")
        )
        _style_scrollable(scroll_frame)
        scroll_frame.grid(row=base_row + 1, column=0, sticky="nsew", padx=TAGS_DIALOG_SCROLL_PADX)
        self._configure_mousewheel_for_scrollable(scroll_frame)

        input_container = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        input_container.grid(row=base_row + 2, column=0, sticky="ew", pady=TAGS_DIALOG_INPUT_PADY, padx=TAGS_DIALOG_INPUT_PADX)

        ph_text = _tr_text(self._parent, "placeholder_tags")

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
                txt_auto = _tr_text(self._parent, "btn_autodetect")
                btn_auto = ctk.CTkButton(
                    input_container,
                    text=txt_auto,
                    width=TAGS_DIALOG_AUTODETECT_BUTTON_WIDTH,
                    height=TAGS_DIALOG_AUTODETECT_BUTTON_HEIGHT,
                    command=self._on_autodetect
                )
                _style_button(btn_auto, "blue")
                btn_auto.pack(side="left", padx=TAGS_DIALOG_AUTODETECT_BUTTON_PADX)
                self.btn_auto = btn_auto

    def _on_autodetect(self):
        path = filedialog.askdirectory(parent=self, title=self._parent._tr("btn_autodetect"))
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
            log_error("Error autodetectando.", e, operation="autodetect_project_tags")
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
        canvas = self._get_scroll_canvas(frame)
        try:
            current_view = canvas.yview()[0] if canvas is not None else 0.0
        except Exception:
            current_view = 0.0
        for widget in frame.winfo_children(): widget.destroy()
        if not frame.winfo_exists(): return
        frame.update_idletasks()

        container_width = self._get_container_width(frame)
        if container_width < 220:
            return

        row_container = ctk.CTkFrame(frame, fg_color="transparent")
        row_container.pack(fill="x", anchor="nw")
        current_row = ctk.CTkFrame(row_container, fg_color="transparent")
        current_row.pack(fill="x", anchor="w", pady=TAGS_DIALOG_ROW_PADY)
        current_row_width = 0

        space_between_pills = TAGS_DIALOG_PILL_SPACING
        wrap_safety_px = max(4, TAGS_DIALOG_WRAP_SAFETY_PX)

        for index, tag_data in enumerate(tag_list):
            estimated_pill_width = self._estimate_pill_width(tag_data["nombre"])
            projected_width = current_row_width + ((space_between_pills + wrap_safety_px) if current_row_width > 0 else 0) + estimated_pill_width

            if current_row_width > 0 and projected_width > container_width:
                current_row = ctk.CTkFrame(row_container, fg_color="transparent")
                current_row.pack(fill="x", anchor="w", pady=TAGS_DIALOG_ROW_PADY)
                current_row_width = 0

            pill_frame = self._create_pill_frame(current_row, tag_data, index, tag_list)
            pill_frame.pack(side="left", padx=(0, space_between_pills))
            pill_frame.update_idletasks()

            pill_width = max(estimated_pill_width, pill_frame.winfo_reqwidth(), pill_frame.winfo_width())
            current_row_width += (space_between_pills if current_row_width > 0 else 0) + pill_width

        self._configure_mousewheel_for_scrollable(frame)
        try:
            frame.update_idletasks()
        except Exception:
            pass
        if canvas is not None:
            try:
                bbox = canvas.bbox("all")
                canvas.configure(scrollregion=bbox if bbox is not None else (0, 0, 0, 0))
            except Exception:
                pass
            self._clamp_scroll_position(frame, current_view)
            self.after_idle(lambda sf=frame: self._refresh_scroll_visuals(sf))

    def _create_pill_frame(self, parent, tag_data, index, tag_list):
        tag_name, tag_state = tag_data["nombre"], tag_data["estado"]
        colors = self.tag_colors[tag_state]

        pill_frame = ctk.CTkFrame(parent, fg_color=colors["fg"], border_color=colors.get("border", colors["fg"]), border_width=colors.get("border_width", 0), corner_radius=TAGS_DIALOG_PILL_RADIUS)

        label = ctk.CTkLabel(pill_frame, text=tag_name, text_color=colors["text"], font=self.tag_font)
        label.pack(side="left", padx=TAGS_DIALOG_PILL_LABEL_PADX, pady=TAGS_DIALOG_PILL_LABEL_PADY)

        close_button = ctk.CTkButton(
            pill_frame,
            text="✕",
            width=TAGS_DIALOG_PILL_CLOSE_SIZE,
            height=TAGS_DIALOG_PILL_CLOSE_SIZE,
            corner_radius=TAGS_DIALOG_PILL_CLOSE_RADIUS,
            font=(FONT_FAMILY_PRIMARY, DIALOG_BUTTON_FONT_SIZE, "bold"),
            text_color=colors["text"],
            fg_color="transparent",
            hover_color=colors["hover"],
            command=lambda i=index, l=tag_list: self._delete_tag(i, l)
        )

        close_button.pack(side="right", padx=TAGS_DIALOG_PILL_CLOSE_PADX, pady=TAGS_DIALOG_PILL_CLOSE_PADY)
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
