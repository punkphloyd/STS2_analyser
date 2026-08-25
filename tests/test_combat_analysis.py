from pathlib import Path
from datetime import datetime

from analysis.combat_analysis import (
    calculate_elite_boss_statistics,
    calculate_encounter_statistics,
    encounter_won,
    filter_encounters,
)

from data_models.encounter_data import EncounterData
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata


def make_run(
    encounters: list[EncounterData],
) -> RunData:

    metadata = RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026, 8, 1),
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
        act=1,
        floor=2,
        act_floor=2,
        turns_taken=5,
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

    assert result["ENCOUNTER.ENTOMANCER_ELITE"].fights == 2
    assert result["ENCOUNTER.ENTOMANCER_ELITE"].wins == 2
    assert (
        result["ENCOUNTER.ENTOMANCER_ELITE"].win_rate
        == 1.0
    )

    assert result["ENCOUNTER.SENTRY_ELITE"].fights == 2
    assert result["ENCOUNTER.SENTRY_ELITE"].wins == 1
    assert (
        result["ENCOUNTER.SENTRY_ELITE"].win_rate
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

    assert result["ENCOUNTER.ENTOMANCER_ELITE"].fights == 2
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
        result["ENCOUNTER.WATERFALL_GIANT_BOSS"].fights
        == 2
    )

    assert (
        result["ENCOUNTER.WATERFALL_GIANT_BOSS"].wins
        == 1
    )

    assert (
        result["ENCOUNTER.WATERFALL_GIANT_BOSS"].win_rate
        == 0.5
    )

    assert (
        result["ENCOUNTER.WATERFALL_GIANT_BOSS"].encounter_type
        == "boss"
    )


def test_statistics_empty_runs():

    result = calculate_elite_boss_statistics([])

    assert result == {}


def test_filter_encounters_by_act():

    runs = [
        make_run(
            [
                make_encounter(
                    "ENCOUNTER.ENTOMANCER_ELITE",
                    "elite",
                    20,
                ),
            ]
        ),
    ]

    runs[0].encounters[0].act = 2

    assert len(
        filter_encounters(
            runs,
            act=2,
        )
    ) == 1

    assert len(
        filter_encounters(
            runs,
            act=1,
        )
    ) == 0


def test_filter_encounters_by_type():

    runs = [
        make_run(
            [
                make_encounter(
                    "ENCOUNTER.ENTOMANCER_ELITE",
                    "elite",
                    20,
                ),
                make_encounter(
                    "ENCOUNTER.SLUDGE_SPINNER_WEAK",
                    "monster",
                    20,
                ),
            ]
        ),
    ]

    result = filter_encounters(
        runs,
        encounter_type="elite",
    )

    assert len(result) == 1
    assert result[0].encounter == (
        "ENCOUNTER.ENTOMANCER_ELITE"
    )


def test_filter_encounters_by_specific_encounter():

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
                    20,
                ),
            ]
        ),
    ]

    result = filter_encounters(
        runs,
        encounter_name="ENCOUNTER.SENTRY_ELITE",
    )

    assert len(result) == 1
    assert result[0].encounter == (
        "ENCOUNTER.SENTRY_ELITE"
    )


def test_filter_encounters_combines_filters():

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
                    20,
                ),
                make_encounter(
                    "ENCOUNTER.WATERFALL_GIANT_BOSS",
                    "boss",
                    20,
                ),
            ]
        ),
    ]

    runs[0].encounters[0].act = 1
    runs[0].encounters[1].act = 2
    runs[0].encounters[2].act = 2

    result = filter_encounters(
        runs,
        act=2,
        encounter_type="elite",
        encounter_name="ENCOUNTER.SENTRY_ELITE",
    )

    assert len(result) == 1
    assert result[0].encounter == (
        "ENCOUNTER.SENTRY_ELITE"
    )
    assert result[0].act == 2
    assert result[0].encounter_type == "elite"


def test_calculate_encounter_statistics():

    runs = [
        make_run(
            [
                EncounterData(
                    encounter="ENCOUNTER.ENTOMANCER_ELITE",
                    encounter_type="elite",
                    act=1,
                    floor=10,
                    act_floor=10,
                    turns_taken=5,
                    damage_taken=20,
                    current_hp=60,
                    max_hp=80,
                    hp_healed=0,
                    max_hp_gained=0,
                    max_hp_lost=0,
                ),
                EncounterData(
                    encounter="ENCOUNTER.ENTOMANCER_ELITE",
                    encounter_type="elite",
                    act=1,
                    floor=15,
                    act_floor=15,
                    turns_taken=10,
                    damage_taken=40,
                    current_hp=40,
                    max_hp=80,
                    hp_healed=0,
                    max_hp_gained=0,
                    max_hp_lost=0,
                ),
                EncounterData(
                    encounter="ENCOUNTER.ENTOMANCER_ELITE",
                    encounter_type="elite",
                    act=1,
                    floor=17,
                    act_floor=17,
                    turns_taken=4,
                    damage_taken=10,
                    current_hp=0,
                    max_hp=80,
                    hp_healed=0,
                    max_hp_gained=0,
                    max_hp_lost=0,
                ),
            ]
        ),
    ]

    result = calculate_encounter_statistics(
        runs
    )

    statistics = result[
        "ENCOUNTER.ENTOMANCER_ELITE"
    ]

    assert statistics.encounter_type == "elite"
    assert statistics.fights == 3
    assert statistics.wins == 2
    assert statistics.win_rate == 2 / 3

    assert statistics.average_damage == 70 / 3
    assert statistics.median_damage == 20
    assert statistics.minimum_damage == 10
    assert statistics.maximum_damage == 40

    assert statistics.average_turns == 19 / 3
    assert statistics.minimum_turns == 4
    assert statistics.maximum_turns == 10

    assert statistics.average_damage_per_turn == (
        (
            20 / 5
            + 40 / 10
            + 10 / 4
        ) / 3
    )


def test_calculate_encounter_statistics_empty_runs():

    result = calculate_encounter_statistics([])

    assert result == {}


def test_encounter_won_when_player_survives():

    encounter = EncounterData(
        encounter="ENCOUNTER.TEST",
        encounter_type="elite",
        act=1,
        floor=10,
        act_floor=10,
        turns_taken=5,
        damage_taken=20,
        current_hp=30,
        max_hp=80,
        hp_healed=0,
        max_hp_gained=0,
        max_hp_lost=0,
    )

    assert encounter_won(encounter) is True


def test_encounter_won_when_player_dies():

    encounter = EncounterData(
        encounter="ENCOUNTER.TEST",
        encounter_type="elite",
        act=1,
        floor=10,
        act_floor=10,
        turns_taken=5,
        damage_taken=80,
        current_hp=0,
        max_hp=80,
        hp_healed=0,
        max_hp_gained=0,
        max_hp_lost=0,
    )

    assert encounter_won(encounter) is False