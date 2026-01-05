from tkinter import filedialog


def ask_directory(title: str = "") -> str:
    return filedialog.askdirectory(title=title) or ""
