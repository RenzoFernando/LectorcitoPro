import copy

import customtkinter as ctk

from i18n.translations import translate_default
from view.dialogs import (
    BaseDialog,
    ConfirmDialog,
    _get_color_tuple,
    _style_button,
    _style_entry,
    _style_scrollable,
)
from view.ui_assets import load_add_icon, load_delete_icon
from view.ui_constants import (
    ACTION_BUTTON_TOKENS,
    FONT_FAMILY_PRIMARY,
    PROFILE_ITEM_BORDER_WIDTH,
    PROFILE_ITEM_DELETE_BUTTON_SIZE,
    PROFILE_ITEM_DELETE_PADX,
    PROFILE_ITEM_FONT_SIZE,
    PROFILE_ITEM_LABEL_PADX,
    PROFILE_ITEM_LABEL_PADY,
    PROFILE_ITEM_PADY,
    PROFILE_ITEM_RADIUS,
    PROFILES_DIALOG_ACTION_BUTTON_PADX,
    PROFILES_DIALOG_ACTION_BUTTON_PADY,
    PROFILES_DIALOG_ACTION_BUTTON_WIDTH,
    PROFILES_DIALOG_ADD_BUTTON_WIDTH,
    PROFILES_DIALOG_BOTTOM_PADX,
    PROFILES_DIALOG_BOTTOM_PADY,
    PROFILES_DIALOG_ENTRY_PADX,
    PROFILES_DIALOG_HEIGHT,
    PROFILES_DIALOG_SCROLL_HEIGHT,
    PROFILES_DIALOG_SCROLL_PADX,
    PROFILES_DIALOG_SCROLL_PADY,
    PROFILES_DIALOG_TITLE_FONT_SIZE,
    PROFILES_DIALOG_TITLE_PADY,
    PROFILES_DIALOG_WIDTH,
)

# =============================================================================
# DIALOGO DE GESTION DE PERFILES
# =============================================================================


def _tr_text(parent, key: str, *args):
    tr_callable = getattr(parent, "_tr", None)
    if callable(tr_callable):
        try:
            return tr_callable(key, *args)
        except Exception:
            pass
    return translate_default(key, *args)


class ProfilesDialog(BaseDialog):
    def __init__(
        self,
        parent,
        profiles_meta: dict | None = None,
        active_id: str = "default",
        on_save_callback=None,
        persistent: bool = False,
        defer_show: bool = False,
    ):
        title = _tr_text(parent, "dlg_profiles_title")
        super().__init__(parent, title, persistent=persistent, defer_show=defer_show)

        self.profiles = {}
        self.active_id = "default"
        self.selected_id = "default"
        self.result = None
        self.parent_view = parent
        self.on_save_callback = on_save_callback

        self.colors = {
            "card": _get_color_tuple("card"),
            "text": _get_color_tuple("text"),
            "selected": ("#EFF6FF", "#172554"),
            "selected_text": ("#2563EB", "#93C5FD"),
            "selected_border": ("#2563EB", "#3B82F6"),
            "panel": _get_color_tuple("bg_panel"),
            "border": _get_color_tuple("border_subtle"),
        }
        self.add_icon = load_add_icon((14, 14))
        self.delete_icon = load_delete_icon((14, 14))

        self._build_ui()
        self.load_state(
            profiles_meta if profiles_meta is not None else {"default": {}},
            active_id,
            on_save_callback,
        )

    def _build_ui(self):
        self.geometry(f"{PROFILES_DIALOG_WIDTH}x{PROFILES_DIALOG_HEIGHT}")

        self.main_frame = self._create_card_frame()

        self.lbl_select_profile = ctk.CTkLabel(
            self.main_frame,
            text=_tr_text(self.parent_view, "lbl_select_profile"),
            font=(FONT_FAMILY_PRIMARY, PROFILES_DIALOG_TITLE_FONT_SIZE, "bold"),
            text_color=self.colors["text"],
        )
        self.lbl_select_profile.pack(pady=PROFILES_DIALOG_TITLE_PADY)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame, fg_color="transparent", height=PROFILES_DIALOG_SCROLL_HEIGHT
        )
        _style_scrollable(self.scroll_frame)
        self.scroll_frame.pack(
            fill="both",
            expand=True,
            padx=PROFILES_DIALOG_SCROLL_PADX,
            pady=PROFILES_DIALOG_SCROLL_PADY,
        )

        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(
            fill="x", padx=PROFILES_DIALOG_BOTTOM_PADX, pady=PROFILES_DIALOG_BOTTOM_PADY
        )

        self.entry_new = ctk.CTkEntry(
            self.bottom_frame, placeholder_text=_tr_text(self.parent_view, "ph_new_profile")
        )
        _style_entry(self.entry_new)
        self.entry_new.pack(side="left", fill="x", expand=True, padx=PROFILES_DIALOG_ENTRY_PADX)

        self.btn_add = ctk.CTkButton(
            self.bottom_frame,
            text="",
            image=self.add_icon,
            width=PROFILES_DIALOG_ADD_BUTTON_WIDTH,
            command=self._add_profile,
        )
        _style_button(self.btn_add, "blue")
        self.btn_add.pack(side="right")

        self.entry_new.bind("<Return>", lambda e: self._add_profile())

        self.actions_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.actions_frame.pack(
            fill="x",
            padx=PROFILES_DIALOG_BOTTOM_PADX,
            pady=PROFILES_DIALOG_ACTION_BUTTON_PADY,
        )

        self.btn_cancel = ctk.CTkButton(
            self.actions_frame,
            text=_tr_text(self.parent_view, "btn_cancel_simple"),
            width=PROFILES_DIALOG_ACTION_BUTTON_WIDTH,
            command=self._on_cancel,
        )
        _style_button(self.btn_cancel, "red")
        self.btn_cancel.pack(side="left", padx=PROFILES_DIALOG_ACTION_BUTTON_PADX)

        self.btn_apply = ctk.CTkButton(
            self.actions_frame,
            text=_tr_text(self.parent_view, "btn_apply"),
            width=PROFILES_DIALOG_ACTION_BUTTON_WIDTH,
            command=self._on_ok,
        )
        _style_button(self.btn_apply, "green")
        self.btn_apply.pack(side="right", padx=PROFILES_DIALOG_ACTION_BUTTON_PADX)

    def refresh_texts(self):
        try:
            self.title(self.parent_view._tr("dlg_profiles_title"))
        except Exception:
            pass
        self.lbl_select_profile.configure(text=_tr_text(self.parent_view, "lbl_select_profile"))
        self.btn_cancel.configure(text=_tr_text(self.parent_view, "btn_cancel_simple"))
        self.btn_apply.configure(text=_tr_text(self.parent_view, "btn_apply"))
        self._redraw_list()

    def load_state(self, profiles_meta: dict, active_id: str, on_save_callback=None):
        self.profiles = copy.deepcopy(profiles_meta) if profiles_meta else {"default": {}}
        self.active_id = active_id if active_id in self.profiles else "default"
        self.selected_id = self.active_id
        self.on_save_callback = on_save_callback
        self.result = None
        self.refresh_texts()
        try:
            self.entry_new.delete(0, "end")
        except Exception:
            pass

    def _redraw_list(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        keys = list(self.profiles.keys())
        keys.sort(key=lambda x: (0 if x == "default" else 1, x.lower()))

        for pid in keys:
            self._create_profile_item(pid)

        if len(self.profiles) >= 5:
            self.entry_new.configure(
                state="disabled", placeholder_text=self.parent_view._tr("msg_max_profiles_reached")
            )
            self.btn_add.configure(state="disabled")
        else:
            self.entry_new.configure(
                state="normal", placeholder_text=self.parent_view._tr("ph_new_profile")
            )
            self.btn_add.configure(state="normal")

        self._update_apply_state()

    def _create_profile_item(self, pid):
        is_active = pid == self.active_id
        is_selected = pid == self.selected_id
        is_default = pid == "default"

        display_name = self.parent_view._tr("lbl_default_name") if pid == "default" else pid
        suffix = self.parent_view._tr("lbl_active_suffix") if is_active else ""

        item_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.colors["selected"] if is_selected else self.colors["panel"],
            border_width=PROFILE_ITEM_BORDER_WIDTH,
            border_color=self.colors["selected_border"] if is_selected else self.colors["border"],
            corner_radius=PROFILE_ITEM_RADIUS,
        )
        item_frame.pack(fill="x", pady=PROFILE_ITEM_PADY)

        lbl = ctk.CTkLabel(
            item_frame,
            text=f"  {display_name}{suffix}",
            font=(FONT_FAMILY_PRIMARY, PROFILE_ITEM_FONT_SIZE, "bold" if is_selected else "normal"),
            text_color=self.colors["selected_text"] if is_selected else self.colors["text"],
        )
        lbl.pack(side="left", padx=PROFILE_ITEM_LABEL_PADX, pady=PROFILE_ITEM_LABEL_PADY)

        item_frame.bind("<Button-1>", lambda e, p=pid: self._select_profile(p))
        lbl.bind("<Button-1>", lambda e, p=pid: self._select_profile(p))

        if not is_default:
            destructive_bg = (
                ACTION_BUTTON_TOKENS["light"]["destructive"]["bg"],
                ACTION_BUTTON_TOKENS["dark"]["destructive"]["bg"],
            )
            destructive_hover = (
                ACTION_BUTTON_TOKENS["light"]["destructive"]["hover"],
                ACTION_BUTTON_TOKENS["dark"]["destructive"]["hover"],
            )
            destructive_border = (
                ACTION_BUTTON_TOKENS["light"]["destructive"]["border"],
                ACTION_BUTTON_TOKENS["dark"]["destructive"]["border"],
            )
            btn_del = ctk.CTkButton(
                item_frame,
                text="",
                image=self.delete_icon,
                width=PROFILE_ITEM_DELETE_BUTTON_SIZE,
                height=PROFILE_ITEM_DELETE_BUTTON_SIZE,
                fg_color=destructive_bg,
                hover_color=destructive_hover,
                border_width=1,
                border_color=destructive_border,
                command=lambda p=pid: self._delete_profile(p),
            )
            btn_del.pack(side="right", padx=PROFILE_ITEM_DELETE_PADX)

    def _add_profile(self):
        name = self.entry_new.get().strip()
        if not name:
            return
        pid = name.lower().replace(" ", "_")

        if pid in self.profiles:
            self.parent_view.show_message("error_title", "msg_profile_exists")
            return

        if len(self.profiles) >= 5:
            return

        self.profiles[pid] = "NEW"
        self.entry_new.delete(0, "end")

        if self.on_save_callback:
            self.on_save_callback(copy.deepcopy(self.profiles), self.active_id)

        self._redraw_list()

    def _restore_after_child_dialog(self):
        try:
            if self.winfo_exists() and self._modal_active:
                self.lift()
                self.focus_force()
                self.grab_set()
        except Exception:
            pass

    def _delete_profile(self, pid):
        if pid == "default":
            return

        confirmed = ConfirmDialog.ask(
            self,
            self.parent_view._tr("confirm_del_title"),
            self.parent_view._tr("confirm_del_profile", pid),
        )
        self._restore_after_child_dialog()
        if not confirmed:
            return

        del self.profiles[pid]
        if pid == self.active_id:
            self.active_id = "default"
        if pid == self.selected_id:
            self.selected_id = self.active_id if self.active_id in self.profiles else "default"

        if self.on_save_callback:
            self.on_save_callback(copy.deepcopy(self.profiles), self.active_id)

        self._redraw_list()

    def _update_apply_state(self):
        state = "normal" if self.selected_id != self.active_id else "disabled"
        try:
            self.btn_apply.configure(state=state)
        except Exception:
            pass

    def _select_profile(self, pid):
        if pid not in self.profiles:
            return
        self.selected_id = pid
        self._redraw_list()

    def present(self):
        super().present()
        try:
            self.entry_new.focus_set()
        except Exception:
            pass

    def _on_ok(self, event=None):
        if self.selected_id not in self.profiles:
            return
        self.result = (self.selected_id, copy.deepcopy(self.profiles))
        self._close_with_fade_out()
