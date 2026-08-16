from __future__ import annotations

import os
import subprocess

from platform_services.base import PlatformService


class LinuxPlatformService(PlatformService):
    platform_name = "linux"

    def open_folder(self, path: str) -> bool:
        return self._open_linux_path(path)

    def open_file(self, path: str) -> bool:
        return self._open_linux_path(path)

    def _open_linux_path(self, path: str) -> bool:
        try:
            subprocess.Popen(
                ["xdg-open", os.path.realpath(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            return True
        except Exception:
            return self._open_with_webbrowser(path)
