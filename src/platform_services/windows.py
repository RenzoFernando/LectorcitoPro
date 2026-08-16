from __future__ import annotations

import os
import subprocess

from platform_services.base import PlatformActionResult, PlatformService
from app_logging import log_warning


class WindowsPlatformService(PlatformService):
    platform_name = "windows"

    def __init__(self, win32_client=None):
        if win32_client is None:
            import win32com.client as win32_client
        self._win32_client = win32_client

    def get_runtime_executable(self) -> str:
        executable_path = super().get_runtime_executable()
        if not executable_path or not executable_path.lower().endswith(".exe"):
            return ""
        return executable_path

    def get_script_fallback_launcher(self) -> str:
        executable_path = super().get_script_fallback_launcher()
        if not executable_path or not executable_path.lower().endswith(".exe"):
            return ""
        return executable_path

    def is_valid_launcher(self, path) -> bool:
        clean_path = self.normalize_launcher_path(path)
        return bool(clean_path and os.path.isfile(clean_path) and clean_path.lower().endswith(".exe"))

    def supports_launcher_configuration(self) -> bool:
        return True

    def supported_shortcut_modes(self) -> tuple[str, ...]:
        return ("desktop", "start", "taskbar", "start_pin")

    def open_folder(self, path: str) -> bool:
        return self._open_windows_path(path)

    def open_file(self, path: str) -> bool:
        return self._open_windows_path(path)

    def _open_windows_path(self, path: str) -> bool:
        try:
            os.startfile(os.path.realpath(path))
            return True
        except Exception:
            return self._open_path_with_webbrowser(path)

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
            return PlatformActionResult(False, status="unsupported", error=f"Unsupported Windows shortcut mode: {mode}")
        if not self.is_valid_launcher(target_path):
            return PlatformActionResult(False, status="invalid_target", error="Invalid Windows executable path.")

        try:
            work_dir = os.path.dirname(target_path)
            shell = self._win32_client.Dispatch("WScript.Shell")
            link_path = ""

            if mode == "desktop":
                desktop_dir = shell.SpecialFolders("Desktop")
                link_path = os.path.join(desktop_dir, f"{app_name}.lnk")
                status = "desktop_created"
            elif mode == "start":
                programs_folder = self._get_programs_folder(shell)
                link_path = os.path.join(programs_folder, f"{app_name}.lnk")
                status = "start_created"
            else:
                programs_folder = self._get_programs_folder(shell)
                link_path = os.path.join(programs_folder, f"{app_name}.lnk")
                status = "taskbar_pinned" if mode == "taskbar" else "start_pinned"

            shortcut = shell.CreateShortCut(link_path)
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = work_dir
            shortcut.IconLocation = f"{target_path},0"
            shortcut.WindowStyle = 1
            shortcut.Description = description
            shortcut.Save()

            if mode in ("taskbar", "start_pin"):
                taskbar = mode == "taskbar"
                success_pin = self._try_programmatic_pin(target_path, taskbar=taskbar)
                if not success_pin:
                    success_pin = self._try_programmatic_pin(link_path, taskbar=taskbar)

                if not success_pin:
                    instruction_name = taskbar_instruction if taskbar else start_instruction
                    link_path = self._rename_shortcut_for_manual_action(link_path, instruction_name)
                    self._reveal_in_explorer(link_path)
                    status = "taskbar_manual" if taskbar else "start_manual"

            return PlatformActionResult(True, status=status, path=link_path)
        except Exception as exc:
            return PlatformActionResult(False, status="error", error=str(exc))

    def _get_programs_folder(self, shell) -> str:
        start_menu = shell.SpecialFolders("StartMenu")
        programs_folder = os.path.join(start_menu, "Programs")
        if not os.path.exists(programs_folder):
            try:
                os.makedirs(programs_folder)
            except Exception:
                programs_folder = start_menu
        return programs_folder

    def _try_programmatic_pin(self, link_path: str, taskbar: bool = True) -> bool:
        try:
            path = os.path.abspath(link_path)
            folder = os.path.dirname(path)
            filename = os.path.basename(path)

            shell = self._win32_client.Dispatch("Shell.Application")
            namespace = shell.NameSpace(folder)
            item = namespace.ParseName(filename)
            if not item:
                return False

            keywords = ["anclar a la barra de tareas", "pin to taskbar", "taskbar"] if taskbar else [
                "anclar a inicio", "pin to start", "start"
            ]

            for verb in item.Verbs():
                verb_name = verb.Name.lower()
                if any(keyword in verb_name for keyword in keywords):
                    if "desanclar" in verb_name or "unpin" in verb_name:
                        continue
                    verb.DoIt()
                    return True
            return False
        except Exception as exc:
            log_warning(str(exc), operation="pin_shortcut", file_path=link_path)
            return False

    def _rename_shortcut_for_manual_action(self, link_path: str, instruction_name: str) -> str:
        if not instruction_name:
            return link_path
        try:
            folder = os.path.dirname(link_path)
            safe_name = "".join(char for char in instruction_name if char.isalnum() or char in " _-")
            if not safe_name:
                return link_path
            new_path = os.path.join(folder, f"{safe_name}.lnk")
            if os.path.exists(new_path):
                os.remove(new_path)
            os.rename(link_path, new_path)
            return new_path
        except Exception as exc:
            log_warning(str(exc), operation="rename_shortcut", file_path=link_path)
            return link_path

    def _reveal_in_explorer(self, link_path: str):
        try:
            subprocess.run(f'explorer /select,"{link_path}"', shell=True)
        except Exception:
            pass
