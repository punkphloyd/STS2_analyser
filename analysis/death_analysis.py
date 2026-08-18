from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import mean, median

from data_models.run_data import RunData


@dataclass(slots=True)
class FloorStatistics:
    runs: int
    average: float
    median: float
    highest: int
    lowest: int


def calculate_floor_statistics(
    runs: list[RunData],
) -> FloorStatistics | None:
    """Calculate floor statistics for the supplied runs."""

    if not runs:
        return None

    floors = [
        run.floor_reached
        for run in runs
    ]

    return FloorStatistics(
        runs=len(floors),
        average=mean(floors),
        median=median(floors),
        highest=max(floors),
        lowest=min(floors),
    )


def calculate_floor_statistics_by_character(
    runs: list[RunData],
) -> dict[str, FloorStatistics]:
    """Calculate floor statistics grouped by character."""

    character_runs: dict[
        str,
        list[RunData]
    ] = defaultdict(list)

    for run in runs:
        character_runs[run.metadata.character].append(run)

    return {
        character: calculate_floor_statistics(
            character_runs[character]
        )
        for character in character_runs
    }


def calculate_floor_statistics_by_ascension(
    runs: list[RunData],
) -> dict[int, FloorStatistics]:
    """Calculate floor statistics grouped by ascension."""

    ascension_runs: dict[
        int,
        list[RunData]
    ] = defaultdict(list)

    for run in runs:
        ascension_runs[run.metadata.ascension].append(run)

    return {
        ascension: calculate_floor_statistics(
            ascension_runs[ascension]
        )
        for ascension in ascension_runs
    }


def calculate_floor_statistics_by_character_and_ascension(
    runs: list[RunData],
) -> dict[tuple[str, int], FloorStatistics]:
    """Calculate floor statistics grouped by character and ascension."""

    grouped_runs: dict[
        tuple[str, int],
        list[RunData]
    ] = defaultdict(list)

    for run in runs:
        key = (
            run.metadata.character,
            run.metadata.ascension,
        )
        grouped_runs[key].append(run)

    return {
        key: calculate_floor_statistics(
            grouped_runs[key]
        )
        for key in grouped_runs
    }


@dataclass(slots=True)
class KilledByStatistics:
    killed_by: str
    deaths: int
    percentage: float


def calculate_top_killed_by(
    runs: list[RunData],
    limit: int = 10,
) -> list[KilledByStatistics]:
    """Return the most common causes of death."""

    killed_by_counts: Counter[str] = Counter()

    for run in runs:

        if run.death_data is None:
            continue

        killed_by = run.death_data.killed_by_encounter

        if killed_by is None or killed_by == "NONE.NONE":
            killed_by = run.death_data.killed_by_event

        if killed_by is None or killed_by == "NONE.NONE":
            killed_by = "UNKNOWN"

        killed_by_counts[killed_by] += 1

    total_deaths = sum(killed_by_counts.values())

    if total_deaths == 0:
        return []

    return [
        KilledByStatistics(
            killed_by=killed_by,
            deaths=deaths,
            percentage=deaths / total_deaths,
        )
        for killed_by, deaths in (
            killed_by_counts.most_common(limit)
        )
    ]