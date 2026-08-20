from pathlib import Path
from datetime import datetime

from analysis.combat_analysis import (
    calculate_elite_boss_statistics,
)
from data_models.encounter_data import EncounterData
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata


def make_run(
    encounters: list[EncounterData],
) -> RunData:

    metadata = RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026,8,1),
        character="Ironclad",
        ascension=0,
        victory=False,
        game_version="test",
        game_mode="standard",
        multiplayer=False,
    )

    return RunData(
        metadata=metadata,
        floor_reached=1,
        encounters=encounters,
    )


def make_encounter(
    encounter: str,
    encounter_type: str,
    current_hp: int,
) -> EncounterData:

    return EncounterData(
        encounter=encounter,
        encounter_type=encounter_type,
        damage_taken=10,
        current_hp=current_hp,
        max_hp=80,
        hp_healed=0,
        max_hp_gained=0,
        max_hp_lost=0,
    )


def test_calculate_elite_boss_statistics():

    runs = [
        make_run(
            [
                make_encounter(
                    "ENCOUNTER.ENTOMANCER_ELITE",
                    "elite",
                    20,
                ),
                make_encounter(
                    "ENCOUNTER.SENTRY_ELITE",
                    "elite",
                    0,
                ),
            ]
        ),
        make_run(
            [
                make_encounter(
                    "ENCOUNTER.ENTOMANCER_ELITE",
                    "elite",
                    30,
                ),
                make_encounter(
                    "ENCOUNTER.SENTRY_ELITE",
                    "elite",
                    10,
                ),
            ]
        ),
    ]

    result = calculate_elite_boss_statistics(runs)

    assert result["ENCOUNTER.ENTOMANCER_ELITE"].faced == 2
    assert result["ENCOUNTER.ENTOMANCER_ELITE"].wins == 2
    assert (
        result["ENCOUNTER.ENTOMANCER_ELITE"].success_rate
        == 1.0
    )

    assert result["ENCOUNTER.SENTRY_ELITE"].faced == 2
    assert result["ENCOUNTER.SENTRY_ELITE"].wins == 1
    assert (
        result["ENCOUNTER.SENTRY_ELITE"].success_rate
        == 0.5
    )
    assert (
            result["ENCOUNTER.ENTOMANCER_ELITE"].encounter_type
            == "elite"
    )

    assert (
            result["ENCOUNTER.SENTRY_ELITE"].encounter_type
            == "elite"
    )


def test_statistics_count_encounters_not_runs():

    runs = [
        make_run(
            [
                make_encounter(
                    "ENCOUNTER.ENTOMANCER_ELITE",
                    "elite",
                    20,
                ),
                make_encounter(
                    "ENCOUNTER.ENTOMANCER_ELITE",
                    "elite",
                    30,
                ),
            ]
        ),
    ]

    result = calculate_elite_boss_statistics(runs)

    assert result["ENCOUNTER.ENTOMANCER_ELITE"].faced == 2
    assert result["ENCOUNTER.ENTOMANCER_ELITE"].wins == 2


def test_statistics_include_bosses():

    runs = [
        make_run(
            [
                make_encounter(
                    "ENCOUNTER.WATERFALL_GIANT_BOSS",
                    "boss",
                    20,
                ),
                make_encounter(
                    "ENCOUNTER.WATERFALL_GIANT_BOSS",
                    "boss",
                    0,
                ),
            ]
        ),
    ]

    result = calculate_elite_boss_statistics(runs)

    assert (
        result["ENCOUNTER.WATERFALL_GIANT_BOSS"].faced
        == 2
    )
    assert (
        result["ENCOUNTER.WATERFALL_GIANT_BOSS"].wins
        == 1
    )
    assert (
        result["ENCOUNTER.WATERFALL_GIANT_BOSS"].success_rate
        == 0.5
    )
    assert (
            result["ENCOUNTER.WATERFALL_GIANT_BOSS"].encounter_type
            == "boss"
    )


def test_statistics_empty_runs():

    result = calculate_elite_boss_statistics([])

    assert result == {}