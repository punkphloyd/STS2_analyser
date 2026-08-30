from dataclasses import dataclass

from data.starting_decks import get_starting_deck


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

    return [
        CardState(card=card)
        for card in get_starting_deck(
            character,
            ascension,
        )
    ]


def add_card(
    card_states: list[CardState],
    card: str,
    upgraded: bool = False,
) -> None:
    """Add a card to the current deck state."""

    card_states.append(
        CardState(
            card=card,
            upgraded=upgraded,
        )
    )


def upgrade_card(
    card_states: list[CardState],
    card: str,
) -> bool:
    """
    Upgrade one unupgraded copy of a card.

    Returns True if a card was upgraded, otherwise False.
    """

    for card_state in card_states:
        if (
            card_state.card == card
            and not card_state.upgraded
        ):
            card_state.upgraded = True
            return True

    return False


def transform_card(
    card_states: list[CardState],
    original_card: str,
    final_card: str,
) -> bool:
    """
    Transform one copy of a card.

    The transformed card is always unupgraded.

    Returns True if a card was transformed, otherwise False.
    """

    for index, card_state in enumerate(card_states):
        if card_state.card != original_card:
            continue

        card_states[index] = CardState(
            card=final_card,
            upgraded=False,
        )

        return True

    return False