from datetime import datetime
from pathlib import Path

from analysis.death_analysis import (
    calculate_floor_statistics,
    calculate_floor_statistics_by_ascension,
    calculate_floor_statistics_by_character,
    calculate_floor_statistics_by_character_and_ascension,
    calculate_top_killed_by,
)
from data_models.death_data import DeathData
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata


def make_run(
    floor_reached: int,
    victory: bool,
    killed_by_encounter: str | None = None,
    killed_by_event: str | None = None,
    character: str = "Ironclad",
    ascension: int = 0,
) -> RunData:

    metadata = RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026, 8, 1),
        character=character,
        ascension=ascension,
        victory=victory,
        game_version="v0.107.1",
        game_mode="standard",
        multiplayer=False,
    )

    death_data = None

    if not victory:
        death_data = DeathData(
            killed_by_encounter=killed_by_encounter,
            killed_by_event=killed_by_event,
        )

    return RunData(
        metadata=metadata,
        floor_reached=floor_reached,
        death_data=death_data,
    )


def test_calculate_floor_statistics():

    runs = [
        make_run(20, False),
        make_run(30, False),
        make_run(40, True),
        make_run(50, True),
    ]

    result = calculate_floor_statistics(runs)

    assert result is not None
    assert result.runs == 4
    assert result.average == 35
    assert result.median == 35
    assert result.highest == 50
    assert result.lowest == 20


def test_calculate_floor_statistics_empty():

    result = calculate_floor_statistics([])

    assert result is None


def test_floor_statistics_include_victories():

    runs = [
        make_run(20, False),
        make_run(50, True),
    ]

    result = calculate_floor_statistics(runs)

    assert result is not None
    assert result.runs == 2
    assert result.average == 35


def test_calculate_top_killed_by():

    runs = [
        make_run(
            20,
            False,
            killed_by_encounter="ENCOUNTER.GREMLIN",
        ),
        make_run(
            25,
            False,
            killed_by_encounter="ENCOUNTER.GREMLIN",
        ),
        make_run(
            30,
            False,
            killed_by_encounter="ENCOUNTER.GREMLIN",
        ),
        make_run(
            35,
            False,
            killed_by_encounter="ENCOUNTER.SENTRY",
        ),
        make_run(
            40,
            False,
            killed_by_encounter="ENCOUNTER.SENTRY",
        ),
        make_run(
            50,
            True,
        ),
    ]

    result = calculate_top_killed_by(runs)

    assert len(result) == 2

    assert result[0].killed_by == "ENCOUNTER.GREMLIN"
    assert result[0].deaths == 3
    assert result[0].percentage == 0.6

    assert result[1].killed_by == "ENCOUNTER.SENTRY"
    assert result[1].deaths == 2
    assert result[1].percentage == 0.4


def test_calculate_top_killed_by_ignores_victories():

    runs = [
        make_run(50, True),
        make_run(
            30,
            False,
            killed_by_encounter="ENCOUNTER.GREMLIN",
        ),
    ]

    result = calculate_top_killed_by(runs)

    assert len(result) == 1
    assert result[0].killed_by == "ENCOUNTER.GREMLIN"
    assert result[0].deaths == 1
    assert result[0].percentage == 1.0


def test_calculate_top_killed_by_empty():

    result = calculate_top_killed_by([])

    assert result == []


def test_calculate_floor_statistics_by_character():

    runs = [
        make_run(20, False),
        make_run(30, False),
    ]

    runs[0].metadata.character = "Ironclad"
    runs[1].metadata.character = "Silent"

    result = calculate_floor_statistics_by_character(runs)

    assert set(result.keys()) == {
        "Ironclad",
        "Silent",
    }

    assert result["Ironclad"].runs == 1
    assert result["Ironclad"].average == 20

    assert result["Silent"].runs == 1
    assert result["Silent"].average == 30

def test_calculate_floor_statistics_by_character():

    runs = [
        make_run(20, False, character="Ironclad"),
        make_run(30, False, character="Silent"),
        make_run(40, True, character="Ironclad"),
    ]

    result = calculate_floor_statistics_by_character(runs)

    assert set(result.keys()) == {
        "Ironclad",
        "Silent",
    }

    assert result["Ironclad"].runs == 2
    assert result["Ironclad"].average == 30

    assert result["Silent"].runs == 1
    assert result["Silent"].average == 30

def test_calculate_floor_statistics_by_ascension():

    runs = [
        make_run(20, False, ascension=0),
        make_run(30, False, ascension=5),
        make_run(40, True, ascension=5),
    ]

    result = calculate_floor_statistics_by_ascension(runs)

    assert set(result.keys()) == {
        0,
        5,
    }

    assert result[0].runs == 1
    assert result[0].average == 20

    assert result[5].runs == 2
    assert result[5].average == 35


def test_calculate_floor_statistics_by_character_and_ascension():

    runs = [
        make_run(
            20,
            False,
            character="Ironclad",
            ascension=0,
        ),
        make_run(
            30,
            False,
            character="Ironclad",
            ascension=5,
        ),
        make_run(
            40,
            True,
            character="Silent",
            ascension=5,
        ),
        make_run(
            50,
            False,
            character="Silent",
            ascension=5,
        ),
    ]

    result = calculate_floor_statistics_by_character_and_ascension(
        runs
    )

    assert set(result.keys()) == {
        ("Ironclad", 0),
        ("Ironclad", 5),
        ("Silent", 5),
    }

    assert result[("Ironclad", 0)].average == 20

    assert result[("Ironclad", 5)].average == 30

    assert result[("Silent", 5)].runs == 2
    assert result[("Silent", 5)].average == 45


def test_calculate_top_killed_by_includes_event_deaths():

    runs = [
        make_run(
            20,
            False,
            killed_by_event="EVENT.CURSED_TOME",
        ),
        make_run(
            25,
            False,
            killed_by_event="EVENT.CURSED_TOME",
        ),
        make_run(
            30,
            False,
            killed_by_encounter="ENCOUNTER.GREMLIN",
        ),
    ]

    result = calculate_top_killed_by(runs)

    assert len(result) == 2

    assert result[0].killed_by == "EVENT.CURSED_TOME"
    assert result[0].deaths == 2
    assert result[0].percentage == 2 / 3

    assert result[1].killed_by == "ENCOUNTER.GREMLIN"
    assert result[1].deaths == 1
    assert result[1].percentage == 1 / 3


def test_calculate_top_killed_by_respects_limit():

    runs = [
        make_run(
            floor_reached=20 + index,
            victory=False,
            killed_by_encounter=f"ENCOUNTER.ENEMY_{index}",
        )
        for index in range(15)
    ]

    result = calculate_top_killed_by(
        runs,
        limit=10,
    )

    assert len(result) == 10