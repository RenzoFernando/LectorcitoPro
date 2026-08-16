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
        return str(path).strip().replace('"', '') if path is not None else ""

    def normalize_compare_path(self, path) -> str:
        clean_path = self.normalize_launcher_path(path)
        if not clean_path:
            return ""
        try:
            return os.path.normcase(os.path.abspath(clean_path))
        except Exception:
            return os.path.normcase(clean_path)

    def get_runtime_executable(self) -> str:
        if not getattr(sys, "frozen", False):
            return ""
        executable_path = os.path.abspath(sys.executable)
        if not os.path.isfile(executable_path):
            return ""
        return executable_path

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
        if getattr(sys, "frozen", False):
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

    def get_capabilities(self) -> dict:
        return {
            "platform": self.platform_name,
            "supports_launcher_configuration": self.supports_launcher_configuration(),
            "shortcut_modes": self.supported_shortcut_modes()
        }

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
        start_instruction: str = ""
    ) -> PlatformActionResult:
        return PlatformActionResult(False, status="unsupported", error=f"Unsupported platform action: {mode}")
