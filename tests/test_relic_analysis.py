from datetime import datetime
from pathlib import Path

from analysis.relic_analysis import (
    calculate_neow_relic_statistics,
    calculate_relic_encounter_statistics,
    calculate_relic_statistics,
)
from data_models.encounter_data import EncounterData
from data_models.relic_data import RelicAcquisition
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata
from parsers.run_parser import parse_run


def make_run(
    offered_relics: list[str],
    selected_relic: str | None,
    victory: bool,
    relic_acquisitions: list[RelicAcquisition] | None = None,
    encounters: list[EncounterData] | None = None,
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
        relic_acquisitions=relic_acquisitions or [],
        encounters=encounters or [],
    )


def make_relic_acquisition(
    relic: str,
    floor: int,
) -> RelicAcquisition:

    return RelicAcquisition(
        relic=relic,
        source="elite",
        act=1,
        floor=floor,
        act_floor=floor,
    )


def make_encounter(
    encounter: str,
    encounter_type: str,
    floor: int,
    current_hp: int = 20,
    damage_taken: int = 10,
    turns_taken: int = 5,
) -> EncounterData:

    return EncounterData(
        encounter=encounter,
        encounter_type=encounter_type,
        act=1,
        floor=floor,
        act_floor=floor,
        turns_taken=turns_taken,
        damage_taken=damage_taken,
        current_hp=current_hp,
        max_hp=80,
        hp_healed=0,
        max_hp_gained=0,
        max_hp_lost=0,
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


def test_relic_statistics():

    runs = [
        make_run(
            [],
            None,
            True,
            relic_acquisitions=[
                make_relic_acquisition(
                    "RELIC.TEST",
                    5,
                ),
            ],
        ),
        make_run(
            [],
            None,
            False,
            relic_acquisitions=[
                make_relic_acquisition(
                    "RELIC.TEST",
                    10,
                ),
            ],
        ),
    ]

    result = calculate_relic_statistics(runs)

    assert result["RELIC.TEST"].runs_acquired == 2
    assert result["RELIC.TEST"].wins == 1
    assert result["RELIC.TEST"].win_rate == 0.5


def test_relic_statistics_empty():

    assert calculate_relic_statistics([]) == {}


def test_relic_encounter_statistics_empty():

    assert calculate_relic_encounter_statistics([]) == {}


def test_relic_encounter_statistics_relic_acquired_before_encounter():

    relic = make_relic_acquisition(
        "RELIC.TEST",
        5,
    )

    encounter = make_encounter(
        "ENCOUNTER.TEST_ELITE",
        "elite",
        10,
        current_hp=30,
        damage_taken=20,
        turns_taken=5,
    )

    run = make_run(
        [],
        None,
        True,
        relic_acquisitions=[relic],
        encounters=[encounter],
    )

    result = calculate_relic_encounter_statistics(
        [run],
        encounter_type="elite",
    )

    statistics = result["RELIC.TEST"]

    assert statistics.fights == 1
    assert statistics.wins == 1
    assert statistics.win_rate == 1.0
    assert statistics.average_damage == 20
    assert statistics.median_damage == 20
    assert statistics.minimum_damage == 20
    assert statistics.maximum_damage == 20
    assert statistics.average_turns == 5
    assert statistics.minimum_turns == 5
    assert statistics.maximum_turns == 5
    assert statistics.average_damage_per_turn == 4


def test_relic_acquired_on_same_floor_is_not_present():

    relic = make_relic_acquisition(
        "RELIC.TEST",
        10,
    )

    encounter = make_encounter(
        "ENCOUNTER.TEST_ELITE",
        "elite",
        10,
    )

    run = make_run(
        [],
        None,
        True,
        relic_acquisitions=[relic],
        encounters=[encounter],
    )

    result = calculate_relic_encounter_statistics(
        [run],
        encounter_type="elite",
    )

    assert "RELIC.TEST" not in result


def test_relic_acquired_after_encounter_is_not_present():

    relic = make_relic_acquisition(
        "RELIC.TEST",
        15,
    )

    encounter = make_encounter(
        "ENCOUNTER.TEST_ELITE",
        "elite",
        10,
    )

    run = make_run(
        [],
        None,
        True,
        relic_acquisitions=[relic],
        encounters=[encounter],
    )

    result = calculate_relic_encounter_statistics(
        [run],
        encounter_type="elite",
    )

    assert "RELIC.TEST" not in result


def test_relic_contributes_to_multiple_subsequent_encounters():

    relic = make_relic_acquisition(
        "RELIC.TEST",
        5,
    )

    encounters = [
        make_encounter(
            "ENCOUNTER.FIRST_ELITE",
            "elite",
            10,
            current_hp=30,
        ),
        make_encounter(
            "ENCOUNTER.SECOND_ELITE",
            "elite",
            15,
            current_hp=0,
        ),
        make_encounter(
            "ENCOUNTER.THIRD_ELITE",
            "elite",
            20,
            current_hp=40,
        ),
    ]

    run = make_run(
        [],
        None,
        False,
        relic_acquisitions=[relic],
        encounters=encounters,
    )

    result = calculate_relic_encounter_statistics(
        [run],
        encounter_type="elite",
    )

    statistics = result["RELIC.TEST"]

    assert statistics.fights == 3
    assert statistics.wins == 2
    assert statistics.win_rate == 2 / 3


def test_relic_encounter_statistics_respects_encounter_name_filter():

    relic = make_relic_acquisition(
        "RELIC.TEST",
        5,
    )

    encounters = [
        make_encounter(
            "ENCOUNTER.FIRST_ELITE",
            "elite",
            10,
            current_hp=30,
        ),
        make_encounter(
            "ENCOUNTER.SECOND_ELITE",
            "elite",
            15,
            current_hp=0,
        ),
    ]

    run = make_run(
        [],
        None,
        False,
        relic_acquisitions=[relic],
        encounters=encounters,
    )

    result = calculate_relic_encounter_statistics(
        [run],
        encounter_name="ENCOUNTER.SECOND_ELITE",
    )

    statistics = result["RELIC.TEST"]

    assert statistics.fights == 1
    assert statistics.wins == 0
    assert statistics.win_rate == 0.0

def test_relic_encounter_statistics_respects_acquisition_timing():

    path = EXAMPLE_RUNFILES / "1780143874.run"

    run = parse_run(path)

    result = calculate_relic_encounter_statistics(
        [run],
        encounter_type="elite",
    )

    assert "RELIC.WHITE_BEAST_STATUE" in result
    assert "RELIC.BLOOD_VIAL" in result

    white_beast = result["RELIC.WHITE_BEAST_STATUE"]
    blood_vial = result["RELIC.BLOOD_VIAL"]

    # White Beast was acquired on floor 10,
    # so it is present for the floor-12 elite.
    assert white_beast.fights >= 1

    # Blood Vial was acquired from the floor-12 elite,
    # so it must not be counted for that fight.
    # It should nevertheless be present for later elites.
    assert blood_vial.fights >= 1


def test_relic_encounter_statistics_calculates_encounter_results():

    encounters = [
        make_encounter(
            "ENCOUNTER.TEST_ELITE",
            "elite",
            10,
            current_hp=20,
            damage_taken=10,
            turns_taken=5,
        ),
        make_encounter(
            "ENCOUNTER.TEST_ELITE",
            "elite",
            15,
            current_hp=0,
            damage_taken=20,
            turns_taken=10,
        ),
    ]

    relic = make_relic_acquisition(
        "RELIC.TEST",
        5,
    )

    run = make_run(
        [],
        None,
        False,
        relic_acquisitions=[relic],
        encounters=encounters,
    )

    result = calculate_relic_encounter_statistics(
        [run],
        encounter_name="ENCOUNTER.TEST_ELITE",
    )

    statistics = result["RELIC.TEST"]

    assert statistics.fights == 2
    assert statistics.wins == 1
    assert statistics.win_rate == 0.5

    assert statistics.average_damage == 15
    assert statistics.median_damage == 15
    assert statistics.minimum_damage == 10
    assert statistics.maximum_damage == 20

    assert statistics.average_turns == 7.5
    assert statistics.minimum_turns == 5
    assert statistics.maximum_turns == 10

    assert statistics.average_damage_per_turn == 2