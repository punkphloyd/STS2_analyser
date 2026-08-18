from datetime import datetime
from pathlib import Path
from parsers.run_parser import parse_run
from analysis.relic_analysis import calculate_neow_relic_statistics
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata


def make_run(
    offered_relics: list[str],
    selected_relic: str | None,
    victory: bool,
) -> RunData:

    metadata = RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026, 8, 1),
        character="Ironclad",
        ascension=0,
        victory=victory,
        game_version="v0.107.1",
        game_mode="standard",
        multiplayer=False,
    )

    return RunData(
        metadata=metadata,
        floor_reached=30,
        neow_bonus_relic=selected_relic,
        neow_relic_choices=offered_relics,
    )

def test_neow_relic_statistics():

    runs = [
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            "LARGE_CAPSULE",
            True,
        ),
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            "LARGE_CAPSULE",
            True,
        ),
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            "HEFTY_TABLET",
            False,
        ),
        make_run(
            ["HEFTY_TABLET", "NEOWS_BONES", "OTHER_RELIC"],
            "HEFTY_TABLET",
            True,
        ),
        make_run(
            ["HEFTY_TABLET", "NEOWS_BONES", "OTHER_RELIC"],
            "NEOWS_BONES",
            False,
        ),
    ]

    result = calculate_neow_relic_statistics(runs)

    assert result["LARGE_CAPSULE"].offered == 3
    assert result["LARGE_CAPSULE"].picks == 2
    assert result["LARGE_CAPSULE"].pick_rate == 2 / 3
    assert result["LARGE_CAPSULE"].wins == 2
    assert result["LARGE_CAPSULE"].win_rate == 1.0

    assert result["HEFTY_TABLET"].offered == 5
    assert result["HEFTY_TABLET"].picks == 2
    assert result["HEFTY_TABLET"].pick_rate == 2 / 5
    assert result["HEFTY_TABLET"].wins == 1
    assert result["HEFTY_TABLET"].win_rate == 1 / 2

    assert result["NEOWS_BONES"].offered == 5
    assert result["NEOWS_BONES"].picks == 1
    assert result["NEOWS_BONES"].pick_rate == 1 / 5
    assert result["NEOWS_BONES"].wins == 0
    assert result["NEOWS_BONES"].win_rate == 0.0

def test_neow_relic_statistics_ignores_runs_without_neow_relic():

    runs = [
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            "LARGE_CAPSULE",
            True,
        ),
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            None,
            True,
        ),
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            "HEFTY_TABLET",
            False,
        ),
    ]

    result = calculate_neow_relic_statistics(runs)

    assert result["LARGE_CAPSULE"].offered == 3
    assert result["LARGE_CAPSULE"].picks == 1
    assert result["LARGE_CAPSULE"].pick_rate == 1 / 3

    assert result["HEFTY_TABLET"].offered == 3
    assert result["HEFTY_TABLET"].picks == 1
    assert result["HEFTY_TABLET"].pick_rate == 1 / 3

def test_neow_relic_statistics_empty():

    assert calculate_neow_relic_statistics([]) == {}

def test_neow_relic_offered_but_never_picked():

    runs = [
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            "LARGE_CAPSULE",
            True,
        ),
        make_run(
            ["LARGE_CAPSULE", "HEFTY_TABLET", "NEOWS_BONES"],
            "LARGE_CAPSULE",
            False,
        ),
    ]

    result = calculate_neow_relic_statistics(runs)

    assert result["HEFTY_TABLET"].offered == 2
    assert result["HEFTY_TABLET"].picks == 0
    assert result["HEFTY_TABLET"].pick_rate == 0.0
    assert result["HEFTY_TABLET"].wins == 0
    assert result["HEFTY_TABLET"].win_rate is None


EXAMPLE_RUNFILES = Path("example_runfiles")


def test_neow_relic_analysis_from_example_runs():

    paths = [
        EXAMPLE_RUNFILES / "1785257698.run",
        EXAMPLE_RUNFILES / "1780176025.run",
    ]

    runs = [
        parse_run(path)
        for path in paths
    ]

    result = calculate_neow_relic_statistics(runs)

    assert result