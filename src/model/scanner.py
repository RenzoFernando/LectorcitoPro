import os
from fnmatch import fnmatchcase
from file_rules import matches_file_rule
from model.report_model import ReportFile, ReportFolder, ReportProject
from app_logging import log_error, log_warning
from text_io import read_text_file


class ProjectScanner:
    def __init__(self, config: dict):
        self.config = config
        self.important_folders = self._get_active_tags("etiquetas_carpetas_importantes")
        self.text_extensions = self._get_active_tags("etiquetas_extensiones_incluidas")
        self.media_extensions = set(config.get("media_extensions", []))
        self.excluded_folders = self._get_active_tags("etiquetas_carpetas_excluidas")
        self.excluded_files = self._get_active_tags("etiquetas_archivos_excluidos")
        self.valid_extensions = self.text_extensions.union(self.media_extensions)

    def _get_active_tags(self, key: str) -> set:
        tag_list = self.config.get(key, [])
        return {tag["nombre"] for tag in tag_list if tag.get("estado") == "activo"}

    @staticmethod
    def _split_gitignore_line(raw_line: str) -> tuple[bool, bool, bool, str, bool] | None:
        line = raw_line.rstrip("\n\r").strip()
        if not line:
            return None
        if line.startswith("\\#") or line.startswith("\\!"):
            line = line[1:]
        elif line.startswith("#"):
            return None

        negate = line.startswith("!")
        if negate:
            line = line[1:]

        line = line.replace("\\", "/").strip()
        if not line:
            return None

        anchored = line.startswith("/")
        if anchored:
            line = line[1:]

        dir_only = line.endswith("/")
        if dir_only:
            line = line[:-1]

        line = line.strip("/")
        if not line:
            return None

        has_slash = "/" in line
        return negate, dir_only, anchored, line, has_slash

    def _load_gitignore_rules(self, source_folder: str) -> list[tuple[bool, bool, bool, str, bool]]:
        if not self.config.get("use_gitignore_exclusions", False):
            return []

        gitignore_path = os.path.join(source_folder, ".gitignore")
        if not os.path.isfile(gitignore_path):
            return []

        rules = []
        try:
            content = read_text_file(gitignore_path)
            for raw_line in content.splitlines(keepends=True):
                parsed = self._split_gitignore_line(raw_line)
                if parsed is not None:
                    rules.append(parsed)
        except OSError as error:
            log_warning(
                str(error),
                operation="load_gitignore",
                file_path=gitignore_path
            )
            return []

        return rules

    @staticmethod
    def _build_dir_candidates(rel_path: str) -> list[str]:
        normalized_path = rel_path.replace("\\", "/").strip("/")
        if not normalized_path:
            return []

        parts = [part for part in normalized_path.split("/") if part]
        candidates = []
        for index in range(len(parts)):
            candidates.append("/".join(parts[:index + 1]))
        return candidates

    @staticmethod
    def _match_gitignore_path(pattern: str, anchored: bool, has_slash: bool, candidate: str) -> bool:
        candidate = candidate.replace("\\", "/").strip("/")
        if not candidate:
            return False

        if not has_slash:
            return fnmatchcase(candidate.rsplit("/", 1)[-1], pattern)

        if anchored:
            return fnmatchcase(candidate, pattern)

        parts = [part for part in candidate.split("/") if part]
        for index in range(len(parts)):
            suffix = "/".join(parts[index:])
            if fnmatchcase(suffix, pattern):
                return True
        return False

    def _is_gitignore_excluded(
            self,
            rel_path: str,
            is_dir: bool,
            gitignore_rules: list[tuple[bool, bool, bool, str, bool]]
    ) -> bool:
        if not gitignore_rules:
            return False

        normalized_path = rel_path.replace("\\", "/").strip("/")
        if not normalized_path:
            return False

        dir_candidates = self._build_dir_candidates(
            normalized_path if is_dir else os.path.dirname(normalized_path)
        )
        path_candidates = list(dir_candidates)
        if is_dir:
            if normalized_path not in path_candidates:
                path_candidates.append(normalized_path)
        else:
            path_candidates.append(normalized_path)

        ignored = False
        for negate, dir_only, anchored, pattern, has_slash in gitignore_rules:
            candidates_to_check = dir_candidates if dir_only else path_candidates
            if any(
                    self._match_gitignore_path(pattern, anchored, has_slash, candidate)
                    for candidate in candidates_to_check
            ):
                ignored = not negate

        return ignored

    def scan_project(self, source_folder: str) -> ReportProject:
        source_folder = os.path.abspath(source_folder)
        project = ReportProject(
            name=os.path.basename(os.path.normpath(source_folder)),
            source_path=source_folder
        )
        gitignore_rules = self._load_gitignore_rules(source_folder)

        try:
            for root, dirs, filenames in os.walk(source_folder, topdown=True):
                relative_root = os.path.relpath(root, source_folder)
                relative_root = "" if relative_root == "." else relative_root
                dirs[:] = [
                    directory for directory in dirs
                    if directory not in self.excluded_folders
                    and not self._is_gitignore_excluded(
                        os.path.join(relative_root, directory),
                        True,
                        gitignore_rules
                    )
                ]
                filenames.sort()

                report_files = []
                for filename in filenames:
                    if matches_file_rule(filename, self.excluded_files):
                        continue
                    if self._is_gitignore_excluded(
                            os.path.join(relative_root, filename),
                            False,
                            gitignore_rules
                    ):
                        continue

                    is_text = matches_file_rule(filename, self.text_extensions)
                    is_media = matches_file_rule(filename, self.media_extensions)
                    if not is_text and not is_media:
                        continue

                    absolute_path = os.path.join(root, filename)
                    report_files.append(
                        ReportFile(
                            filename=filename,
                            absolute_path=absolute_path,
                            relative_path=os.path.relpath(absolute_path, source_folder),
                            kind="text" if is_text else "media"
                        )
                    )

                if report_files:
                    project.folders.append(
                        ReportFolder(
                            relative_path=relative_root,
                            important=os.path.basename(root) in self.important_folders,
                            files=report_files
                        )
                    )
        except OSError as error:
            log_error(
                "Error recorriendo el proyecto.",
                error,
                operation="scan_project",
                file_path=source_folder
            )
            return ReportProject(name=project.name, source_path=project.source_path)

        return project

    @staticmethod
    def read_file(report_file: ReportFile) -> ReportFile:
        if not report_file.is_text:
            return report_file

        report_file.content = None
        report_file.read_error = None
        try:
            report_file.content = read_text_file(report_file.absolute_path)
        except Exception as error:
            report_file.read_error = str(error)
            log_error(
                "Error leyendo archivo de proyecto.",
                error,
                operation="read_project_file",
                file_path=report_file.absolute_path
            )
        return report_file

    def build_tree_text(self, source_folder: str) -> str:
        source_folder = os.path.abspath(source_folder)
        gitignore_rules = self._load_gitignore_rules(source_folder)
        lines = [f"{os.path.basename(os.path.normpath(source_folder))}/"]
        self._build_tree_recursive(
            current_path=source_folder,
            prefix="",
            output_lines=lines,
            source_folder=source_folder,
            gitignore_rules=gitignore_rules
        )
        return "\n".join(lines) + "\n"

    def _build_tree_recursive(
            self,
            current_path: str,
            prefix: str,
            output_lines: list[str],
            source_folder: str,
            gitignore_rules: list[tuple[bool, bool, bool, str, bool]]
    ):
        try:
            elements = sorted(os.listdir(current_path))
        except OSError as error:
            log_warning(
                str(error),
                operation="build_tree",
                file_path=current_path
            )
            return

        filtered_elements = []
        for element in elements:
            element_path = os.path.join(current_path, element)
            relative_path = os.path.relpath(element_path, source_folder)
            if os.path.isdir(element_path):
                if (
                        element not in self.excluded_folders
                        and not self._is_gitignore_excluded(relative_path, True, gitignore_rules)
                ):
                    filtered_elements.append(element)
            else:
                if (
                        not matches_file_rule(element, self.excluded_files)
                        and not self._is_gitignore_excluded(relative_path, False, gitignore_rules)
                        and matches_file_rule(element, self.valid_extensions)
                ):
                    filtered_elements.append(element)

        pointers = ["├── "] * (len(filtered_elements) - 1) + ["└── "]

        for pointer, element in zip(pointers, filtered_elements):
            output_lines.append(prefix + pointer + element)
            element_path = os.path.join(current_path, element)
            if os.path.isdir(element_path):
                extension = "│   " if pointer == "├── " else "    "
                self._build_tree_recursive(
                    element_path,
                    prefix + extension,
                    output_lines,
                    source_folder,
                    gitignore_rules
                )
