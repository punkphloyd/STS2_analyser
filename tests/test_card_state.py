from analysis.card_state import (
    CardState,
    add_card,
    make_starting_card_states,
    transform_card,
    upgrade_card,
)


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