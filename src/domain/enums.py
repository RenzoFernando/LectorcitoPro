from enum import Enum


class Theme(str, Enum):
    LIGHT = "Light"
    DARK = "Dark"


class Language(str, Enum):
    ES = "es"
    EN = "en"


class ProcessStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"
    NO_FILES = "no_files"
