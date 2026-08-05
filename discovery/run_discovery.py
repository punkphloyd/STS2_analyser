from pathlib import Path


def discover_runs(directory: str) -> list[Path]:
    """
    Recursively find all .run files within the selected directory.
    """
    return sorted(Path(directory).rglob("*.run"))