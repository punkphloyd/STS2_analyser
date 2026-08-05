import json
from datetime import datetime
from pathlib import Path

from data_models.run_metadata import RunMetadata


CHARACTER_NAMES = {
    "CHARACTER.IRONCLAD": "Ironclad",
    "CHARACTER.SILENT": "Silent",
    "CHARACTER.DEFECT": "Defect",
    "CHARACTER.REGENT": "Regent",
    "CHARACTER.NECROBINDER": "Necrobinder",
}


def parse_metadata(path: Path) -> RunMetadata:
    """Parse a Slay the Spire 2 .run file into a RunMetadata object."""

    with path.open("r", encoding="utf-8") as file:
        data: dict = json.load(file)

    player = data["players"][0]

    return RunMetadata(
        file_path=path,
        start_time=datetime.fromtimestamp(data["start_time"]),
        character = CHARACTER_NAMES[player["character"]],
        ascension=data["ascension"],
        victory=data["win"]
    )