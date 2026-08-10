from pathlib import Path

from data_models.run_metadata import RunMetadata
from discovery.run_discovery import discover_runs
from parsers.metadata_parser import parse_metadata


def load_run_metadata(directory: str | Path) -> list[RunMetadata]:

    run_files = discover_runs(directory)

    metadata = [
        parse_metadata(run)
        for run in run_files
    ]

    metadata.sort(
        key=lambda run: run.start_time,
        reverse=True
    )

    return metadata