import customtkinter as ctk


def create_progress_area(parent):
    progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
    progress_frame.grid(row=2, column=0, sticky="nsew", pady=(1, 1))
    progress_frame.grid_columnconfigure(0, weight=1)
    progress_frame.grid_rowconfigure(1, weight=1)
    progress_frame.grid_rowconfigure(3, weight=1)

    progress_content_wrapper = ctk.CTkFrame(progress_frame, fg_color="transparent")
    progress_content_wrapper.grid(row=0, column=0, sticky="nsew", rowspan=4)
    lbl_gif_animation = ctk.CTkLabel(progress_content_wrapper, text="")
    lbl_gif_animation.pack(expand=True)

    lbl_progress_status = ctk.CTkLabel(progress_frame, text="", font=("Segoe UI", 11, "bold"))
    lbl_percent = ctk.CTkLabel(progress_frame, text="", font=("Segoe UI", 11, "bold"))
    progress_bar = ctk.CTkProgressBar(progress_frame, height=10, corner_radius=8, mode="determinate")
    progress_bar.set(0)
    lbl_current_file = ctk.CTkLabel(progress_frame, text="", font=("Segoe UI", 9), anchor="w")
    btn_cancel = ctk.CTkButton(progress_frame, width=150, height=28)

    return {
        "frame": progress_frame,
        "content_wrapper": progress_content_wrapper,
        "gif": lbl_gif_animation,
        "status": lbl_progress_status,
        "percent": lbl_percent,
        "bar": progress_bar,
        "current_file": lbl_current_file,
        "cancel": btn_cancel,
    }
