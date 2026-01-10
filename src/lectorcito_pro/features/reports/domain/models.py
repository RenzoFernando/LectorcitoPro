
from dataclasses import dataclass
from typing import Optional


@dataclass
class ReportResult:
    status: str
    path: Optional[str]
