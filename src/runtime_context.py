import os
import sys

def is_pyinstaller_frozen() -> bool:
    return bool(getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"))

def is_nuitka_compiled() -> bool:
    return globals().get("__compiled__") is not None

def is_frozen_runtime() -> bool:
    return bool(getattr(sys, "frozen", False) or is_nuitka_compiled())

def get_runtime_kind() -> str:
    if is_pyinstaller_frozen():
        return "pyinstaller"
    if is_nuitka_compiled():
        return "nuitka"
    return "development"

def get_runtime_executable_candidates() -> list[str]:
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(sys.executable)

    if is_nuitka_compiled():
        compiled_info = globals().get("__compiled__")
        original_argv0 = getattr(compiled_info, "original_argv0", "") if compiled_info is not None else ""
        if original_argv0:
            candidates.append(original_argv0)
        if sys.argv:
            candidates.append(sys.argv[0])
        candidates.append(sys.executable)

    result = []
    seen = set()
    for candidate in candidates:
        try:
            resolved = os.path.abspath(os.path.expanduser(str(candidate)))
        except Exception:
            continue
        key = os.path.normcase(resolved)
        if key not in seen:
            seen.add(key)
            result.append(resolved)
    return result

def get_resource_base_candidates(module_file: str) -> list[str]:
    candidates = []

    bundle_root = getattr(sys, "_MEIPASS", "")
    if bundle_root:
        candidates.append(os.path.abspath(bundle_root))

    module_dir = os.path.dirname(os.path.abspath(module_file))
    if os.path.basename(module_dir).lower() == "src":
        candidates.append(os.path.abspath(os.path.join(module_dir, "..")))
    candidates.append(module_dir)
    candidates.append(os.path.abspath(os.path.join(module_dir, "..")))

    result = []
    seen = set()
    for candidate in candidates:
        key = os.path.normcase(candidate)
        if key not in seen:
            seen.add(key)
            result.append(candidate)
    return result
