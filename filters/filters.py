from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class RunFilter:

    date_mode: str = "all"

    start_date: datetime | None = None
    end_date: datetime | None = None

    characters: set[str] | None = None

    min_ascension: int = 0
    max_ascension: int = 10

    victory: bool | None = None