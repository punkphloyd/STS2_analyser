from datetime import datetime
from pathlib import Path

from analysis.encounter_analysis import (
    acquisition_precedes_encounter,
    relic_present_at_encounter,
)
from data_models.encounter_data import EncounterData
from data_models.relic_data import RelicAcquisition
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata
from parsers.run_parser import parse_run


EXAMPLE_RUNFILES = Path("example_runfiles")


def make_encounter(
    floor: int,
) -> EncounterData:
    return EncounterData(
        encounter="ENCOUNTER.TEST_ELITE",
        encounter_type="elite",
        act=1,
        floor=floor,
        act_floor=floor,
        turns_taken=5,
        damage_taken=10,
        current_hp=20,
        max_hp=50,
        hp_healed=0,
        max_hp_gained=0,
        max_hp_lost=0,
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


def make_run(
    relic_acquisitions: list[RelicAcquisition],
) -> RunData:
    return RunData(
        metadata=RunMetadata(
            file_path=Path("test.run"),
            start_time=datetime(2026, 8, 1),
            character="Ironclad",
            ascension=0,
            victory=False,
            game_version="v0.107.1",
            game_mode="standard",
            multiplayer=False,
        ),
        floor_reached=30,
        relic_acquisitions=relic_acquisitions,
    )


def test_acquisition_precedes_encounter():

    acquisition = make_relic_acquisition(
        "RELIC.TEST",
        5,
    )

    encounter = make_encounter(8)

    assert acquisition_precedes_encounter(
        acquisition,
        encounter,
    )


def test_acquisition_on_same_floor_does_not_precede_encounter():

    acquisition = make_relic_acquisition(
        "RELIC.TEST",
        8,
    )

    encounter = make_encounter(8)

    assert not acquisition_precedes_encounter(
        acquisition,
        encounter,
    )


def test_relic_present_at_encounter():

    acquisition = make_relic_acquisition(
        "RELIC.TEST",
        5,
    )

    run = make_run(
        [acquisition],
    )

    encounter = make_encounter(8)

    assert relic_present_at_encounter(
        "RELIC.TEST",
        run,
        encounter,
    )


def test_relic_not_present_if_acquired_at_or_after_encounter():

    acquisition = make_relic_acquisition(
        "RELIC.TEST",
        8,
    )

    run = make_run(
        [acquisition],
    )

    encounter = make_encounter(8)

    assert not relic_present_at_encounter(
        "RELIC.TEST",
        run,
        encounter,
    )


def test_relic_not_present_if_not_acquired():

    run = make_run([])

    encounter = make_encounter(8)

    assert not relic_present_at_encounter(
        "RELIC.TEST",
        run,
        encounter,
    )


def test_relic_presence_respects_acquisition_floor():

    path = EXAMPLE_RUNFILES / "1780143874.run"

    run = parse_run(path)

    before_white_beast = next(
        encounter
        for encounter in run.encounters
        if encounter.floor < 10
    )

    blood_vial_encounter = next(
        encounter
        for encounter in run.encounters
        if (
            encounter.floor == 12
            and encounter.encounter_type == "elite"
        )
    )

    after_blood_vial = next(
        encounter
        for encounter in run.encounters
        if encounter.floor > 12
    )

    assert not relic_present_at_encounter(
        "RELIC.WHITE_BEAST_STATUE",
        run,
        before_white_beast,
    )

    assert relic_present_at_encounter(
        "RELIC.WHITE_BEAST_STATUE",
        run,
        blood_vial_encounter,
    )

    assert not relic_present_at_encounter(
        "RELIC.BLOOD_VIAL",
        run,
        blood_vial_encounter,
    )

    assert relic_present_at_encounter(
        "RELIC.BLOOD_VIAL",
        run,
        after_blood_vial,
    )