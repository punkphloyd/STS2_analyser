from dataclasses import dataclass
from datetime import date


@dataclass(slots=True)
class RunFilter:


    start_date: date | None = None
    end_date: date | None = None

    characters: set[str] | None = None

    min_ascension: int = 0
    max_ascension: int = 10

    victory: bool | None = None

    exclude_daily: bool = False
    exclude_custom: bool = False
    game_version: str | None = None