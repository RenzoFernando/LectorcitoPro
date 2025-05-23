import os, sys, json, shutil, threading, ctypes, datetime, webbrowser
from tkinter import PhotoImage, filedialog, messagebox, simpledialog, Canvas
import customtkinter as ctk
from PIL import Image
import tkinter as tk 

# ───────────────  Versión y metadatos  ────────────────
VERSION    = "3.7"
YEAR       = datetime.datetime.now().year
AUTHOR     = "Renzo Fernando Mosquera Daza"
COAUTHOR   = "ChatGPT Plus"
REPO_URL   = "https://github.com/RenzoFernando/LectorcitoPro.git"

INFO_ES = (
    f"Lectorcito Pro v{VERSION}\n"
    f"Desarrollado por: {AUTHOR} & {COAUTHOR}\n"
    f"Repositorio: {REPO_URL}\n"
    f"© {YEAR}"
)
INFO_EN = (
    f"Lectorcito Pro v{VERSION}\n"
    f"Developed by: {AUTHOR} & {COAUTHOR}\n"
    f"Repository: {REPO_URL}\n"
    f"© {YEAR}"
)


# ───────────────  Configuración persistente  ────────────────
CFG_FILE = os.path.join(os.path.expanduser("~"), ".lectorcito_cfg.json")
DEFAULT_CFG = {
    "lecturas_path": "",
    "EXTENSIONES_TEXTO": [".txt", ".py", ".html", ".java", ".md", ".css"],
    "CARPETAS_EXCLUIDAS": ["__pycache__", "venv", ".venv", "migrations", ".git"],
    "theme": "Light",
    "lang":  "es"
}

# ───────────────  Colores (mock‑up)  ────────────────
CLR_BG_LT,  CLR_BG_DK  = "#EBEBEB", "#1A1E22"
CLR_TXT_LT, CLR_TXT_DK = "#000000", "#FFFFFF"
CLR_BLUE = "#3B8ED0"
CLR_GREEN, CLR_GREEN_D = "#3BD056", "#2FA047"
CLR_RED,  CLR_RED_D    = "#D03B3D", "#A03031"
CLR_BAR_LT, CLR_BAR_DK = "#D9D9D9", "#333333"
LEFT_BG_LT, LEFT_BG_DK = "#1A1E22", "#EBEBEB"      # inverso para contraste
TOPBAR_CLR = "#1C2C59"

BTN_W_MAIN, BTN_H_MAIN     = 250, 30
BTN_W_ICON = BTN_H_ICON    = 35
BTN_ICON_RAD               = 10
PROGRESS_W                 = 357

# ───────────────  Utils de recurso / cfg  ────────────────
def res(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, "recursos", rel)

def load_cfg():
    if os.path.exists(CFG_FILE):
        try:
            data = json.load(open(CFG_FILE, encoding="utf‑8"))
            for k, v in DEFAULT_CFG.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return DEFAULT_CFG.copy()

def save_cfg(cfg):
    try:
        json.dump(cfg, open(CFG_FILE, "w", encoding="utf‑8"), indent=2)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar la configuración:\n{e}")

# ───────────────  App principal  ────────────────
class LectorcitoApp(ctk.CTk):

    # ───────  Traducciones  ───────
    TR = {
        "es": {
            "title": "LECTORCITO PRO",
            "welcome": "por favor seleccione una opción a realizar",
            "btn_choose_folder": "Elegir Carpeta a Leer",
            "btn_sel_lecturas":  "Seleccionar Ruta de Lecturas",
            "btn_open_lecturas": "Abrir archivo Lecturas",
            "btn_open_last":     "Abrir último archivo generado",
            "btn_del":           "Eliminar todas las Lecturas",
            "msg_done":          "Operación completada",
            "msg_select_read":   "Seleccione primero la carpeta a leer.",
            "msg_select_lect":   "Primero seleccione la ruta de Lecturas.",
            "msg_no_files":      "No se encontraron archivos válidos",
            "dlg_exts":          "Extensiones permitidas separadas por comas:",
            "dlg_excl":          "Carpetas excluidas separadas por comas:",
            "info": INFO_ES,
            "confirm_del":       "¿Eliminar todas las Lecturas?",
            "greet_m": "Buenos días", "greet_a": "Buenas tardes", "greet_n": "Buenas noches"
        },
        "en": {
            "title": "LECTORCITO PRO",
            "welcome": "please choose an option to perform",
            "btn_choose_folder": "Choose Folder to Read",
            "btn_sel_lecturas":  "Select Lecturas Path",
            "btn_open_lecturas": "Open Lecturas File",
            "btn_open_last":     "Open last generated file",
            "btn_del":           "Delete all Lecturas",
            "msg_done":          "Done",
            "msg_select_read":   "Select folder to read first.",
            "msg_select_lect":   "Select Lecturas path first.",
            "msg_no_files":      "No valid files found",
            "dlg_exts":          "Allowed extensions (comma separated):",
            "dlg_excl":          "Excluded folders (comma separated):",
            "info": INFO_EN,
            "confirm_del":       "Delete all Lecturas?",
            "greet_m": "Good morning", "greet_a": "Good afternoon", "greet_n": "Good evening"
        },
    }

    # ───────  INIT  ───────
    def __init__(self):
        super().__init__()
        if os.name == "nt":
            try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception: pass

        # Estado
        self.cfg = load_cfg()
        self.lang          = self.cfg.get("lang", "es")
        self.current_theme = self.cfg.get("theme", "Light")
        self.lecturas_path      = self.cfg["lecturas_path"]
        self.EXTENSIONES_TEXTO  = self.cfg["EXTENSIONES_TEXTO"]
        self.CARPETAS_EXCLUIDAS = self.cfg["CARPETAS_EXCLUIDAS"]

        # Ventana
        self.title("Lectorcito Pro")
        self.geometry("600x425"); self.resizable(False, False)
        ctk.set_appearance_mode(self.current_theme)
        ctk.set_default_color_theme("blue")

        # Recursos
        self._tk_icon = PhotoImage(file=res("lector.png"))
        try:
            self.iconphoto(True, self._tk_icon)
        except:
            pass

        self._load_icons()
        if os.path.exists(res("lector.ico")):
            try: self.iconbitmap(res("lector.ico"))
            except: pass
        #self._topbar()

        # Layout
        #NO TE NECEITO MAS -> self._topbar()
        self._sidebar_left()
        self._sidebar_right()
        self._header()
        self._main_buttons()
        self._progress()
        self._footer()
        self._apply_theme()
        self._apply_lang()

    # ───────────────  Recursos / iconos  ────────────────
    def _load_icons(self):
        # sol / luna
        self.icon_sun  = ctk.CTkImage(Image.open(res("sol.png")),  size=(24,24))
        self.icon_moon = ctk.CTkImage(Image.open(res("luna.png")), size=(24,24))
        # otros
        self.icons = {}
        for key in ["ver","nover","guardar","traducir","github","info"]:
            self.icons[key] = ctk.CTkImage(
                light_image=Image.open(res(f"{key}_claro.png")),
                dark_image =Image.open(res(f"{key}_oscuro.png")),
                size=(24,24))

    # ───────────────  Sidebar izquierda  ────────────────
    def _sidebar_left(self):
        self.side_left = ctk.CTkFrame(self, width=40, height=310, fg_color="#1a1e22", corner_radius=17)
        self.side_left.place(x=15, y=43)

        self.canvas_left = Canvas(self.side_left, width=25, height=270, highlightthickness=0, bg="#1a1e22")
        self.canvas_left.place(x=5, y=45)

        self.canvas_left.bind("<Configure>", self._paint_left)

    def _paint_left(self, *_):
        col = CLR_TXT_DK if self.current_theme=="Light" else CLR_TXT_LT
        self.canvas_left.delete("all")
        self.canvas_left.create_text(
            17.5, self.canvas_left.winfo_height()/2 + 4,
            text=f"Lectorcito Pro v{VERSION}", angle=90,
            font=("Segoe UI",10,"bold"), fill=col)


    # ───────────────  Sidebar derecha  ────────────────
    def _sidebar_right(self):
        self.side_right = ctk.CTkFrame(self, width=35, height=306, fg_color="transparent", corner_radius=17)
        self.side_right.place(x=600-15-60, y=40)

        btns = [
            ("ver",      self._cfg_exts),
            ("nover",    self._cfg_excl),
            ("guardar",  self._save_prefs),
            ("tema",     self._toggle_theme),
            ("traducir", self._toggle_lang),
            ("github",   lambda: webbrowser.open_new("https://github.com/RenzoFernando/LectorcitoPro.git")),
            ("info",     lambda: messagebox.showinfo("Info", self._tr("info"))),
        ]
        for k, cmd in btns:
            img = self.icon_moon if k=="tema" and self.current_theme=="Light" else \
                  self.icon_sun  if k=="tema" and self.current_theme=="Dark"  else self.icons[k]
            ctk.CTkButton(
                self.side_right, width=BTN_W_ICON, height=BTN_H_ICON, corner_radius=BTN_ICON_RAD,
                fg_color="#1A1E22", hover_color="#1A1E22",
                image=img, text="", command=cmd
            ).pack(pady=5, padx=10)

    # ───────────────  Encabezado  ────────────────
    def _header(self):
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.place(relx=0.5, y=20, anchor="n")
        self.lbl_title = ctk.CTkLabel(self.header, font=("Segoe UI",16,"bold"))
        self.lbl_title.pack()
        self.lbl_greet = ctk.CTkLabel(self.header, font=("Segoe UI",13,"bold"))
        self.lbl_greet.pack(pady=(0,0))

    # ───────────────  Botones principales  ────────────────
    def _main_buttons(self):
        self.main_fr = ctk.CTkFrame(self, fg_color="transparent")
        self.main_fr.place(relx=0.5, y=118, anchor="n") 

        self.btn_selpath = ctk.CTkButton(self.main_fr, width=BTN_W_MAIN, height=BTN_H_MAIN,
                                         corner_radius=10, font=("Segoe UI",11,"bold"),
                                         command=self._select_lecturas_path)
        self.btn_choose = ctk.CTkButton(self.main_fr, width=BTN_W_MAIN, height=BTN_H_MAIN,
                                        corner_radius=10, font=("Segoe UI",11,"bold"),
                                        command=self._select_folder_to_read)
        self.btn_openlect = ctk.CTkButton(self.main_fr, width=BTN_W_MAIN, height=BTN_H_MAIN,
                                          corner_radius=10, font=("Segoe UI",11,"bold"),
                                          command=self._open_lecturas_folder)
        self.btn_openlast = ctk.CTkButton(self.main_fr, width=BTN_W_MAIN, height=BTN_H_MAIN,
                                          corner_radius=10, font=("Segoe UI",11,"bold"),
                                          fg_color=CLR_GREEN, hover_color=CLR_GREEN_D,
                                          text_color="#FFFFFF", command=self._open_last_file)
        self.btn_delete   = ctk.CTkButton(self.main_fr, width=BTN_W_MAIN, height=BTN_H_MAIN,
                                          corner_radius=10, font=("Segoe UI",11,"bold"),
                                          fg_color=CLR_RED, hover_color=CLR_RED_D,
                                          text_color="#FFFFFF", command=self._delete_all)

        for idx, btn in enumerate([self.btn_selpath, self.btn_choose, 
                                   self.btn_openlect, self.btn_openlast,
                                   self.btn_delete]):
            btn.grid(row=idx, column=0, pady=4)

    # ───────────────  Barra de progreso  ────────────────
    def _progress(self):
        self.fr_prog = ctk.CTkFrame(self, fg_color="transparent")
        self.fr_prog.place(relx=0.5, y=335, anchor="n")   
        self.progress = ctk.CTkProgressBar(self.fr_prog, width=PROGRESS_W, corner_radius=10)
        self.progress.grid(row=0, column=0); self.progress.set(0)
        self.lbl_pct = ctk.CTkLabel(self.fr_prog, text="0%")
        self.lbl_pct.grid(row=1, column=0, pady=3)

    # ───────────────  Footer  ────────────────
    def _footer(self):
        foot = ctk.CTkFrame(self, height=30, corner_radius=0)
        foot.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")
        ctk.CTkLabel(foot, text="Copyright © - 2025 - Renzo Fernando - All Rights Reserved.",
                     font=("Segoe UI",9)).place(relx=0.5, rely=0.5, anchor="center")

    # ───────────────  Helpers de UI  ────────────────
    def _tr(self, k): return self.TR[self.lang][k]

    def _apply_theme(self):
        lt = self.current_theme=="Light"
        bg, fg = (CLR_BG_LT, CLR_TXT_LT) if lt else (CLR_BG_DK, CLR_TXT_DK)
        left_bg = LEFT_BG_LT if lt else LEFT_BG_DK
        self.configure(fg_color=bg)
        self.side_left.configure(fg_color=left_bg); self.canvas_left.configure(bg=left_bg)
        for fr in [self.side_right, self.header, self.main_fr, self.fr_prog]:
            fr.configure(fg_color="transparent")
        self.lbl_title.configure(text_color=fg)
        self.lbl_greet.configure(text_color=fg)
        self.lbl_pct.configure(text_color=fg)
        self.canvas_left.event_generate("<Configure>")
        # botones azules
        for btn in [self.btn_choose, self.btn_selpath, self.btn_openlect]:
            btn.configure(fg_color=CLR_BLUE, text_color="#FFFFFF")
        # icon buttons bg
        for b in self.side_right.winfo_children():
            b.configure(fg_color="#1A1E22" if lt else "#EBEBEB",
                        hover_color="#1A1E22" if lt else "#EBEBEB")
        # sol/luna icon
        self.side_right.winfo_children()[3].configure(
            image=self.icon_moon if lt else self.icon_sun)
        # progress bar
        self.progress.configure(progress_color=CLR_BLUE,
                                fg_color=CLR_BAR_LT if lt else CLR_BAR_DK)

    def _apply_lang(self):
        self.lbl_title.configure(text=self._tr("title"))
        self._update_greet()
        self.btn_choose.configure(text=self._tr("btn_choose_folder"))
        self.btn_selpath.configure(text=self._tr("btn_sel_lecturas"))
        self.btn_openlect.configure(text=self._tr("btn_open_lecturas"))
        self.btn_openlast.configure(text=self._tr("btn_open_last"))
        self.btn_delete.configure(text=self._tr("btn_del"))

    def _update_greet(self):
        h = datetime.datetime.now().hour
        greet = self._tr("greet_m") if h<12 else self._tr("greet_a") if h<18 else self._tr("greet_n")
        user = os.getlogin() if hasattr(os,"getlogin") else "####"
        self.lbl_greet.configure(text=f"{greet} {user},  {self._tr('welcome')}")

    # ───────────────  Acciones side‑right  ────────────────
    def _cfg_exts(self):
        # 1) Usa un Toplevel nativo en lugar de CTkToplevel
        dialog = tk.Toplevel(self)
        # Aplica el icono .ico de tu app
        try:
            dialog.iconbitmap(res("lector.ico"))
        except Exception:
            pass

        dialog.title("Extensiones")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()

        # 2) Mete tus widgets CTk dentro de un frame contenedor
        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        lbl = ctk.CTkLabel(container, text=self._tr("dlg_exts"), font=("Segoe UI", 12))
        lbl.pack(pady=(0,10))
        entry = ctk.CTkEntry(container, width=300)
        entry.insert(0, ",".join(self.EXTENSIONES_TEXTO))
        entry.pack(pady=(0,20))

        

        def save():
            s = entry.get()
            if s:
                self.EXTENSIONES_TEXTO = [x.strip() for x in s.split(",") if x.strip()]
                self.cfg["EXTENSIONES_TEXTO"] = self.EXTENSIONES_TEXTO
            dialog.destroy()

        btn_save = ctk.CTkButton(container, text="Guardar", command=save)
        btn_save.pack()

    def _cfg_excl(self):
        dialog = tk.Toplevel(self)
        try:
            dialog.iconbitmap(res("lector.ico"))
        except Exception:
            pass

        dialog.title("Carpetas Excluidas")
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()

        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        lbl = ctk.CTkLabel(container, text=self._tr("dlg_excl"), font=("Segoe UI", 12))
        lbl.pack(pady=(0,10))
        entry = ctk.CTkEntry(container, width=300)
        entry.insert(0, ",".join(self.CARPETAS_EXCLUIDAS))
        entry.pack(pady=(0,20))

        def save():
            s = entry.get()
            if s:
                self.CARPETAS_EXCLUIDAS = [x.strip() for x in s.split(",") if x.strip()]
                self.cfg["CARPETAS_EXCLUIDAS"] = self.CARPETAS_EXCLUIDAS
            dialog.destroy()

        btn_save = ctk.CTkButton(container, text="Guardar", command=save)
        btn_save.pack()

    def _save_prefs(self):
        self.cfg.update({
            "lecturas_path": self.lecturas_path,
            "EXTENSIONES_TEXTO": self.EXTENSIONES_TEXTO,
            "CARPETAS_EXCLUIDAS": self.CARPETAS_EXCLUIDAS,
            "theme": self.current_theme,
            "lang": self.lang
        })
        save_cfg(self.cfg)
        messagebox.showinfo("guardado/saved", self._tr("msg_done"))

    def _toggle_theme(self):
        self.current_theme = "Dark" if self.current_theme=="Light" else "Light"
        ctk.set_appearance_mode(self.current_theme)
        self._apply_theme()
        self._apply_lang()

    def _toggle_lang(self):
        self.lang = "en" if self.lang=="es" else "es"
        self._apply_lang()

    # ───────────────  Botones principales (lógica)  ────────────────
    def _select_lecturas_path(self):
        p = filedialog.askdirectory(title=self._tr("btn_sel_lecturas"))
        if p:
            self.lecturas_path = os.path.join(p, "Lecturas")
            os.makedirs(self.lecturas_path, exist_ok=True)

    def _select_folder_to_read(self):
        f = filedialog.askdirectory(title=self._tr("btn_choose_folder"))
        if f:
            self.folder_to_read = f
            if not self.lecturas_path:
                messagebox.showwarning("…", self._tr("msg_select_lect"))
            else:
                self._start_processing()

    def _open_lecturas_folder(self):
        if self.lecturas_path and os.path.isdir(self.lecturas_path):
            os.startfile(self.lecturas_path)
        else:
            messagebox.showwarning("…", self._tr("msg_select_lect"))

    def _open_last_file(self):
        if self.archivo_generado and os.path.isfile(self.archivo_generado):
            os.startfile(self.archivo_generado)
        else:
            messagebox.showwarning("…", self._tr("msg_no_files"))

    def _delete_all(self):
        if self.lecturas_path and os.path.isdir(self.lecturas_path):
            if messagebox.askyesno("…", self._tr("confirm_del")):
                shutil.rmtree(self.lecturas_path, ignore_errors=True)

    # ───────────────  Procesamiento  ────────────────
    def _start_processing(self):
        threading.Thread(target=self._process, daemon=True).start()

    def _process(self):
        self._set_state("disabled")
        self._progress_set(0)
        tot = self._count_files(self.folder_to_read)
        if not tot:
            messagebox.showinfo("…", self._tr("msg_no_files"))
            self._set_state("normal"); return

        base = os.path.basename(os.path.normpath(self.folder_to_read))
        idx = 1
        while True:
            self.archivo_generado = os.path.join(self.lecturas_path, f"{base}_v{idx}.txt")
            if not os.path.exists(self.archivo_generado): break
            idx += 1

        done = 0
        try:
            with open(self.archivo_generado,"w",encoding="utf‑8") as out:
                out.write(f"REPORTE DE ARCHIVOS EN: {self.folder_to_read}\n\n")
                for root, dirs, files in os.walk(self.folder_to_read):
                    dirs[:] = [d for d in dirs if d not in self.CARPETAS_EXCLUIDAS]
                    rel = os.path.relpath(root, self.folder_to_read)
                    out.write(f"Carpeta: {rel}\n")
                    for fn in sorted(files):
                        if os.path.splitext(fn)[1].lower() in self.EXTENSIONES_TEXTO:
                            fp = os.path.join(root, fn)
                            relp = os.path.relpath(fp, self.folder_to_read)
                            out.write(f"    Archivo: {relp}\n    -------- CONTENIDO --------\n")
                            try:
                                for l in open(fp,"r",encoding="utf‑8",errors="ignore"):
                                    out.write("    "+l)
                            except Exception as e:
                                out.write(f"    Error: {e}\n")
                            out.write("    -------- FIN --------\n\n")
                            done += 1
                            self._progress_set(done/tot*100)
            messagebox.showinfo("✔", self._tr("msg_done"))
            self._progress_set(0)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._progress_set(0)
        self._set_state("normal")

    def _count_files(self, folder):
        c = 0
        for root, dirs, files in os.walk(folder):
            dirs[:] = [d for d in dirs if d not in self.CARPETAS_EXCLUIDAS]
            c += sum(1 for f in files if os.path.splitext(f)[1].lower() in self.EXTENSIONES_TEXTO)
        return c

    def _progress_set(self, pct):
        pct = max(0, min(100, pct))
        self.progress.set(pct/100)
        self.lbl_pct.configure(text=f"{pct:.0f}%")
        self.update_idletasks()

    def _set_state(self, st):
        for btn in [self.btn_choose, self.btn_selpath, self.btn_openlect,
                    self.btn_openlast, self.btn_delete]:
            btn.configure(state=st)

# ───────────────  Run  ────────────────
if __name__ == "__main__":
    app = LectorcitoApp()
    app.mainloop()
