
import customtkinter as ctk
import os
from view.tooltip import CustomTooltip, _get_monitor_workarea_for_point
from view.ui_constants import COLORS, get_button_tokens, get_color_pair, DIALOG_ICON_DELAY_MS, DIALOG_PREPARE_DELAY_MS, DIALOG_CENTER_RETRY_DELAY_MS, DIALOG_CENTER_MAX_ATTEMPTS, DIALOG_INITIAL_ALPHA, DIALOG_REVEAL_OFFSET_Y, DIALOG_REVEAL_STEP_PX, DIALOG_FADE_IN_STEP, DIALOG_FADE_IN_INTERVAL_MS, DIALOG_FADE_OUT_STEP, DIALOG_FADE_OUT_INTERVAL_MS
from view.ui_assets import get_app_icon_path

MESSAGE_AUTO_CLOSE_SECONDS = 10


def _restore_parent_modal_state(parent):
    try:
        if parent and hasattr(parent, "restore_ui_from_modal"):
            parent.restore_ui_from_modal()
    except Exception:
        pass

# =============================================================================
# UTILIDADES DE ESTILO
# =============================================================================

def _get_color_tuple(key: str) -> tuple[str, str]:
    key_map = {
        "bg": "bg_base",
        "card": "bg_dialog",
        "card_border": "border_subtle",
        "inner_area": "bg_panel",
        "text": "text_primary",
        "text_secondary": "text_secondary",
        "text_muted": "text_muted",
        "separator_line": "separator_line",
        "border_subtle": "border_subtle",
        "border_strong": "border_strong",
        "bg_panel": "bg_panel",
        "bg_card": "bg_card",
        "bg_dialog": "bg_dialog"
    }
    actual_key = key_map.get(key, key)
    return get_color_pair(actual_key)


def _style_button(btn: ctk.CTkButton, color_type="blue"):
    palette = get_button_tokens(color_type)

    btn.configure(
        corner_radius=16,
        height=34,
        font=("Segoe UI", 12, "bold"),
        text_color=palette.get("text", _get_color_tuple("text")),
        fg_color=palette["bg"],
        hover_color=palette["hover"],
        border_color=palette["border"],
        border_width=1
    )


def _style_entry(widget):
    widget.configure(
        height=34,
        corner_radius=12,
        fg_color=_get_color_tuple("bg_panel"),
        border_color=_get_color_tuple("border_subtle"),
        text_color=_get_color_tuple("text"),
        placeholder_text_color=_get_color_tuple("text_muted")
    )


def _style_option_menu(widget):
    blue = get_button_tokens("blue")
    widget.configure(
        height=34,
        corner_radius=12,
        fg_color=_get_color_tuple("bg_panel"),
        button_color=blue["bg"],
        button_hover_color=blue["hover"],
        text_color=_get_color_tuple("text"),
        dropdown_fg_color=_get_color_tuple("bg_card"),
        dropdown_hover_color=_get_color_tuple("bg_panel"),
        dropdown_text_color=_get_color_tuple("text")
    )


def _style_checkbox(widget):
    blue = get_button_tokens("blue")
    widget.configure(
        text_color=_get_color_tuple("text"),
        fg_color=blue["bg"],
        hover_color=blue["hover"],
        border_color=_get_color_tuple("border_strong"),
        checkmark_color=_get_color_tuple("bg_elevated")
    )


def _style_scrollable(widget):
    widget.configure(
        fg_color=_get_color_tuple("bg_card"),
        border_width=1,
        border_color=get_color_pair("card_border"),
        scrollbar_button_color=get_color_pair("accent_blue"),
        scrollbar_button_hover_color=get_color_pair("accent_blue_hover")
    )


def _get_widget_window_rect(widget):
    try:
        if not widget or not widget.winfo_exists():
            raise RuntimeError
        try:
            import ctypes
            from ctypes import wintypes

            hwnd = int(widget.winfo_id())

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", wintypes.LONG),
                    ("top", wintypes.LONG),
                    ("right", wintypes.LONG),
                    ("bottom", wintypes.LONG),
                ]

            rect = RECT()
            if ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect)):
                return int(rect.left), int(rect.top), int(rect.right), int(rect.bottom)
        except Exception:
            pass

        widget.update_idletasks()
        x = int(widget.winfo_x())
        y = int(widget.winfo_y())
        w = int(widget.winfo_width())
        h = int(widget.winfo_height())
        return x, y, x + w, y + h
    except Exception:
        return 0, 0, 0, 0


def _get_widget_workarea(widget):
    try:
        if widget and widget.winfo_exists():
            rect = _get_widget_window_rect(widget)
            if rect != (0, 0, 0, 0):
                cx = int((rect[0] + rect[2]) / 2)
                cy = int((rect[1] + rect[3]) / 2)
            else:
                cx = int(widget.winfo_pointerx())
                cy = int(widget.winfo_pointery())
            return _get_monitor_workarea_for_point(cx, cy, widget)
    except Exception:
        pass
    return 0, 0, 1920, 1080


def _get_centered_position(target_rect, win_w: int, win_h: int):
    left, top, right, bottom = target_rect
    area_w = max(1, int(right - left))
    area_h = max(1, int(bottom - top))
    x = int(left + (area_w - int(win_w)) / 2)
    y = int(top + (area_h - int(win_h)) / 2)
    return x, y


# =============================================================================
# CLASE BASE PARA DIALOGOS
# =============================================================================

class BaseDialog(ctk.CTkToplevel):

    def __init__(self, parent, title: str, persistent: bool = False, defer_show: bool = False):
        CustomTooltip.hide_global()

        super().__init__(parent)
        self.parent = parent
        self._is_base_dialog = True
        self._persistent_mode = bool(persistent)
        self._defer_show = bool(defer_show)
        self._done_var = ctk.BooleanVar(master=parent, value=False)
        self._prepare_after_id = None

        try:
            self.withdraw()
            self.attributes("-alpha", 0.0)

            if not self._defer_show and hasattr(parent, "dim_ui_for_modal"):
                parent.dim_ui_for_modal()

            try:
                self.transient(parent)
            except Exception:
                pass

            self.title(title)
            self.resizable(False, False)

            self.configure(fg_color=_get_color_tuple("bg"))

            self._closing_grab_released = False
            self._escape_bindtag = f"__esc_close_{id(self)}"
            self._reveal_target_y = None

            try:
                self.bind_class(self._escape_bindtag, "<Escape>", self._on_escape_key, add="+")
            except Exception:
                self.bind("<Escape>", self._on_escape_key, add="+")

            self.bind("<Map>", self._install_escape_bindtags, add="+")

            self.after(DIALOG_ICON_DELAY_MS, self._set_icon_safe)
            if not self._defer_show:
                self._prepare_after_id = self.after(DIALOG_PREPARE_DELAY_MS, self._prepare_geometry)

            self.result = None
            self.protocol("WM_DELETE_WINDOW", self._close_with_fade_out)
        except Exception:
            _restore_parent_modal_state(parent)
            try:
                if self.winfo_exists():
                    self.destroy()
            except Exception:
                pass
            raise

    def _set_icon_safe(self):
        try:
            if not self.winfo_exists(): return
            icon_path = get_app_icon_path()
            if icon_path and os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                self.after(100, lambda: self.iconbitmap(icon_path))
        except Exception:
            pass

    def _create_card_frame(self) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            self,
            fg_color=_get_color_tuple("card"),
            border_color=_get_color_tuple("card_border"),
            border_width=1,
            corner_radius=18
        )
        card.pack(expand=True, fill="both", padx=15, pady=15)
        return card

    def _on_escape_key(self, event=None):
        self._close_with_fade_out()
        return "break"

    def _install_escape_bindtags(self, event=None):
        try:
            if not self.winfo_exists(): return
        except Exception:
            return

        def apply_tag(widget):
            try:
                tags = list(widget.bindtags())
            except Exception:
                return
            if self._escape_bindtag not in tags:
                tags.insert(0, self._escape_bindtag)
            try:
                widget.bindtags(tuple(tags))
            except Exception:
                pass
            try:
                for child in widget.winfo_children(): apply_tag(child)
            except Exception:
                pass

        apply_tag(self)

    def present(self):
        if not self.winfo_exists():
            return
        self._closing_grab_released = False
        self.result = None
        try:
            self._done_var.set(False)
        except Exception:
            pass
        CustomTooltip.hide_global()
        if hasattr(self.parent, "dim_ui_for_modal"):
            self.parent.dim_ui_for_modal()
        if self._prepare_after_id:
            try:
                self.after_cancel(self._prepare_after_id)
            except Exception:
                pass
            self._prepare_after_id = None
        self._prepare_after_id = self.after(DIALOG_PREPARE_DELAY_MS, self._prepare_geometry)

    def wait_result(self):
        try:
            self.parent.wait_variable(self._done_var)
        except Exception:
            pass
        return self.result

    def _finalize_close(self):
        if self._prepare_after_id:
            try:
                self.after_cancel(self._prepare_after_id)
            except Exception:
                pass
            self._prepare_after_id = None
        try:
            self._done_var.set(True)
        except Exception:
            pass
        if self._persistent_mode:
            try:
                self.withdraw()
                self.attributes("-alpha", 0.0)
            except Exception:
                pass
        else:
            self.destroy()
        if hasattr(self.parent, "restore_ui_from_modal"):
            self.parent.restore_ui_from_modal()

    def _prepare_geometry(self):
        if not self.winfo_exists(): return

        self._prepare_after_id = None
        try:
            self.withdraw()
            self.attributes("-alpha", 0.0)
        except Exception:
            pass
        self.update_idletasks()
        self.after(DIALOG_CENTER_RETRY_DELAY_MS, lambda: self._try_center_window(0))

    def _get_target_rect(self):
        try:
            if self.master and self.master.winfo_exists():
                if hasattr(self.master, "get_real_window_rect"):
                    rect = self.master.get_real_window_rect()
                else:
                    rect = _get_widget_window_rect(self.master)
                if rect != (0, 0, 0, 0):
                    return rect
        except Exception:
            pass
        return _get_widget_workarea(self)

    def _try_center_window(self, attempt=0):
        if not self.winfo_exists(): return

        try:
            self.update_idletasks()
            w = max(int(self.winfo_width()), int(self.winfo_reqwidth()))
            h = max(int(self.winfo_height()), int(self.winfo_reqheight()))

            if w < 50 or h < 50:
                self.after(DIALOG_CENTER_RETRY_DELAY_MS, lambda: self._try_center_window(attempt))
                return

            target_rect = self._get_target_rect()
            target_cx = int((target_rect[0] + target_rect[2]) / 2)
            target_cy = int((target_rect[1] + target_rect[3]) / 2)

            if attempt == 0:
                x, y = _get_centered_position(target_rect, w, h)
                self.geometry(f"+{x}+{y}")
                self.deiconify()
                self.attributes("-alpha", 0.0)
                self.lift()
                self.after(DIALOG_CENTER_RETRY_DELAY_MS, lambda: self._try_center_window(1))
                return

            actual_rect = _get_widget_window_rect(self)
            actual_cx = int((actual_rect[0] + actual_rect[2]) / 2)
            actual_cy = int((actual_rect[1] + actual_rect[3]) / 2)
            dx = target_cx - actual_cx
            dy = target_cy - actual_cy

            if (abs(dx) > 1 or abs(dy) > 1) and attempt < DIALOG_CENTER_MAX_ATTEMPTS:
                self.geometry(f"+{int(self.winfo_x()) + dx}+{int(self.winfo_y()) + dy}")
                self.after(DIALOG_CENTER_RETRY_DELAY_MS, lambda: self._try_center_window(attempt + 1))
                return

            self._reveal_target_y = int(self.winfo_y())
            if DIALOG_REVEAL_OFFSET_Y > 0:
                self.geometry(f"+{int(self.winfo_x())}+{self._reveal_target_y + DIALOG_REVEAL_OFFSET_Y}")

            self.lift()
            self.focus_force()
            self.grab_set()
            self.attributes("-alpha", DIALOG_INITIAL_ALPHA)
            self._fade_in()

        except Exception:
            self.attributes("-alpha", 1.0)

    def _fade_in(self):
        if not self.winfo_exists(): return
        try:
            alpha = float(self.attributes("-alpha"))
        except Exception:
            alpha = 1.0

        target_y = self._reveal_target_y
        if target_y is not None:
            try:
                current_y = int(self.winfo_y())
                if current_y > target_y:
                    step = min(DIALOG_REVEAL_STEP_PX, current_y - target_y)
                    self.geometry(f"+{int(self.winfo_x())}+{current_y - step}")
                else:
                    self._reveal_target_y = current_y
            except Exception:
                self._reveal_target_y = None

        if alpha < 1.0:
            new_alpha = min(alpha + DIALOG_FADE_IN_STEP, 1.0)
            self.attributes("-alpha", new_alpha)
            self.after(DIALOG_FADE_IN_INTERVAL_MS, self._fade_in)
        else:
            self.focus_set()

    def _close_with_fade_out(self, event=None):
        if not self._closing_grab_released:
            try:
                self.grab_release()
            except Exception:
                pass
            self._closing_grab_released = True

        try:
            alpha = self.attributes("-alpha")
        except:
            alpha = 1.0

        if alpha > 0:
            alpha = max(alpha - DIALOG_FADE_OUT_STEP, 0.0)
            self.attributes("-alpha", alpha)
            self.after(DIALOG_FADE_OUT_INTERVAL_MS, self._close_with_fade_out)
        else:
            self._finalize_close()

    def _on_ok(self, event=None):
        self._close_with_fade_out()

    def _on_cancel(self, event=None):
        self.result = None
        self._close_with_fade_out()


# =============================================================================
# DIALOGOS ESPECIFICOS
# =============================================================================

class MessageDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)

        self._auto_close_after_id = None
        self._schedule_auto_close()

        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=350,
            justify="center",
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(20, 20))

        btn_text = parent._tr("btn_ok") if hasattr(parent, "_tr") else "OK"

        ok_button = ctk.CTkButton(
            card,
            text=btn_text,
            width=110,
            command=self._on_ok
        )
        _style_button(ok_button, "blue")
        ok_button.pack(pady=(0, 20))
        ok_button.focus_set()

        self.bind("<Return>", self._on_ok)

    def _schedule_auto_close(self):
        self._cancel_auto_close()
        try:
            seconds = float(MESSAGE_AUTO_CLOSE_SECONDS)
        except Exception:
            seconds = 0.0
        if seconds <= 0: return
        ms = max(1, int(seconds * 1000))
        self._auto_close_after_id = self.after(ms, self._auto_close)

    def _cancel_auto_close(self):
        if self._auto_close_after_id:
            try:
                self.after_cancel(self._auto_close_after_id)
            except Exception:
                pass
            self._auto_close_after_id = None

    def _auto_close(self):
        self._auto_close_after_id = None
        try:
            if not self.winfo_exists(): return
        except Exception:
            return
        self.result = None
        self._close_with_fade_out()

    def _close_with_fade_out(self, event=None):
        self._cancel_auto_close()
        return super()._close_with_fade_out(event)

    def _on_ok(self, event=None):
        self._cancel_auto_close()
        self.result = True
        super()._on_ok(event)


class ConfirmDialog(BaseDialog):
    def __init__(self, parent, title, message):
        super().__init__(parent, title)
        self.result = False

        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=350,
            justify="center",
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(25, 25))

        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(pady=(0, 20))

        txt_yes = parent._tr("btn_yes") if hasattr(parent, "_tr") else "Sí"
        txt_no = parent._tr("btn_no") if hasattr(parent, "_tr") else "No"

        btn_yes = ctk.CTkButton(button_frame, text=txt_yes, width=100, command=self._on_yes)
        _style_button(btn_yes, "green")
        btn_yes.pack(side="left", padx=10)

        btn_no = ctk.CTkButton(button_frame, text=txt_no, width=100, command=self._on_no)
        _style_button(btn_no, "red")
        btn_no.pack(side="left", padx=10)

    def _on_yes(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_no(self, event=None): self.result = False; self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message):
        dialog = None
        try:
            dialog = cls(parent, title, message)
            parent.wait_window(dialog)
            return dialog.result
        except Exception:
            _restore_parent_modal_state(parent)
            return False
        finally:
            if dialog is not None:
                try:
                    if dialog.winfo_exists():
                        dialog.destroy()
                except Exception:
                    pass


class ExternalLinkDialog(BaseDialog):
    def __init__(self, parent, title, message, target_label=None, continue_text=None, cancel_text=None):
        super().__init__(parent, title)
        self.result = False
        self.geometry("430x240")

        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=360,
            justify="center",
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(24, 14))

        if target_label:
            target_box = ctk.CTkFrame(
                card,
                fg_color=_get_color_tuple("bg_panel"),
                border_color=_get_color_tuple("border_subtle"),
                border_width=1,
                corner_radius=14
            )
            target_box.pack(fill="x", padx=20, pady=(0, 18))

            ctk.CTkLabel(
                target_box,
                text=target_label,
                wraplength=330,
                justify="center",
                font=("Segoe UI", 11),
                text_color=_get_color_tuple("text_secondary")
            ).pack(fill="x", padx=12, pady=10)

        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(pady=(0, 20))

        if continue_text is None:
            continue_text = parent._tr("btn_continue_external") if hasattr(parent, "_tr") else "Continue"
        if cancel_text is None:
            cancel_text = parent._tr("btn_cancel_simple") if hasattr(parent, "_tr") else "Cancel"

        btn_continue = ctk.CTkButton(button_frame, text=continue_text, width=126, command=self._on_continue)
        _style_button(btn_continue, "blue")
        btn_continue.pack(side="left", padx=8)

        btn_cancel = ctk.CTkButton(button_frame, text=cancel_text, width=126, command=self._on_cancel)
        _style_button(btn_cancel, "red")
        btn_cancel.pack(side="left", padx=8)
        btn_continue.focus_set()

        self.bind("<Return>", self._on_continue)

    def _on_continue(self, event=None): self.result = True; self._close_with_fade_out()

    def _on_cancel(self, event=None): self.result = False; self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, title, message, target_label=None, continue_text=None, cancel_text=None):
        dialog = None
        try:
            dialog = cls(parent, title, message, target_label, continue_text, cancel_text)
            parent.wait_window(dialog)
            return dialog.result
        except Exception:
            _restore_parent_modal_state(parent)
            return False
        finally:
            if dialog is not None:
                try:
                    if dialog.winfo_exists():
                        dialog.destroy()
                except Exception:
                    pass


class ChoiceDialog(BaseDialog):
    def __init__(self, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        super().__init__(parent, title)
        self.option1_value, self.option2_value = option1_value, option2_value

        self.geometry("400x200")

        card = self._create_card_frame()

        ctk.CTkLabel(
            card,
            text=message,
            wraplength=340,
            font=("Segoe UI", 13),
            text_color=_get_color_tuple("text")
        ).pack(fill="x", padx=20, pady=(25, 15))

        btn1 = ctk.CTkButton(card, text=option1_text, width=220, command=self._on_option1)
        _style_button(btn1, "blue")
        btn1.pack(pady=(5, 8))

        btn2 = ctk.CTkButton(card, text=option2_text, width=220, command=self._on_option2)
        _style_button(btn2, "blue")
        btn2.pack(pady=(0, 20))

    def _on_option1(self): self.result = self.option1_value; super()._on_ok()

    def _on_option2(self): self.result = self.option2_value; super()._on_ok()

    @classmethod
    def ask(cls, parent, title, message, option1_text, option2_text, option1_value, option2_value):
        dialog = None
        try:
            dialog = cls(parent, title, message, option1_text, option2_text, option1_value, option2_value)
            parent.wait_window(dialog)
            return dialog.result
        except Exception:
            _restore_parent_modal_state(parent)
            return None
        finally:
            if dialog is not None:
                try:
                    if dialog.winfo_exists():
                        dialog.destroy()
                except Exception:
                    pass




