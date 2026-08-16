from dataclasses import dataclass, field


@dataclass(slots=True)
class ReportFile:
    filename: str
    absolute_path: str
    relative_path: str
    kind: str
    content: str | None = None
    read_error: str | None = None

    @property
    def is_text(self) -> bool:
        return self.kind == "text"

    @property
    def is_media(self) -> bool:
        return self.kind == "media"


@dataclass(slots=True)
class ReportFolder:
    relative_path: str
    important: bool
    files: list[ReportFile] = field(default_factory=list)


@dataclass(slots=True)
class ReportProject:
    name: str
    source_path: str
    folders: list[ReportFolder] = field(default_factory=list)

    @property
    def file_count(self) -> int:
        return sum(len(folder.files) for folder in self.folders)
