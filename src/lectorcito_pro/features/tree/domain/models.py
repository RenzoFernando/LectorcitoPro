
from dataclasses import dataclass
from typing import Optional


@dataclass
class TreeResult:
    status: str
    path: Optional[str]
