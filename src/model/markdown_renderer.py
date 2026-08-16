import hashlib
import os
import re
import unicodedata


_LANGUAGE_BY_EXTENSION = {
    ".asm": "asm",
    ".bat": "batch",
    ".c": "c",
    ".cc": "cpp",
    ".cfg": "ini",
    ".clj": "clojure",
    ".cljs": "clojure",
    ".cmake": "cmake",
    ".cmd": "batch",
    ".conf": "text",
    ".cpp": "cpp",
    ".cs": "csharp",
    ".css": "css",
    ".csv": "csv",
    ".cxx": "cpp",
    ".dart": "dart",
    ".dockerfile": "dockerfile",
    ".env": "dotenv",
    ".fs": "fsharp",
    ".fsx": "fsharp",
    ".go": "go",
    ".gradle": "groovy",
    ".graphql": "graphql",
    ".groovy": "groovy",
    ".h": "c",
    ".hpp": "cpp",
    ".htm": "html",
    ".html": "html",
    ".ini": "ini",
    ".java": "java",
    ".js": "javascript",
    ".json": "json",
    ".jsx": "jsx",
    ".kt": "kotlin",
    ".kts": "kotlin",
    ".less": "less",
    ".lua": "lua",
    ".md": "markdown",
    ".mjs": "javascript",
    ".php": "php",
    ".plist": "xml",
    ".properties": "properties",
    ".proto": "protobuf",
    ".ps1": "powershell",
    ".py": "python",
    ".r": "r",
    ".rb": "ruby",
    ".rs": "rust",
    ".sass": "sass",
    ".scss": "scss",
    ".sh": "bash",
    ".sql": "sql",
    ".svelte": "svelte",
    ".swift": "swift",
    ".toml": "toml",
    ".ts": "typescript",
    ".tsx": "tsx",
    ".txt": "text",
    ".vue": "vue",
    ".xml": "xml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".zsh": "bash",
}

_LANGUAGE_BY_FILENAME = {
    ".dockerignore": "dockerignore",
    ".editorconfig": "editorconfig",
    ".env": "dotenv",
    ".gitattributes": "gitattributes",
    ".gitignore": "gitignore",
    "cmakelists.txt": "cmake",
    "dockerfile": "dockerfile",
    "gemfile": "ruby",
    "makefile": "makefile",
    "pipfile": "toml",
    "procfile": "text",
    "requirements.txt": "text",
}


def _max_backtick_run(text: str) -> int:
    runs = re.findall(r"`+", text or "")
    return max((len(run) for run in runs), default=0)


def _fence_for(text: str) -> str:
    return "`" * max(3, _max_backtick_run(text) + 1)


def _inline_code(text: str) -> str:
    value = str(text)
    fence = "`" * max(1, _max_backtick_run(value) + 1)
    if value.startswith(" ") or value.endswith(" "):
        return f"{fence} {value} {fence}"
    return f"{fence}{value}{fence}"


def _language_for(filename: str) -> str:
    basename = os.path.basename(filename).lower()
    if basename in _LANGUAGE_BY_FILENAME:
        return _LANGUAGE_BY_FILENAME[basename]
    _, extension = os.path.splitext(basename)
    return _LANGUAGE_BY_EXTENSION.get(extension, "")


def _slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
    return slug or "raiz"


def _escape_link_text(value: str) -> str:
    return str(value).replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]")


class MarkdownReportRenderer:
    def __init__(self, outfile, labels: dict[str, str]):
        self.outfile = outfile
        self.labels = labels
        self._anchors = {}
        self._used_anchors = {}

    def _anchor(self, kind: str, path: str) -> str:
        key = (kind, path)
        if key in self._anchors:
            return self._anchors[key]

        base = f"{kind}-{_slugify(path)}"
        anchor = base
        previous = self._used_anchors.get(anchor)
        if previous is not None and previous != key:
            digest = hashlib.sha1(f"{kind}:{path}".encode("utf-8")).hexdigest()[:8]
            anchor = f"{base}-{digest}"
            while anchor in self._used_anchors and self._used_anchors[anchor] != key:
                digest = hashlib.sha1(f"{kind}:{path}:{anchor}".encode("utf-8")).hexdigest()[:8]
                anchor = f"{base}-{digest}"

        self._anchors[key] = anchor
        self._used_anchors[anchor] = key
        return anchor

    def _write_metadata(self, project_name: str, source_path: str):
        self.outfile.write(
            f"**{self.labels['project_label']}:** {_inline_code(project_name)}  \n"
            f"**{self.labels['path_label']}:** {_inline_code(source_path)}\n\n"
        )

    def write_header(self, title: str, project_name: str, source_path: str):
        self.outfile.write(f"# {title}\n\n")
        self._write_metadata(project_name, source_path)

    def write_toc(self, entries: list[dict]):
        self.outfile.write(f"## {self.labels['toc']}\n\n")
        for entry in entries:
            folder_path = entry["relative_root"] or self.labels["root"]
            folder_anchor = self._anchor(self.labels["folder_anchor_prefix"], folder_path)
            folder_text = entry["relative_root"] or self.labels["root"]
            important = f" — **{self.labels['important']}**" if entry.get("important") else ""
            self.outfile.write(
                f"- [{_escape_link_text(folder_text)}](#{folder_anchor}){important}\n"
            )
            for file_entry in entry["files"]:
                file_anchor = self._anchor(self.labels["file_anchor_prefix"], file_entry["relative_path"])
                self.outfile.write(
                    f"  - [{_escape_link_text(file_entry['filename'])}](#{file_anchor})\n"
                )
        self.outfile.write("\n")

    def write_folder(self, relative_root: str, important: bool):
        folder_path = relative_root or self.labels["root"]
        folder_anchor = self._anchor(self.labels["folder_anchor_prefix"], folder_path)
        folder_display = _inline_code(relative_root) if relative_root else self.labels["root"]
        important_text = f" — **{self.labels['important']}**" if important else ""
        self.outfile.write(
            f'<a id="{folder_anchor}"></a>\n'
            f"## {self.labels['folder_label']}: {folder_display}{important_text}\n\n"
        )

    def write_text_file(self, filename: str, relative_path: str, content: str):
        file_anchor = self._anchor(self.labels["file_anchor_prefix"], relative_path)
        filename_inline = _inline_code(filename)
        self.outfile.write(
            f'<a id="{file_anchor}"></a>\n'
            f"### {self.labels['file_label']}: {filename_inline}\n\n"
            f"**{self.labels['path_label']}:** {_inline_code(relative_path)}\n\n"
            f"**{self.labels['content_start']}: {filename_inline}**\n\n"
        )

        fence = _fence_for(content)
        language = _language_for(filename)
        self.outfile.write(f"{fence}{language}\n")
        self.outfile.write(content)
        if content and not content.endswith("\n"):
            self.outfile.write("\n")
        self.outfile.write(f"{fence}\n\n")
        self.outfile.write(
            f"**{self.labels['content_end']}: {filename_inline}**\n\n"
        )

    def write_read_error(self, filename: str, relative_path: str, error_text: str):
        file_anchor = self._anchor(self.labels["file_anchor_prefix"], relative_path)
        filename_inline = _inline_code(filename)
        self.outfile.write(
            f'<a id="{file_anchor}"></a>\n'
            f"### {self.labels['file_label']}: {filename_inline}\n\n"
            f"**{self.labels['path_label']}:** {_inline_code(relative_path)}\n\n"
            f"> {self.labels['read_error'].format(error_text)}\n\n"
        )

    def write_media_file(self, filename: str, relative_path: str):
        file_anchor = self._anchor(self.labels["file_anchor_prefix"], relative_path)
        self.outfile.write(
            f'<a id="{file_anchor}"></a>\n'
            f"### {self.labels['file_label']}: {_inline_code(filename)}\n\n"
            f"**{self.labels['path_label']}:** {_inline_code(relative_path)}\n\n"
            f"> {self.labels['media_notice']}\n\n"
        )

    def write_tree(self, title: str, project_name: str, source_path: str, tree_text: str):
        self.write_header(title, project_name, source_path)
        self.outfile.write(f"## {self.labels['tree_structure']}\n\n")
        fence = _fence_for(tree_text)
        self.outfile.write(f"{fence}text\n")
        self.outfile.write(tree_text)
        if tree_text and not tree_text.endswith("\n"):
            self.outfile.write("\n")
        self.outfile.write(f"{fence}\n")
