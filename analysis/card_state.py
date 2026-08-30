from dataclasses import dataclass


@dataclass(slots=True)
class CardState:
    """Represent a single card currently in the deck."""

    card: str
    upgraded: bool = False


def make_starting_card_states(
    character: str,
    ascension: int,
) -> list[CardState]:
    """Return the initial card states for a run."""

    from data.starting_decks import get_starting_deck

    return [
        CardState(card=card)
        for card in get_starting_deck(
            character,
            ascension,
        )
    ]