from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class RunFilter:
    run_directory: Path | None = None

    date_mode: str = "all"

    start_date: datetime | None = None
    end_date: datetime | None = None

    characters: list[str] | None = None

    min_ascension: int = 0
    max_ascension: int = 10

    victory: bool | None = None