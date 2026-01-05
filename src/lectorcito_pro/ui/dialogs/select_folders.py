import customtkinter as ctk
from tkinter import filedialog

from .base import BaseDialog, COLORS


class MultiFolderSelectDialog(BaseDialog):
    def __init__(self, parent, initial_dir: str = ""):
        super().__init__(parent, parent._tr("dlg_multi_folder_title"))
        self.geometry("500x400")
        self.selected_paths = []
        self._parent = parent
        self._initial_dir = initial_dir or ""
        self.list_item_widgets = []
        self.currently_selected_index = -1

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

        self.scrollable_frame = ctk.CTkScrollableFrame(list_area_frame, label_text=self._parent._tr("dlg_multi_list_title"))
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")

        reorder_button_frame = ctk.CTkFrame(list_area_frame, fg_color="transparent")
        reorder_button_frame.grid(row=0, column=1, sticky="ns", padx=(10, 0))
        ctk.CTkButton(reorder_button_frame, text="▲", width=30, command=self._move_up).pack(pady=2)
        ctk.CTkButton(reorder_button_frame, text="▼", width=30, command=self._move_down).pack(pady=2)
        ctk.CTkButton(
            reorder_button_frame,
            text="✕",
            width=30,
            command=self._remove_selected_folder,
            fg_color=COLORS["button"]["red"],
            hover_color=COLORS["button_hover"]["red_h"],
        ).pack(pady=(10, 2))

        bottom_button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        bottom_button_frame.grid(row=2, column=0, sticky="e", pady=(15, 0))
        ctk.CTkButton(
            bottom_button_frame,
            text=self._parent._tr("btn_cancel"),
            command=self._on_cancel,
            fg_color=COLORS["button"]["red"],
            hover_color=COLORS["button_hover"]["red_h"],
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            bottom_button_frame,
            text=self._parent._tr("dlg_multi_process"),
            command=self._on_process,
            fg_color=COLORS["button"]["green"],
            hover_color=COLORS["button_hover"]["green_h"],
        ).pack(side="left")

        self._update_folder_list()

    def _update_folder_list(self):
        for widget in self.list_item_widgets:
            widget.destroy()
        self.list_item_widgets.clear()

        if not self.selected_paths:
            label = ctk.CTkLabel(self.scrollable_frame, text=self._parent._tr("dlg_multi_empty"), text_color="gray")
            label.pack(pady=10)
            self.list_item_widgets.append(label)
            return

        for i, path in enumerate(self.selected_paths):
            is_selected = i == self.currently_selected_index
            fg_color = COLORS["list_item"]["selected_bg"] if is_selected else COLORS["list_item"]["normal_bg"]

            item_frame = ctk.CTkFrame(self.scrollable_frame, fg_color=fg_color, corner_radius=6)
            item_frame.pack(fill="x", padx=5, pady=3)
            label = ctk.CTkLabel(item_frame, text=f"{i + 1}. {path}", anchor="w", compound="left", padx=10, font=("Segoe UI", 10))
            label.pack(fill="x")

            item_frame.bind("<Button-1>", lambda e, index=i: self._on_item_select(index))
            label.bind("<Button-1>", lambda e, index=i: self._on_item_select(index))
            self.list_item_widgets.append(item_frame)

    def _on_item_select(self, index):
        self.currently_selected_index = index
        self._update_folder_list()

    def _add_folder(self):
        path = filedialog.askdirectory(title=self._parent._tr("dlg_multi_add_title"), initialdir=self._initial_dir or None)
        if path and path not in self.selected_paths:
            self.selected_paths.append(path)
            self.currently_selected_index = len(self.selected_paths) - 1
            self._initial_dir = path
            self._update_folder_list()

    def _remove_selected_folder(self):
        if 0 <= self.currently_selected_index < len(self.selected_paths):
            self.selected_paths.pop(self.currently_selected_index)
            self.currently_selected_index = -1
            self._update_folder_list()

    def _move_up(self):
        if 0 < self.currently_selected_index < len(self.selected_paths):
            idx = self.currently_selected_index
            self.selected_paths[idx], self.selected_paths[idx - 1] = self.selected_paths[idx - 1], self.selected_paths[idx]
            self.currently_selected_index -= 1
            self._update_folder_list()

    def _move_down(self):
        if 0 <= self.currently_selected_index < len(self.selected_paths) - 1:
            idx = self.currently_selected_index
            self.selected_paths[idx], self.selected_paths[idx + 1] = self.selected_paths[idx + 1], self.selected_paths[idx]
            self.currently_selected_index += 1
            self._update_folder_list()

    def _on_process(self):
        self.result = self.selected_paths[:] if self.selected_paths else None
        self._close_with_fade_out()

    @classmethod
    def ask(cls, parent, initial_dir: str = ""):
        dialog = cls(parent, initial_dir=initial_dir)
        parent.wait_window(dialog)
        return dialog.result


SelectFoldersDialog = MultiFolderSelectDialog
