import customtkinter as ctk
from view.dialogs import BaseDialog, _style_button, _get_color_tuple, ConfirmDialog
from view.ui_constants import COLORS


# =============================================================================
# DIALOGO DE GESTION DE PERFILES
# =============================================================================

class ProfilesDialog(BaseDialog):
    def __init__(self, parent, profiles_meta: dict, active_id: str, on_save_callback=None):
        title = parent._tr("dlg_profiles_title") if hasattr(parent, "_tr") else "Perfiles"
        super().__init__(parent, title)

        # Ocultamos y quitamos opacidad para evitar parpadeos visuales al calcular geometria
        self.withdraw()
        self.attributes("-alpha", 0.0)

        self.profiles = profiles_meta.copy()
        self.active_id = active_id
        self.result = None
        self.parent_view = parent
        self.on_save_callback = on_save_callback

        self.colors = {
            "card": _get_color_tuple("card"),
            "text": _get_color_tuple("text"),
            "selected": COLORS["button"]["blue"]["bg"],
            "hover": COLORS["sidebar_hover"]
        }

        self._build_ui()
        self._redraw_list()

        # Damos tiempo al sistema para "respirar" antes de calcular la geometria final
        self.after(300, self._step_calculate_geometry)

    def _build_ui(self):
        self.geometry("450x500")

        self.main_frame = self._create_card_frame()

        ctk.CTkLabel(
            self.main_frame,
            text=self.parent_view._tr("lbl_select_profile") if hasattr(self.parent_view,
                                                                       "_tr") else "Seleccione un Perfil",
            font=("Segoe UI", 14, "bold"),
            text_color=self.colors["text"]
        ).pack(pady=(20, 10))

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            fg_color="transparent",
            height=250
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.bottom_frame.pack(fill="x", padx=20, pady=20)

        self.entry_new = ctk.CTkEntry(
            self.bottom_frame,
            placeholder_text=self.parent_view._tr("ph_new_profile") if hasattr(self.parent_view,
                                                                               "_tr") else "Nombre nuevo perfil..."
        )
        self.entry_new.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.btn_add = ctk.CTkButton(
            self.bottom_frame,
            text="+",
            width=40,
            command=self._add_profile
        )
        _style_button(self.btn_add, "blue")
        self.btn_add.pack(side="right")

        self.entry_new.bind("<Return>", lambda e: self._add_profile())

    def _step_calculate_geometry(self):
        # Calcula el centro exacto sin mostrar la ventana aun
        try:
            self.update_idletasks()

            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            win_w = 450
            win_h = 500

            x = (screen_w // 2) - (win_w // 2)
            y = (screen_h // 2) - (win_h // 2)

            self.geometry(f"{win_w}x{win_h}+{x}+{y}")

            self.after(100, self._step_show_window)
        except Exception:
            self.geometry("450x500")
            self.deiconify()
            self.attributes("-alpha", 1.0)

    def _step_show_window(self):
        # Hace visible la ventana suavemente y activa la modalidad
        self.deiconify()
        self.attributes("-alpha", 1.0)
        self.lift()
        self.focus_force()
        self.grab_set()

    def _redraw_list(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        keys = list(self.profiles.keys())
        keys.sort(key=lambda x: (0 if x == "default" else 1, x.lower()))

        for pid in keys:
            self._create_profile_item(pid)

        # Limite de perfiles para evitar desorden visual
        if len(self.profiles) >= 5:
            self.entry_new.configure(state="disabled",
                                     placeholder_text=self.parent_view._tr("msg_max_profiles_reached"))
            self.btn_add.configure(state="disabled")
        else:
            self.entry_new.configure(state="normal", placeholder_text=self.parent_view._tr("ph_new_profile"))
            self.btn_add.configure(state="normal")

        if len(self.profiles) < 5:
            try:
                self.entry_new.focus_set()
            except Exception:
                pass

    def _create_profile_item(self, pid):
        is_active = (pid == self.active_id)
        is_default = (pid == "default")

        display_name = self.parent_view._tr("lbl_default_name") if pid == "default" else pid
        suffix = self.parent_view._tr("lbl_active_suffix") if is_active else ""

        item_frame = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=self.colors["selected"] if is_active else "transparent",
            border_width=1,
            border_color=self.colors["text"] if is_active else "gray",
            corner_radius=8
        )
        item_frame.pack(fill="x", pady=4)

        lbl = ctk.CTkLabel(
            item_frame,
            text=f"  {display_name}{suffix}",
            font=("Segoe UI", 12, "bold" if is_active else "normal"),
            text_color="#FFFFFF" if is_active else self.colors["text"]
        )
        lbl.pack(side="left", padx=10, pady=8)

        item_frame.bind("<Button-1>", lambda e, p=pid: self._select_profile(p))
        lbl.bind("<Button-1>", lambda e, p=pid: self._select_profile(p))

        if not is_default:
            btn_del = ctk.CTkButton(
                item_frame,
                text="✕",
                width=24, height=24,
                fg_color="transparent",
                hover_color="#D03B3D",
                text_color="#FFFFFF" if is_active else self.colors["text"],
                command=lambda p=pid: self._delete_profile(p)
            )
            btn_del.pack(side="right", padx=10)

    def _add_profile(self):
        name = self.entry_new.get().strip()
        if not name: return
        pid = name.lower().replace(" ", "_")

        if pid in self.profiles:
            self.parent_view.show_message("error_title", "msg_profile_exists")
            return

        if len(self.profiles) >= 5: return

        self.profiles[pid] = "NEW"
        self.entry_new.delete(0, "end")

        if self.on_save_callback:
            self.on_save_callback(self.profiles)

        self._redraw_list()

    def _delete_profile(self, pid):
        if pid == "default": return
        if ConfirmDialog.ask(self.parent_view,
                             self.parent_view._tr("confirm_del_title"),
                             self.parent_view._tr("confirm_del_profile", pid)):
            del self.profiles[pid]
            if pid == self.active_id:
                self.active_id = "default"

            if self.on_save_callback:
                self.on_save_callback(self.profiles)

            self._redraw_list()

    def _select_profile(self, pid):
        if pid != self.active_id:
            self.active_id = pid
            self._redraw_list()
            self._on_ok()

    def _on_ok(self, event=None):
        self.result = (self.active_id, self.profiles)
        self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, profiles_meta, active_id, on_save_callback=None):
        dialog = cls(parent, profiles_meta, active_id, on_save_callback)
        parent.wait_window(dialog)
        return dialog.result