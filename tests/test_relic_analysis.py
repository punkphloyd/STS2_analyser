from datetime import datetime
from pathlib import Path

from analysis.relic_analysis import (
    calculate_neow_relic_statistics,
    calculate_relic_statistics,
)
from data_models.relic_data import RelicAcquisition
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata
from parsers.run_parser import parse_run


EXAMPLE_RUNFILES = Path("example_runfiles")


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


def make_relic(
    relic: str,
    source: str = "elite",
) -> RelicAcquisition:

    return RelicAcquisition(
        relic=relic,
        source=source,
        act=1,
        floor=5,
        act_floor=5,
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


def test_relic_statistics():

    runs = [
        make_run(
            [],
            None,
            True,
        ),
        make_run(
            [],
            None,
            False,
        ),
    ]

    runs[0].relic_acquisitions = [
        make_relic("RELIC.A"),
        make_relic("RELIC.B"),
    ]

    runs[1].relic_acquisitions = [
        make_relic("RELIC.A"),
    ]

    result = calculate_relic_statistics(runs)

    assert result["RELIC.A"].runs_acquired == 2
    assert result["RELIC.A"].wins == 1
    assert result["RELIC.A"].win_rate == 1 / 2

    assert result["RELIC.B"].runs_acquired == 1
    assert result["RELIC.B"].wins == 1
    assert result["RELIC.B"].win_rate == 1.0


def test_relic_statistics_excludes_unacquired_relics():

    run = make_run(
        [],
        None,
        True,
    )

    run.relic_acquisitions = [
        make_relic("RELIC.A"),
    ]

    result = calculate_relic_statistics([run])

    assert "RELIC.A" in result
    assert "RELIC.B" not in result


def test_relic_statistics_wins_only_count_acquired_relics():

    winning_run = make_run(
        [],
        None,
        True,
    )

    winning_run.relic_acquisitions = [
        make_relic("RELIC.A"),
    ]

    losing_run = make_run(
        [],
        None,
        False,
    )

    losing_run.relic_acquisitions = [
        make_relic("RELIC.B"),
    ]

    result = calculate_relic_statistics(
        [
            winning_run,
            losing_run,
        ]
    )

    assert result["RELIC.A"].runs_acquired == 1
    assert result["RELIC.A"].wins == 1
    assert result["RELIC.A"].win_rate == 1.0

    assert result["RELIC.B"].runs_acquired == 1
    assert result["RELIC.B"].wins == 0
    assert result["RELIC.B"].win_rate == 0.0


def test_relic_statistics_empty():

    assert calculate_relic_statistics([]) == {}


def test_relic_statistics_from_example_runs():

    paths = [
        EXAMPLE_RUNFILES / "1785257698.run",
        EXAMPLE_RUNFILES / "1780176025.run",
    ]

    runs = [
        parse_run(path)
        for path in paths
    ]

    result = calculate_relic_statistics(runs)

    assert result