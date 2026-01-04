import datetime
import os

# Información general de la aplicación
APP_NAME = "LectorcitoPro"
APP_AUTHOR = "APPS_RenzoFernando"
VERSION = "5.11.0"
AUTHOR = "Renzo Fernando Mosquera Daza"
YEAR = datetime.datetime.now().year
REPO_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"

# Rutas base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESOURCES_DIR = os.path.join(BASE_DIR, "recursos")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuración de apariencia
GIF_CHANGE_INTERVAL_MS = 1 * 60 * 1000
COLORS = {
    "light": {"bg": "#EBEBEB", "text": "#000000", "left_bar": "#1A1E22", "progress_bar": "#D9D9D9"},
    "dark": {"bg": "#1A1E22", "text": "#FFFFFF", "left_bar": "#EBEBEB", "progress_bar": "#333333"},
    "button": {"blue": "#3B8ED0", "green": "#3BD056", "red": "#D03B3D"},
    "button_hover": {"blue_h": "#3073A8", "green_h": "#2FA047", "red_h": "#A03031"},
    "sidebar_hover": {"light": "#3C3C3C", "dark": "#DCDCDC"},
    "progress_colors": {"start": "#3B8ED0", "mid": "#F9A825", "done": "#4CAF50"},
}

# Geometría estándar de la UI
BTN_W_MAIN, BTN_H_MAIN = 275, 31
BTN_W_ICON, BTN_H_ICON = 35, 40
SIDEBAR_WIDTH = 48
PROGRESS_W = 357
