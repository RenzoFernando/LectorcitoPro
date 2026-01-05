import os
import threading


def _get_active_tags(config: dict, key: str) -> set:
    tag_list = config.get(key, [])
    return {tag["nombre"] for tag in tag_list if tag.get("estado") == "activo"}


def _build_tree_recursive(root_path: str, prefix: str, config: dict, filtered: bool) -> str:
    folders_to_exclude = _get_active_tags(config, "etiquetas_carpetas_excluidas") if filtered else set()
    files_to_exclude = _get_active_tags(config, "etiquetas_archivos_excluidos") if filtered else set()

    try:
        items = sorted(os.listdir(root_path))
    except Exception:
        return ""

    items = [x for x in items if x not in folders_to_exclude and x not in files_to_exclude]

    tree_str = ""
    for index, name in enumerate(items):
        path = os.path.join(root_path, name)
        connector = "└── " if index == len(items) - 1 else "├── "
        tree_str += f"{prefix}{connector}{name}\n"

        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            tree_str += _build_tree_recursive(path, prefix + extension, config, filtered)

    return tree_str


def generate_tree_report(
    source_folder: str,
    output_path: str,
    use_config: bool,
    config: dict,
    cancel_event: threading.Event = None,
) -> tuple[str, str | None]:
    try:
        if cancel_event and cancel_event.is_set():
            return "cancelled", None

        os.makedirs(output_path, exist_ok=True)
        project_name = os.path.basename(source_folder.rstrip("/\\"))

        version = 1
        while True:
            filename = f"{project_name}_tree_v{version}.txt"
            tree_path = os.path.join(output_path, filename)
            if not os.path.exists(tree_path):
                break
            version += 1

        tree_str = f"{project_name}\n"
        tree_str += _build_tree_recursive(source_folder, "", config, use_config)

        with open(tree_path, "w", encoding="utf-8") as f:
            f.write(tree_str)

        return "success", tree_path

    except Exception:
        return "error", None
