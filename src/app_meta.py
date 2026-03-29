APP_NAME_INTERNAL = "LectorcitoPro"
APP_DISPLAY_NAME = "Lectorcito Pro"
APP_VERSION = "8.0.1"
APP_AUTHOR = "Renzo Fernando Mosquera Daza"
APP_VENDOR_NAME = "APPS_RenzoFernando"
APP_REPOSITORY_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"
APP_WEBSITE_URL = "https://renzofernando.github.io/LectorcitoPro/"
APP_EXECUTABLE_NAME = f"{APP_NAME_INTERNAL}.exe"

def get_current_year() -> int:
    from datetime import datetime
    return datetime.now().year
