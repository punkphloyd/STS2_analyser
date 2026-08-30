import pytest

from data.starting_decks import (
    STARTING_DECKS,
    get_starting_deck,
)


def test_ironclad_starting_deck():
    deck = get_starting_deck(
        "Ironclad",
        0,
    )

    assert deck == [
        "CARD.STRIKE_IRONCLAD",
        "CARD.STRIKE_IRONCLAD",
        "CARD.STRIKE_IRONCLAD",
        "CARD.STRIKE_IRONCLAD",
        "CARD.STRIKE_IRONCLAD",
        "CARD.DEFEND_IRONCLAD",
        "CARD.DEFEND_IRONCLAD",
        "CARD.DEFEND_IRONCLAD",
        "CARD.DEFEND_IRONCLAD",
        "CARD.BASH",
    ]


def test_silent_starting_deck():
    deck = get_starting_deck(
        "Silent",
        0,
    )

    assert deck == [
        "CARD.STRIKE_SILENT",
        "CARD.STRIKE_SILENT",
        "CARD.STRIKE_SILENT",
        "CARD.STRIKE_SILENT",
        "CARD.STRIKE_SILENT",
        "CARD.DEFEND_SILENT",
        "CARD.DEFEND_SILENT",
        "CARD.DEFEND_SILENT",
        "CARD.DEFEND_SILENT",
        "CARD.DEFEND_SILENT",
        "CARD.NEUTRALIZE",
        "CARD.SURVIVOR",
    ]


def test_regent_starting_deck():
    deck = get_starting_deck(
        "Regent",
        0,
    )

    assert deck == [
        "CARD.STRIKE_REGENT",
        "CARD.STRIKE_REGENT",
        "CARD.STRIKE_REGENT",
        "CARD.STRIKE_REGENT",
        "CARD.DEFEND_REGENT",
        "CARD.DEFEND_REGENT",
        "CARD.DEFEND_REGENT",
        "CARD.DEFEND_REGENT",
        "CARD.FALLING_STAR",
        "CARD.VENERATE",
    ]


def test_necrobinder_starting_deck():
    deck = get_starting_deck(
        "Necrobinder",
        0,
    )

    assert deck == [
        "CARD.STRIKE_NECROBINDER",
        "CARD.STRIKE_NECROBINDER",
        "CARD.STRIKE_NECROBINDER",
        "CARD.STRIKE_NECROBINDER",
        "CARD.DEFEND_NECROBINDER",
        "CARD.DEFEND_NECROBINDER",
        "CARD.DEFEND_NECROBINDER",
        "CARD.DEFEND_NECROBINDER",
        "CARD.BODYGUARD",
        "CARD.UNLEASH",
    ]


def test_defect_starting_deck():
    deck = get_starting_deck(
        "Defect",
        0,
    )

    assert deck == [
        "CARD.STRIKE_DEFECT",
        "CARD.STRIKE_DEFECT",
        "CARD.STRIKE_DEFECT",
        "CARD.STRIKE_DEFECT",
        "CARD.DEFEND_DEFECT",
        "CARD.DEFEND_DEFECT",
        "CARD.DEFEND_DEFECT",
        "CARD.DEFEND_DEFECT",
        "CARD.ZAP",
        "CARD.DUALCAST",
    ]


@pytest.mark.parametrize(
    "character,expected_size",
    [
        ("Ironclad", 10),
        ("Silent", 12),
        ("Regent", 10),
        ("Necrobinder", 10),
        ("Defect", 10),
    ],
)
def test_starting_deck_size_at_ascension_zero(
    character: str,
    expected_size: int,
):
    deck = get_starting_deck(
        character,
        0,
    )

    assert len(deck) == expected_size


@pytest.mark.parametrize(
    "character",
    [
        "Ironclad",
        "Silent",
        "Regent",
        "Necrobinder",
        "Defect",
    ],
)
def test_ascenders_bane_not_present_below_ascension_five(
    character: str,
):
    deck = get_starting_deck(
        character,
        4,
    )

    assert "CARD.ASCENDERS_BANE" not in deck


@pytest.mark.parametrize(
    "character",
    [
        "Ironclad",
        "Silent",
        "Regent",
        "Necrobinder",
        "Defect",
    ],
)
@pytest.mark.parametrize(
    "ascension",
    [5, 10, 20],
)
def test_ascenders_bane_present_at_ascension_five_and_above(
    character: str,
    ascension: int,
):
    deck = get_starting_deck(
        character,
        ascension,
    )

    assert "CARD.ASCENDERS_BANE" in deck
    assert len(deck) == len(STARTING_DECKS[character]) + 1


def test_unknown_character_raises_error():
    with pytest.raises(ValueError):
        get_starting_deck(
            "Unknown Character",
            0,
        )


def test_starting_deck_is_independent_copy():
    first_deck = get_starting_deck(
        "Ironclad",
        0,
    )

    first_deck.append("CARD.TEST")

    second_deck = get_starting_deck(
        "Ironclad",
        0,
    )

    assert "CARD.TEST" not in second_deck


def test_ascenders_bane_does_not_modify_static_deck():
    deck = get_starting_deck(
        "Ironclad",
        5,
    )

    assert "CARD.ASCENDERS_BANE" in deck
    assert "CARD.ASCENDERS_BANE" not in STARTING_DECKS["Ironclad"]