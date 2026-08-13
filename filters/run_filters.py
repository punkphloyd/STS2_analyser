from data_models.run_metadata import RunMetadata
from filters.filters import RunFilter


def apply_filters(
    runs: list[RunMetadata],
    filters: RunFilter,
) -> list[RunMetadata]:
    """
    Return all runs matching the supplied filter.
    """

    filtered_runs = runs

    # Character filter
    if filters.characters is not None:
        filtered_runs = [
            run
            for run in filtered_runs
            if run.character in filters.characters
        ]

    # Ascension filter
    filtered_runs = [
        run
        for run in filtered_runs
        if filters.min_ascension <= run.ascension <= filters.max_ascension
    ]

    # Victory filter
    if filters.victory is not None:
        filtered_runs = [
            run
            for run in filtered_runs
            if run.victory == filters.victory
        ]

    # Date filter
    if filters.start_date is not None:
        filtered_runs = [
            run
            for run in filtered_runs
            if run.start_time.date() >= filters.start_date
        ]

    if filters.end_date is not None:
        filtered_runs = [
            run
            for run in filtered_runs
            if run.start_time.date() <= filters.end_date
        ]

    # Game mode filters
    if filters.exclude_daily:
        filtered_runs = [
            run
            for run in filtered_runs
            if run.game_mode != "daily"
        ]

    if filters.exclude_custom:
        filtered_runs = [
            run
            for run in filtered_runs
            if run.game_mode != "custom"
        ]

    # Game version filter
    if filters.game_version is not None:
        filtered_runs = [
            run
            for run in filtered_runs
            if run.game_version == filters.game_version
        ]

    return filtered_runs