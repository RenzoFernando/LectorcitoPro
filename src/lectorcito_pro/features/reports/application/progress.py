
from dataclasses import dataclass


@dataclass
class ProgressUpdate:
    current: int
    total: int
    message: str = ""
