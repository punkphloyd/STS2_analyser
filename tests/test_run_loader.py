from datetime import datetime
from pathlib import Path

from data_models.run_metadata import RunMetadata
from services.run_loader import load_run_data


EXAMPLE_RUNFILES = Path("example_runfiles")


def test_load_run_data():

    metadata = RunMetadata(
        file_path=EXAMPLE_RUNFILES / "1785257698.run",
        start_time=datetime(2026, 8, 1),
        character="Ironclad",
        ascension=0,
        victory=True,
        game_version="v0.107.1",
        game_mode="standard",
        multiplayer=False,
    )

    result = load_run_data([metadata])

    assert len(result) == 1
    assert result[0].metadata.file_path == metadata.file_path
    assert result[0].neow_bonus_relic == "HEFTY_TABLET"