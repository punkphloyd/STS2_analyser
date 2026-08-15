from datetime import datetime
from pathlib import Path

from data_models.run_metadata import RunMetadata
from filters.filters import RunFilter
from filters.run_filters import apply_filters


def make_run(
    game_mode: str = "standard",
    game_version: str = "v0.107.1",
    multiplayer: bool = False,
) -> RunMetadata:
    return RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026, 8, 1),
        character="Ironclad",
        ascension=0,
        victory=True,
        game_version=game_version,
        game_mode=game_mode,
        multiplayer=multiplayer,
    )

def test_daily_runs_included_by_default():

    runs = [
        make_run("standard", "v0.107.1"),
        make_run("daily", "v0.107.1"),
    ]

    filters = RunFilter()

    result = apply_filters(runs, filters)

    assert len(result) == 2

def test_exclude_daily_runs():

    runs = [
        make_run("standard", "v0.107.1"),
        make_run("daily", "v0.107.1"),
    ]

    filters = RunFilter(
        exclude_daily=True
    )

    result = apply_filters(runs, filters)

    assert len(result) == 1
    assert result[0].game_mode == "standard"


def test_exclude_custom_runs():

    runs = [
        make_run("standard", "v0.107.1"),
        make_run("custom", "v0.107.1"),
    ]

    filters = RunFilter(
        exclude_custom=True
    )

    result = apply_filters(runs, filters)

    assert len(result) == 1
    assert result[0].game_mode == "standard"


def test_exclude_daily_and_custom_runs():

    runs = [
        make_run("standard", "v0.107.1"),
        make_run("daily", "v0.107.1"),
        make_run("custom", "v0.107.1"),
    ]

    filters = RunFilter(
        exclude_daily=True,
        exclude_custom=True
    )

    result = apply_filters(runs, filters)

    assert len(result) == 1
    assert result[0].game_mode == "standard"

def test_game_version_filter():

    runs = [
        make_run("standard", "v0.107.1"),
        make_run("standard", "v0.107.0"),
        make_run("daily", "v0.107.1"),
    ]

    filters = RunFilter(
        game_version="v0.107.1"
    )

    result = apply_filters(runs, filters)

    assert len(result) == 2
    assert all(
        run.game_version == "v0.107.1"
        for run in result
    )

def test_game_version_and_mode_filters_combine():

    runs = [
        make_run("standard", "v0.107.1"),
        make_run("daily", "v0.107.1"),
        make_run("custom", "v0.107.1"),
        make_run("standard", "v0.107.0"),
    ]

    filters = RunFilter(
        exclude_daily=True,
        exclude_custom=True,
        game_version="v0.107.1"
    )

    result = apply_filters(runs, filters)

    assert len(result) == 1
    assert result[0].game_mode == "standard"
    assert result[0].game_version == "v0.107.1"

def test_exclude_multiplayer():
    runs = [
        make_run(multiplayer=False),
        make_run(multiplayer=True),
    ]

    filters = RunFilter(
        exclude_multiplayer=True
    )

    result = apply_filters(runs, filters)

    assert len(result) == 1
    assert result[0].multiplayer is False

def test_include_multiplayer():
    runs = [
        make_run(multiplayer=False),
        make_run(multiplayer=True),
    ]

    filters = RunFilter(
        exclude_multiplayer=False
    )

    result = apply_filters(runs, filters)

    assert len(result) == 2