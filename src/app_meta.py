from __future__ import annotations

import json
import os

APP_NAME_INTERNAL = "LectorcitoPro"
APP_DISPLAY_NAME = "Lectorcito Pro"
APP_VERSION = "8.0.4"
APP_AUTHOR = "Renzo Fernando Mosquera Daza"
APP_VENDOR_NAME = "APPS_RenzoFernando"
APP_REPOSITORY_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"
APP_REPOSITORY_WEB_URL = APP_REPOSITORY_URL[:-4] if APP_REPOSITORY_URL.endswith(".git") else APP_REPOSITORY_URL
APP_WEBSITE_URL = "https://renzofernando.github.io/LectorcitoPro/"
APP_MANUAL_TITLE = "Manual de Usuario"
APP_EXECUTABLE_NAME = f"{APP_NAME_INTERNAL}.exe"
APP_RESOURCES_DIR_NAME = "resources"
APP_OUTPUT_DIR_NAME = "downloads"
APP_CERT_DIR_NAME = "certificate_resources"
APP_ICON_ICO_RELATIVE_PATH = os.path.join(APP_RESOURCES_DIR_NAME, "branding", "lector.ico")
APP_WEB_META_RELATIVE_PATH = os.path.join(APP_RESOURCES_DIR_NAME, "js", "app_meta.js")

def get_current_year() -> int:
    from datetime import datetime
    return datetime.now().year


def get_project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_release_download_url() -> str:
    return f"{APP_REPOSITORY_WEB_URL}/releases/latest/download/{APP_EXECUTABLE_NAME}"


def get_document_title() -> str:
    return f"{APP_MANUAL_TITLE} - {APP_DISPLAY_NAME}"


def get_copyright_text() -> str:
    return f"© {get_current_year()} {APP_AUTHOR}. Todos los derechos reservados."


def get_web_meta_payload() -> dict:
    return {
        "nameInternal": APP_NAME_INTERNAL,
        "displayName": APP_DISPLAY_NAME,
        "version": APP_VERSION,
        "author": APP_AUTHOR,
        "repositoryUrl": APP_REPOSITORY_WEB_URL,
        "websiteUrl": APP_WEBSITE_URL,
        "manualTitle": APP_MANUAL_TITLE,
        "documentTitle": get_document_title(),
        "downloadUrl": get_release_download_url(),
        "executableName": APP_EXECUTABLE_NAME,
        "currentYear": get_current_year(),
        "copyrightText": get_copyright_text()
    }


def build_web_meta_js() -> str:
    return "window.APP_META = " + json.dumps(get_web_meta_payload(), ensure_ascii=False, indent=4) + ";\n"


def sync_web_meta_file() -> str | None:
    project_root = get_project_root()
    output_path = os.path.join(project_root, APP_WEB_META_RELATIVE_PATH)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    content = build_web_meta_js()

    try:
        with open(output_path, "r", encoding="utf-8") as existing_file:
            if existing_file.read() == content:
                return output_path
    except FileNotFoundError:
        pass

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(content)

    return output_path


try:
    sync_web_meta_file()
except Exception:
    pass