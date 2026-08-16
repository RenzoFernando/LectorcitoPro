from __future__ import annotations

from dataclasses import dataclass
import os
import sys
import webbrowser


@dataclass(frozen=True)
class PlatformActionResult:
    success: bool
    status: str = ""
    path: str = ""
    error: str = ""


class PlatformService:
    platform_name = "generic"

    def normalize_launcher_path(self, path) -> str:
        if path is None:
            return ""
        clean_path = str(path).strip().replace('"', '')
        if not clean_path:
            return ""
        return os.path.abspath(os.path.expandvars(os.path.expanduser(clean_path)))

    def normalize_compare_path(self, path) -> str:
        clean_path = self.normalize_launcher_path(path)
        if not clean_path:
            return ""
        try:
            return os.path.normcase(os.path.realpath(clean_path))
        except Exception:
            return os.path.normcase(clean_path)

    def _is_nuitka_compiled(self) -> bool:
        return globals().get("__compiled__") is not None

    def get_runtime_executable(self) -> str:
        candidates = []
        if getattr(sys, "frozen", False):
            candidates.append(sys.executable)
        if self._is_nuitka_compiled():
            compiled_info = globals().get("__compiled__")
            original_argv0 = getattr(compiled_info, "original_argv0", "") if compiled_info is not None else ""
            if original_argv0:
                candidates.append(original_argv0)
            if sys.argv:
                candidates.append(sys.argv[0])
            candidates.append(sys.executable)

        for candidate in candidates:
            try:
                resolved = os.path.abspath(os.path.expanduser(str(candidate)))
            except Exception:
                continue
            if os.path.isfile(resolved):
                return resolved
        return ""

    def get_install_marker_path(self, marker_file: str, executable_path: str = "") -> str:
        resolved_path = self.normalize_launcher_path(executable_path) or self.get_runtime_executable()
        if not resolved_path:
            return ""
        return os.path.join(os.path.dirname(resolved_path), marker_file)

    def is_installed_runtime(self, marker_file: str, executable_path: str = "") -> bool:
        marker_path = self.get_install_marker_path(marker_file, executable_path)
        return bool(marker_path and os.path.isfile(marker_path))

    def get_installed_executable(self, marker_file: str) -> str:
        runtime_path = self.get_runtime_executable()
        if runtime_path and self.is_installed_runtime(marker_file, runtime_path):
            return runtime_path
        return ""

    def get_script_fallback_launcher(self) -> str:
        if getattr(sys, "frozen", False) or self._is_nuitka_compiled():
            return ""
        executable_path = self.normalize_launcher_path(sys.executable)
        if not executable_path or not os.path.isfile(executable_path):
            return ""
        return executable_path

    def is_valid_launcher(self, path) -> bool:
        clean_path = self.normalize_launcher_path(path)
        return bool(clean_path and os.path.isfile(clean_path))

    def supports_launcher_configuration(self) -> bool:
        return False

    def supported_shortcut_modes(self) -> tuple[str, ...]:
        return ()

    def supports_shortcut_mode(self, mode: str) -> bool:
        return mode in self.supported_shortcut_modes()

    def get_system_shortcuts_label_key(self) -> str:
        return "lbl_system_shortcuts"

    def get_shortcut_label_keys(self) -> dict:
        return {}

    def get_capabilities(self) -> dict:
        return {
            "platform": self.platform_name,
            "supports_launcher_configuration": self.supports_launcher_configuration(),
            "shortcut_modes": self.supported_shortcut_modes(),
            "system_shortcuts_label_key": self.get_system_shortcuts_label_key(),
            "shortcut_label_keys": self.get_shortcut_label_keys()
        }

    def get_user_config_dir(self, app_name: str, vendor_name: str) -> str:
        from appdirs import user_config_dir
        return user_config_dir(app_name, vendor_name, roaming=True)

    def get_user_data_dir(self, app_name: str, vendor_name: str) -> str:
        return self.get_user_config_dir(app_name, vendor_name)

    def get_user_state_dir(self, app_name: str, vendor_name: str) -> str:
        return self.get_user_config_dir(app_name, vendor_name)

    def is_path_compatible(self, path: str) -> bool:
        clean_path = str(path or "").strip()
        return bool(clean_path)

    def resolve_readings_path(self, use_default_path: bool, custom_path: str, default_path: str) -> tuple[str, bool]:
        if use_default_path:
            return os.path.abspath(os.path.expanduser(default_path)), True
        clean_custom = str(custom_path or "").strip()
        if not clean_custom or not self.is_path_compatible(clean_custom):
            return os.path.abspath(os.path.expanduser(default_path)), True
        return os.path.abspath(os.path.expandvars(os.path.expanduser(clean_custom))), False

    def get_dialog_initial_directory(self, path: str) -> str:
        clean_path = str(path or "").strip()
        if not clean_path or not self.is_path_compatible(clean_path):
            return ""
        try:
            resolved = os.path.abspath(os.path.expandvars(os.path.expanduser(clean_path)))
            return resolved if os.path.isdir(resolved) else ""
        except Exception:
            return ""

    def open_folder(self, path: str) -> bool:
        return self._open_with_webbrowser(path)

    def open_file(self, path: str) -> bool:
        return self._open_with_webbrowser(path)

    def _open_with_webbrowser(self, path: str) -> bool:
        try:
            return bool(webbrowser.open(os.path.realpath(path)))
        except Exception:
            return False

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
        return PlatformActionResult(False, status="unsupported", error=f"Unsupported platform action: {mode}")
