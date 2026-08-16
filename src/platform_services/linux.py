from __future__ import annotations

import ntpath
import os
import re
import shutil
import subprocess
import sys

from platform_services.base import PlatformActionResult, PlatformService


class LinuxPlatformService(PlatformService):
    platform_name = "linux"

    def get_user_config_dir(self, app_name: str, vendor_name: str) -> str:
        return os.path.join(self._xdg_home("XDG_CONFIG_HOME", ".config"), vendor_name, app_name)

    def get_user_data_dir(self, app_name: str, vendor_name: str) -> str:
        return os.path.join(self._xdg_home("XDG_DATA_HOME", os.path.join(".local", "share")), vendor_name, app_name)

    def get_user_state_dir(self, app_name: str, vendor_name: str) -> str:
        return os.path.join(self._xdg_home("XDG_STATE_HOME", os.path.join(".local", "state")), vendor_name, app_name)

    def _xdg_home(self, variable_name: str, fallback_relative: str) -> str:
        configured = str(os.environ.get(variable_name, "") or "").strip()
        if configured:
            return os.path.abspath(os.path.expanduser(configured))
        return os.path.abspath(os.path.join(os.path.expanduser("~"), fallback_relative))

    def is_path_compatible(self, path: str) -> bool:
        clean_path = str(path or "").strip().replace('"', '')
        if not clean_path:
            return False
        drive, _ = ntpath.splitdrive(clean_path)
        if drive:
            return False
        if clean_path.startswith("\\"):
            return False
        return True

    def get_installed_executable(self, marker_file: str) -> str:
        return self.get_runtime_executable()

    def get_script_fallback_launcher(self) -> str:
        if self.get_runtime_executable():
            return ""
        candidate = str(sys.argv[0] if sys.argv else "").strip()
        if not candidate:
            return ""
        candidate = os.path.abspath(os.path.expanduser(candidate))
        if os.path.isfile(candidate) and candidate.lower().endswith(".py"):
            return candidate
        return ""

    def is_valid_launcher(self, path) -> bool:
        clean_path = self.normalize_launcher_path(path)
        if not clean_path or not os.path.isfile(clean_path):
            return False
        if clean_path.lower().endswith(".py"):
            return True
        return os.access(clean_path, os.X_OK)

    def supported_shortcut_modes(self) -> tuple[str, ...]:
        return ("desktop", "start")

    def get_system_shortcuts_label_key(self) -> str:
        return "lbl_system_shortcuts_linux"

    def get_shortcut_label_keys(self) -> dict:
        return {
            "desktop": "btn_shortcut_desktop_linux",
            "start": "btn_shortcut_start_linux"
        }

    def open_folder(self, path: str) -> bool:
        return self._open_linux_path(path)

    def open_file(self, path: str) -> bool:
        return self._open_linux_path(path)

    def _open_linux_path(self, path: str) -> bool:
        resolved = os.path.realpath(os.path.expanduser(str(path or "")))
        if not resolved or not os.path.exists(resolved):
            return False

        commands = []
        gio = shutil.which("gio")
        if gio:
            commands.append([gio, "open", resolved])
        xdg_open = shutil.which("xdg-open")
        if xdg_open:
            commands.append([xdg_open, resolved])

        for command in commands:
            try:
                subprocess.Popen(
                    command,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
                return True
            except Exception:
                continue

        return self._open_path_with_webbrowser(resolved)

    def create_system_shortcut(
        self,
        mode: str,
        target_path: str,
        app_name: str,
        description: str,
        taskbar_instruction: str = "",
        start_instruction: str = "",
        display_name: str = "",
        desktop_id: str = "",
        icon_path: str = ""
    ) -> PlatformActionResult:
        if not self.supports_shortcut_mode(mode):
            return PlatformActionResult(False, status="unsupported", error=f"Unsupported Linux shortcut mode: {mode}")

        target_path = self.normalize_launcher_path(target_path)
        if not self.is_valid_launcher(target_path):
            return PlatformActionResult(False, status="invalid_target", error="Invalid Linux launcher path.")

        try:
            resolved_desktop_id = self._sanitize_desktop_id(desktop_id or app_name)
            installed_icon = self._install_application_icon(icon_path, resolved_desktop_id)
            desktop_content = self._build_desktop_entry(
                target_path=target_path,
                display_name=display_name or app_name,
                description=description,
                icon_path=installed_icon
            )

            if mode == "desktop":
                destination_dir = self._get_desktop_dir()
                os.makedirs(destination_dir, exist_ok=True)
                destination = os.path.join(destination_dir, f"{resolved_desktop_id}.desktop")
                status = "linux_desktop_created"
            else:
                destination_dir = os.path.join(self._xdg_home("XDG_DATA_HOME", os.path.join(".local", "share")), "applications")
                os.makedirs(destination_dir, exist_ok=True)
                destination = os.path.join(destination_dir, f"{resolved_desktop_id}.desktop")
                status = "linux_menu_created"

            self._write_desktop_entry(destination, desktop_content)

            if mode == "desktop":
                self._mark_desktop_entry_trusted(destination)
            else:
                self._refresh_application_database(destination_dir)

            return PlatformActionResult(True, status=status, path=destination)
        except Exception as exc:
            return PlatformActionResult(False, status="error", error=str(exc))

    def _sanitize_desktop_id(self, value: str) -> str:
        raw = str(value or "").strip()
        if not raw:
            raw = "lectorcitopro"
        if "." not in raw:
            raw = f"io.github.renzofernando.{raw}"
        parts = []
        for part in raw.split("."):
            clean = re.sub(r"[^A-Za-z0-9_-]", "", part)
            if not clean:
                continue
            if clean[0].isdigit():
                clean = f"app_{clean}"
            parts.append(clean)
        return ".".join(parts) or "io.github.renzofernando.lectorcitopro"

    def _get_desktop_dir(self) -> str:
        home_dir = os.path.abspath(os.path.expanduser("~"))
        xdg_user_dir = shutil.which("xdg-user-dir")
        if xdg_user_dir:
            try:
                result = subprocess.run(
                    [xdg_user_dir, "DESKTOP"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    check=False
                )
                candidate = str(result.stdout or "").strip()
                if candidate and os.path.abspath(os.path.expanduser(candidate)) != home_dir:
                    return os.path.abspath(os.path.expanduser(candidate))
            except Exception:
                pass

        config_file = os.path.join(self._xdg_home("XDG_CONFIG_HOME", ".config"), "user-dirs.dirs")
        try:
            with open(config_file, "r", encoding="utf-8") as infile:
                for line in infile:
                    if not line.startswith("XDG_DESKTOP_DIR="):
                        continue
                    value = line.split("=", 1)[1].strip().strip('"')
                    candidate = value.replace("$HOME", home_dir)
                    candidate = os.path.abspath(os.path.expanduser(candidate))
                    if candidate != home_dir:
                        return candidate
        except Exception:
            pass

        return os.path.join(home_dir, "Desktop")

    def _install_application_icon(self, icon_path: str, desktop_id: str) -> str:
        source = os.path.abspath(os.path.expanduser(str(icon_path or ""))) if icon_path else ""
        if not source or not os.path.isfile(source):
            return ""

        icon_dir = os.path.join(
            self._xdg_home("XDG_DATA_HOME", os.path.join(".local", "share")),
            "icons",
            "hicolor",
            "256x256",
            "apps"
        )
        os.makedirs(icon_dir, exist_ok=True)
        destination = os.path.join(icon_dir, f"{desktop_id}.png")
        shutil.copy2(source, destination)
        return destination

    def _build_desktop_entry(self, target_path: str, display_name: str, description: str, icon_path: str) -> str:
        if target_path.lower().endswith(".py"):
            exec_value = f"{self._desktop_exec_quote(sys.executable)} {self._desktop_exec_quote(target_path)}"
            try_exec = self._desktop_exec_quote(sys.executable)
            working_dir = os.path.dirname(target_path)
        else:
            exec_value = self._desktop_exec_quote(target_path)
            try_exec = self._desktop_exec_quote(target_path)
            working_dir = os.path.dirname(target_path)

        lines = [
            "[Desktop Entry]",
            "Type=Application",
            "Version=1.5",
            f"Name={self._desktop_string(display_name)}",
            f"Comment={self._desktop_string(description)}",
            f"Exec={exec_value}",
            f"TryExec={try_exec}",
            f"Path={self._desktop_string(working_dir)}",
            "Terminal=false",
            "Categories=Development;Utility;",
            "StartupNotify=true"
        ]
        if icon_path:
            lines.insert(7, f"Icon={self._desktop_string(icon_path)}")
        return "\n".join(lines) + "\n"

    def _desktop_exec_quote(self, value: str) -> str:
        escaped = str(value).replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`").replace("$", "\\$")
        return f'"{escaped}"'

    def _desktop_string(self, value: str) -> str:
        return str(value or "").replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")

    def _write_desktop_entry(self, destination: str, content: str):
        temp_path = f"{destination}.tmp"
        with open(temp_path, "w", encoding="utf-8", newline="\n") as outfile:
            outfile.write(content)
        os.chmod(temp_path, 0o755)
        os.replace(temp_path, destination)
        os.chmod(destination, 0o755)

    def _mark_desktop_entry_trusted(self, destination: str):
        gio = shutil.which("gio")
        if not gio:
            return
        try:
            subprocess.run(
                [gio, "set", destination, "metadata::trusted", "true"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception:
            pass

    def _refresh_application_database(self, applications_dir: str):
        update_desktop_database = shutil.which("update-desktop-database")
        if not update_desktop_database:
            return
        try:
            subprocess.run(
                [update_desktop_database, applications_dir],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
        except Exception:
            pass
