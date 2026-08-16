from __future__ import annotations

import sys

from platform_services.base import PlatformService


_platform_service = None


def get_platform_service() -> PlatformService:
    global _platform_service
    if _platform_service is not None:
        return _platform_service

    if sys.platform.startswith("win"):
        from platform_services.windows import WindowsPlatformService
        _platform_service = WindowsPlatformService()
    elif sys.platform.startswith("linux"):
        from platform_services.linux import LinuxPlatformService
        _platform_service = LinuxPlatformService()
    else:
        _platform_service = PlatformService()

    return _platform_service
