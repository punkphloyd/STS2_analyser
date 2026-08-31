from datetime import datetime
from pathlib import Path

from analysis.card_state import (
    CardState,
    add_card,
    apply_run_card_activity,
    copy_card_states,
    get_card_states_at_floor,
    make_starting_card_states,
    reconstruct_card_states,
    transform_card,
    upgrade_card,
)
from data_models.card_acquisition import CardAcquisition
from data_models.card_transformation import CardTransformation
from data_models.card_upgrade import CardUpgrade
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata
from parsers.run_parser import parse_run

def make_run(
    *,
    floor_reached: int = 10,
    character: str = "Silent",
    ascension: int = 0,
    card_acquisitions: list[CardAcquisition] | None = None,
    card_upgrades: list[CardUpgrade] | None = None,
    card_transformations: list[CardTransformation] | None = None,
) -> RunData:
    """Create a minimal RunData object for card-state tests."""

    return RunData(
        metadata=RunMetadata(
            file_path=Path("test.run"),
            start_time=datetime(2026, 8, 1),
            character=character,
            ascension=ascension,
            victory=False,
            game_version="test",
            game_mode="standard",
            multiplayer=False,
        ),
        floor_reached=floor_reached,
        card_acquisitions=(
            card_acquisitions
            if card_acquisitions is not None
            else []
        ),
        card_upgrades=(
            card_upgrades
            if card_upgrades is not None
            else []
        ),
        card_transformations=(
            card_transformations
            if card_transformations is not None
            else []
        ),
    )


def make_acquisition(
    card: str,
    floor: int,
    upgraded: bool = False,
    source: str = "monster",
) -> CardAcquisition:
    """Create a test card acquisition."""

    return CardAcquisition(
        card=card,
        source=source,
        act=1,
        floor=floor,
        act_floor=floor,
        upgraded=upgraded,
    )


def make_upgrade(
    card: str,
    floor: int,
    source: str = "rest_site",
) -> CardUpgrade:
    """Create a test card upgrade."""

    return CardUpgrade(
        card=card,
        source=source,
        act=1,
        floor=floor,
        act_floor=floor,
    )


def make_transformation(
    original_card: str,
    final_card: str,
    floor: int,
    source: str = "event",
) -> CardTransformation:
    """Create a test card transformation."""

    return CardTransformation(
        original_card=original_card,
        final_card=final_card,
        source=source,
        act=1,
        floor=floor,
        act_floor=floor,
    )


# ---------------------------------------------------------------------------
# Existing CardState tests
# ---------------------------------------------------------------------------


def test_make_starting_card_states():
    states = make_starting_card_states(
        "Ironclad",
        0,
    )

    assert len(states) == 10
    assert states.count(
        CardState("CARD.STRIKE_IRONCLAD")
    ) == 5
    assert states.count(
        CardState("CARD.DEFEND_IRONCLAD")
    ) == 4
    assert CardState("CARD.BASH") in states


def test_make_starting_card_states_includes_ascenders_bane():
    states = make_starting_card_states(
        "Silent",
        5,
    )

    assert CardState("CARD.ASCENDERS_BANE") in states
    assert len(states) == 13


def test_add_unupgraded_card():
    states = []

    add_card(
        states,
        "CARD.CLOAK_AND_DAGGER",
    )

    assert states == [
        CardState("CARD.CLOAK_AND_DAGGER")
    ]


def test_add_upgraded_card():
    states = []

    add_card(
        states,
        "CARD.PREDATOR",
        upgraded=True,
    )

    assert states == [
        CardState(
            "CARD.PREDATOR",
            upgraded=True,
        )
    ]


def test_add_card_does_not_modify_existing_cards():
    states = [
        CardState("CARD.STRIKE_SILENT"),
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
    ]

    add_card(
        states,
        "CARD.BASH",
    )

    assert states == [
        CardState("CARD.STRIKE_SILENT"),
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
        CardState("CARD.BASH"),
    ]


def test_upgrade_card():
    states = [
        CardState("CARD.STRIKE_SILENT"),
    ]

    result = upgrade_card(
        states,
        "CARD.STRIKE_SILENT",
    )

    assert result is True
    assert states == [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        )
    ]


def test_upgrade_only_one_copy():
    states = [
        CardState("CARD.STRIKE_SILENT"),
        CardState("CARD.STRIKE_SILENT"),
        CardState("CARD.STRIKE_SILENT"),
    ]

    result = upgrade_card(
        states,
        "CARD.STRIKE_SILENT",
    )

    assert result is True
    assert states == [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
        CardState("CARD.STRIKE_SILENT"),
        CardState("CARD.STRIKE_SILENT"),
    ]


def test_upgrade_unupgraded_copy_when_upgraded_copy_already_exists():
    states = [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
        CardState("CARD.STRIKE_SILENT"),
    ]

    result = upgrade_card(
        states,
        "CARD.STRIKE_SILENT",
    )

    assert result is True
    assert states == [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
    ]


def test_upgrade_already_upgraded_card_does_nothing():
    states = [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        )
    ]

    result = upgrade_card(
        states,
        "CARD.STRIKE_SILENT",
    )

    assert result is False
    assert states == [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        )
    ]


def test_upgrade_missing_card_does_nothing():
    states = [
        CardState("CARD.STRIKE_SILENT"),
    ]

    result = upgrade_card(
        states,
        "CARD.BASH",
    )

    assert result is False
    assert states == [
        CardState("CARD.STRIKE_SILENT")
    ]


def test_transform_unupgraded_card():
    states = [
        CardState("CARD.STRIKE_SILENT"),
    ]

    result = transform_card(
        states,
        "CARD.STRIKE_SILENT",
        "CARD.BASH",
    )

    assert result is True
    assert states == [
        CardState("CARD.BASH")
    ]


def test_transform_upgraded_card_produces_unupgraded_card():
    states = [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        )
    ]

    result = transform_card(
        states,
        "CARD.STRIKE_SILENT",
        "CARD.BASH",
    )

    assert result is True
    assert states == [
        CardState("CARD.BASH")
    ]


def test_transform_only_one_copy():
    states = [
        CardState("CARD.STRIKE_SILENT"),
        CardState("CARD.STRIKE_SILENT"),
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
    ]

    result = transform_card(
        states,
        "CARD.STRIKE_SILENT",
        "CARD.BASH",
    )

    assert result is True
    assert states == [
        CardState("CARD.BASH"),
        CardState("CARD.STRIKE_SILENT"),
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        ),
    ]


def test_transform_can_consume_an_upgraded_copy():
    states = [
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        )
    ]

    result = transform_card(
        states,
        "CARD.STRIKE_SILENT",
        "CARD.BASH",
    )

    assert result is True
    assert states == [
        CardState("CARD.BASH")
    ]


def test_transform_missing_card_does_nothing():
    states = [
        CardState("CARD.STRIKE_SILENT"),
    ]

    result = transform_card(
        states,
        "CARD.BASH",
        "CARD.NEUTRALIZE",
    )

    assert result is False
    assert states == [
        CardState("CARD.STRIKE_SILENT")
    ]


def test_transform_does_not_modify_other_cards():
    states = [
        CardState("CARD.STRIKE_SILENT"),
        CardState(
            "CARD.DEFEND_SILENT",
            upgraded=True,
        ),
    ]

    result = transform_card(
        states,
        "CARD.STRIKE_SILENT",
        "CARD.BASH",
    )

    assert result is True
    assert states == [
        CardState("CARD.BASH"),
        CardState(
            "CARD.DEFEND_SILENT",
            upgraded=True,
        ),
    ]


# ---------------------------------------------------------------------------
# Card-state reconstruction tests
# ---------------------------------------------------------------------------


def test_copy_card_states_is_independent():
    original = [
        CardState("CARD.STRIKE_SILENT"),
        CardState(
            "CARD.DEFEND_SILENT",
            upgraded=True,
        ),
    ]

    copied = copy_card_states(original)

    copied[0].upgraded = True
    copied.append(
        CardState("CARD.BASH")
    )

    assert original == [
        CardState("CARD.STRIKE_SILENT"),
        CardState(
            "CARD.DEFEND_SILENT",
            upgraded=True,
        ),
    ]


def test_apply_run_card_activity_adds_card():
    run = make_run(
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
            ),
        ],
    )

    states = make_starting_card_states(
        "Silent",
        0,
    )

    apply_run_card_activity(
        run,
        states,
        3,
    )

    assert states.count(
        CardState("CARD.CLOAK_AND_DAGGER")
    ) == 1


def test_apply_run_card_activity_adds_pre_upgraded_card():
    run = make_run(
        card_acquisitions=[
            make_acquisition(
                "CARD.PREDATOR",
                floor=3,
                upgraded=True,
            ),
        ],
    )

    states = make_starting_card_states(
        "Silent",
        0,
    )

    apply_run_card_activity(
        run,
        states,
        3,
    )

    assert CardState(
        "CARD.PREDATOR",
        upgraded=True,
    ) in states


def test_apply_run_card_activity_upgrades_card():
    run = make_run(
        card_upgrades=[
            make_upgrade(
                "CARD.STRIKE_SILENT",
                floor=3,
            ),
        ],
    )

    states = make_starting_card_states(
        "Silent",
        0,
    )

    apply_run_card_activity(
        run,
        states,
        3,
    )

    assert states.count(
        CardState(
            "CARD.STRIKE_SILENT",
            upgraded=True,
        )
    ) == 1

    assert states.count(
        CardState("CARD.STRIKE_SILENT")
    ) == 4


def test_apply_run_card_activity_transforms_card():
    run = make_run(
        card_transformations=[
            make_transformation(
                "CARD.DEFEND_SILENT",
                "CARD.TORIC_TOUGHNESS",
                floor=3,
            ),
        ],
    )

    states = make_starting_card_states(
        "Silent",
        0,
    )

    apply_run_card_activity(
        run,
        states,
        3,
    )

    assert states.count(
        CardState("CARD.DEFEND_SILENT")
    ) == 4

    assert states.count(
        CardState("CARD.TORIC_TOUGHNESS")
    ) == 1


def test_apply_run_card_activity_transform_of_upgraded_card_is_unupgraded():
    run = make_run(
        card_transformations=[
            make_transformation(
                "CARD.DEFEND_SILENT",
                "CARD.TORIC_TOUGHNESS",
                floor=3,
            ),
        ],
    )

    states = make_starting_card_states(
        "Silent",
        0,
    )

    states[5].upgraded = True

    apply_run_card_activity(
        run,
        states,
        3,
    )

    assert CardState(
        "CARD.TORIC_TOUGHNESS",
        upgraded=True,
    ) not in states

    assert CardState(
        "CARD.TORIC_TOUGHNESS"
    ) in states


def test_apply_run_card_activity_ignores_other_floors():
    run = make_run(
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=4,
            ),
        ],
    )

    states = make_starting_card_states(
        "Silent",
        0,
    )

    apply_run_card_activity(
        run,
        states,
        3,
    )

    assert CardState(
        "CARD.CLOAK_AND_DAGGER"
    ) not in states


def test_get_card_states_at_floor_returns_starting_deck_at_floor_zero():
    run = make_run(
        floor_reached=10,
        character="Ironclad",
        ascension=0,
    )

    states = get_card_states_at_floor(
        run,
        0,
    )

    assert len(states) == 10

    assert states.count(
        CardState("CARD.STRIKE_IRONCLAD")
    ) == 5

    assert states.count(
        CardState("CARD.DEFEND_IRONCLAD")
    ) == 4

    assert states.count(
        CardState("CARD.BASH")
    ) == 1


def test_get_card_states_at_floor_applies_activity_up_to_requested_floor():
    run = make_run(
        floor_reached=10,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
            ),
            make_acquisition(
                "CARD.POISONED_STAB",
                floor=7,
            ),
        ],
    )

    floor_2 = get_card_states_at_floor(
        run,
        2,
    )

    floor_3 = get_card_states_at_floor(
        run,
        3,
    )

    floor_6 = get_card_states_at_floor(
        run,
        6,
    )

    floor_7 = get_card_states_at_floor(
        run,
        7,
    )

    assert CardState(
        "CARD.CLOAK_AND_DAGGER"
    ) not in floor_2

    assert CardState(
        "CARD.CLOAK_AND_DAGGER"
    ) in floor_3

    assert CardState(
        "CARD.POISONED_STAB"
    ) not in floor_6

    assert CardState(
        "CARD.POISONED_STAB"
    ) in floor_7


def test_get_card_states_at_floor_applies_transformation_then_upgrade():
    run = make_run(
        floor_reached=10,
        card_transformations=[
            make_transformation(
                "CARD.DEFEND_SILENT",
                "CARD.BASH",
                floor=3,
            ),
        ],
        card_upgrades=[
            make_upgrade(
                "CARD.BASH",
                floor=3,
            ),
        ],
    )

    states = get_card_states_at_floor(
        run,
        3,
    )

    assert CardState(
        "CARD.BASH",
        upgraded=True,
    ) in states

    assert states.count(
        CardState("CARD.DEFEND_SILENT")
    ) == 4



def test_reconstruct_card_states_returns_final_deck():
    run = make_run(
        floor_reached=10,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
            ),
            make_acquisition(
                "CARD.PREDATOR",
                floor=8,
                upgraded=True,
            ),
        ],
        card_transformations=[
            make_transformation(
                "CARD.DEFEND_SILENT",
                "CARD.BASH",
                floor=5,
            ),
        ],
        card_upgrades=[
            make_upgrade(
                "CARD.BASH",
                floor=6,
            ),
        ],
    )

    states = reconstruct_card_states(run)

    assert CardState(
        "CARD.CLOAK_AND_DAGGER"
    ) in states

    assert CardState(
        "CARD.PREDATOR",
        upgraded=True,
    ) in states

    assert CardState(
        "CARD.BASH",
        upgraded=True,
    ) in states

    assert states.count(
        CardState("CARD.DEFEND_SILENT")
    ) == 4


def test_get_card_states_at_floor_results_are_independent():
    run = make_run(
        floor_reached=10,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
            ),
            make_acquisition(
                "CARD.POISONED_STAB",
                floor=5,
            ),
        ],
    )

    floor_3 = get_card_states_at_floor(
        run,
        3,
    )

    floor_5 = get_card_states_at_floor(
        run,
        5,
    )

    assert CardState(
        "CARD.CLOAK_AND_DAGGER"
    ) in floor_3

    assert CardState(
        "CARD.POISONED_STAB"
    ) not in floor_3

    assert CardState(
        "CARD.POISONED_STAB"
    ) in floor_5


def test_get_card_states_at_floor_rejects_negative_floor():
    run = make_run(
        floor_reached=10,
    )

    try:
        get_card_states_at_floor(
            run,
            -1,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_get_card_states_at_floor_rejects_floor_after_run():
    run = make_run(
        floor_reached=10,
    )

    try:
        get_card_states_at_floor(
            run,
            11,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError"
        )

def test_real_run_transformation_produces_unupgraded_card():
    path = (
        Path("example_runfiles")
        / "1780143874.run"
    )

    run = parse_run(path)

    states = get_card_states_at_floor(
        run,
        7,
    )

    assert CardState(
        "CARD.TORIC_TOUGHNESS",
    ) in states

    assert CardState(
        "CARD.TORIC_TOUGHNESS",
        upgraded=True,
    ) not in states


def test_real_run_transformation_then_upgrade():
    path = (
        Path("example_runfiles")
        / "1780143874.run"
    )

    run = parse_run(path)

    states_after_floor_7 = (
        get_card_states_at_floor(
            run,
            7,
        )
    )

    assert CardState(
        "CARD.TORIC_TOUGHNESS",
    ) in states_after_floor_7

    assert CardState(
        "CARD.TORIC_TOUGHNESS",
        upgraded=True,
    ) not in states_after_floor_7

    states_after_floor_8 = (
        get_card_states_at_floor(
            run,
            8,
        )
    )

    assert CardState(
        "CARD.TORIC_TOUGHNESS",
        upgraded=True,
    ) in states_after_floor_8

    assert CardState(
        "CARD.TORIC_TOUGHNESS",
    ) not in states_after_floor_8


def test_real_run_reconstructs_multiple_card_copies():
    path = (
        Path("example_runfiles")
        / "1780143874.run"
    )

    run = parse_run(path)

    states = reconstruct_card_states(run)

    assert states.count(
        CardState("CARD.DAGGER_THROW")
    ) == 2

    assert states.count(
        CardState("CARD.ACROBATICS")
    ) == 2