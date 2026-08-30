STARTING_DECKS: dict[str, list[str]] = {
    "Ironclad": [
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
    ],
    "Silent": [
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
    ],
    "Regent": [
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
    ],
    "Necrobinder": [
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
    ],
    "Defect": [
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
    ],
}


def get_starting_deck(
    character: str,
    ascension: int,
) -> list[str]:
    """Return the starting deck for a character and ascension."""

    if character not in STARTING_DECKS:
        raise ValueError(
            f"Unknown character: {character}"
        )

    deck = list(STARTING_DECKS[character])

    if ascension >= 5:
        deck.append("CARD.ASCENDERS_BANE")

    return deck