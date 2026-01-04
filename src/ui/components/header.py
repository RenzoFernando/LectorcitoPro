import customtkinter as ctk


def create_header(parent, logo_image):
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.grid(row=0, column=0, sticky="ew", pady=(20, 15))
    lbl_title = ctk.CTkLabel(frame, text="", image=logo_image)
    lbl_title.pack()
    lbl_greet = ctk.CTkLabel(frame, font=("Segoe UI", 13))
    lbl_greet.pack()
    return frame, lbl_title, lbl_greet
