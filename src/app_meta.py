from __future__ import annotations

import json
import os

APP_NAME_INTERNAL = "LectorcitoPro"
APP_DISPLAY_NAME = "Lectorcito Pro"
APP_VERSION = "9.3.0"
APP_AUTHOR = "Renzo Fernando Mosquera Daza"
APP_VENDOR_NAME = "APPS_RenzoFernando"
APP_COMPANY_NAME = "Renzo Fernando Mosquera Daza"
APP_PUBLISHER_NAME = APP_COMPANY_NAME
APP_PRODUCT_NAME = APP_DISPLAY_NAME
APP_FILE_DESCRIPTION = "Herramienta de escritorio profesional para auditoría de código, documentación técnica y consolidación de contextos para Inteligencia Artificial."
APP_TRADEMARK = APP_DISPLAY_NAME
APP_REPOSITORY_URL = "https://github.com/RenzoFernando/LectorcitoPro.git"
APP_REPOSITORY_WEB_URL = APP_REPOSITORY_URL[:-4] if APP_REPOSITORY_URL.endswith(".git") else APP_REPOSITORY_URL
APP_WEBSITE_URL = "https://renzofernando.github.io/LectorcitoPro/"
APP_MANUAL_TITLE = "Manual de Usuario"
APP_EXECUTABLE_NAME = f"{APP_NAME_INTERNAL}.exe"
APP_INSTALLER_NAME = f"{APP_NAME_INTERNAL}-Setup.exe"
APP_INSTALLER_BASENAME = os.path.splitext(APP_INSTALLER_NAME)[0]
APP_PORTABLE_ARTIFACT_NAME = f"{APP_NAME_INTERNAL}-Portable.exe"
APP_RELEASE_BASENAME = f"{APP_NAME_INTERNAL}-{APP_VERSION}"
APP_RESOURCES_DIR_NAME = "resources"
APP_OUTPUT_DIR_NAME = "downloads"
APP_CERT_DIR_NAME = "certificate_resources"
APP_LICENSE_FILE_NAME = "LICENSE"
APP_LICENSE_RELATIVE_PATH = APP_LICENSE_FILE_NAME
APP_ICON_ICO_RELATIVE_PATH = os.path.join(APP_RESOURCES_DIR_NAME, "branding", "lector.ico")
APP_WEB_META_RELATIVE_PATH = os.path.join(APP_RESOURCES_DIR_NAME, "js", "app_meta.js")
APP_PUBLISHER_URL = APP_WEBSITE_URL
APP_SUPPORT_URL = APP_REPOSITORY_WEB_URL
APP_UPDATES_URL = f"{APP_REPOSITORY_WEB_URL}/releases/latest"
APP_SIGNING_TIMESTAMP_URL = "http://timestamp.digicert.com"
APP_INSTALL_MARKER_FILE = ".lectorcito_installed"


def get_current_year() -> int:
    from datetime import datetime
    return datetime.now().year


def get_project_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def get_installer_download_url() -> str:
    return f"{APP_REPOSITORY_WEB_URL}/releases/latest/download/{APP_INSTALLER_NAME}"


def get_portable_download_url() -> str:
    return f"{APP_REPOSITORY_WEB_URL}/releases/latest/download/{APP_PORTABLE_ARTIFACT_NAME}"


def get_release_download_url() -> str:
    return get_installer_download_url()


def get_document_title() -> str:
    return f"{APP_MANUAL_TITLE} - {APP_DISPLAY_NAME}"


def get_copyright_text() -> str:
    return f"© {get_current_year()} {APP_AUTHOR}. Todos los derechos reservados."


def get_legal_copyright_text() -> str:
    return f"Copyright {get_current_year()} - {APP_AUTHOR} - All Rights Reserved."


def get_windows_version(value: str | None = None) -> str:
    raw_value = str(value or APP_VERSION).strip()
    raw_parts = [part.strip() for part in raw_value.split(".")]
    normalized_parts = []

    for part in raw_parts:
        if not part:
            continue
        digits_only = "".join(ch for ch in part if ch.isdigit())
        normalized_parts.append(digits_only or "0")
        if len(normalized_parts) == 4:
            break

    while len(normalized_parts) < 4:
        normalized_parts.append("0")

    return ".".join(normalized_parts)


APP_FILE_VERSION = get_windows_version(APP_VERSION)
APP_PRODUCT_VERSION = get_windows_version(APP_VERSION)
APP_LEGAL_COPYRIGHT = get_legal_copyright_text()
APP_SIGNATURE_FRIENDLY_NAME = f"{APP_DISPLAY_NAME} Code Signing"


def get_web_meta_payload() -> dict:
    return {
        "nameInternal": APP_NAME_INTERNAL,
        "displayName": APP_DISPLAY_NAME,
        "productName": APP_PRODUCT_NAME,
        "version": APP_VERSION,
        "fileVersion": APP_FILE_VERSION,
        "productVersion": APP_PRODUCT_VERSION,
        "author": APP_AUTHOR,
        "companyName": APP_COMPANY_NAME,
        "publisherName": APP_PUBLISHER_NAME,
        "fileDescription": APP_FILE_DESCRIPTION,
        "repositoryUrl": APP_REPOSITORY_WEB_URL,
        "websiteUrl": APP_WEBSITE_URL,
        "manualTitle": APP_MANUAL_TITLE,
        "documentTitle": get_document_title(),
        "releaseUrl": APP_UPDATES_URL,
        "downloadUrl": get_release_download_url(),
        "installerDownloadUrl": get_installer_download_url(),
        "portableDownloadUrl": get_portable_download_url(),
        "executableName": APP_EXECUTABLE_NAME,
        "installerName": APP_INSTALLER_NAME,
        "portableArtifactName": APP_PORTABLE_ARTIFACT_NAME,
        "releaseBasename": APP_RELEASE_BASENAME,
        "currentYear": get_current_year(),
        "copyrightText": get_copyright_text(),
        "legalCopyright": APP_LEGAL_COPYRIGHT,
        "trademark": APP_TRADEMARK
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
