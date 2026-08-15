from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(slots=True)
class RunMetadata:
    file_path: Path
    start_time: datetime
    character: str
    ascension: int
    victory: bool
    game_version: str
    game_mode: str
    multiplayer: bool = False