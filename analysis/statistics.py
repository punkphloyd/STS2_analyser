from collections import defaultdict

from data_models.run_metadata import RunMetadata


def calculate_win_rate(runs: list[RunMetadata]) -> float | None:
    """Return the win rate for the supplied runs."""

    if not runs:
        return None

    wins = sum(run.victory for run in runs)

    return wins / len(runs)


def calculate_win_rate_by_character(
    runs: list[RunMetadata],
) -> dict[str, float]:
    """Return win rate grouped by character."""

    character_runs: dict[str, list[RunMetadata]] = defaultdict(list)

    for run in runs:
        character_runs[run.character].append(run)

    return {
        character: calculate_win_rate(character_runs[character])
        for character in character_runs
    }


def calculate_win_rate_by_ascension(
    runs: list[RunMetadata],
) -> dict[int, float]:
    """Return win rate grouped by ascension."""

    ascension_runs: dict[int, list[RunMetadata]] = defaultdict(list)

    for run in runs:
        ascension_runs[run.ascension].append(run)

    return {
        ascension: calculate_win_rate(ascension_runs[ascension])
        for ascension in ascension_runs
    }


def calculate_win_rate_by_character_and_ascension(
    runs: list[RunMetadata],
) -> dict[tuple[str, int], float]:
    """Return win rate grouped by character and ascension."""

    grouped_runs: dict[
        tuple[str, int],
        list[RunMetadata]
    ] = defaultdict(list)

    for run in runs:
        key = (run.character, run.ascension)
        grouped_runs[key].append(run)

    return {
        key: calculate_win_rate(grouped_runs[key])
        for key in grouped_runs
    }