from dataclasses import dataclass

from data.starting_decks import get_starting_deck
from data_models.run_data import RunData


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


def copy_card_states(
    card_states: list[CardState],
) -> list[CardState]:
    """Return an independent copy of a card-state list."""

    return [
        CardState(
            card=card_state.card,
            upgraded=card_state.upgraded,
        )
        for card_state in card_states
    ]


def apply_run_card_activity(
    run: RunData,
    card_states: list[CardState],
    floor: int,
) -> None:
    """
    Apply all card activity occurring on a given floor.

    Transformations are applied before upgrades, followed by
    acquisitions.

    This function mutates card_states.
    """

    for transformation in run.card_transformations:
        if transformation.floor != floor:
            continue

        transform_card(
            card_states,
            transformation.original_card,
            transformation.final_card,
        )

    for upgrade in run.card_upgrades:
        if upgrade.floor != floor:
            continue

        upgrade_card(
            card_states,
            upgrade.card,
        )

    for acquisition in run.card_acquisitions:
        if acquisition.floor != floor:
            continue

        add_card(
            card_states,
            acquisition.card,
            upgraded=acquisition.upgraded,
        )


def get_card_states_at_floor(
    run: RunData,
    floor: int,
) -> list[CardState]:
    """
    Return the card states at the end of a given floor.

    All card activity occurring on floors up to and including
    the requested floor is applied.

    Raises ValueError if floor is outside the run.
    """

    if floor < 0 or floor > run.floor_reached:
        raise ValueError(
            f"Floor must be between 0 and "
            f"{run.floor_reached}: {floor}"
        )

    card_states = make_starting_card_states(
        run.metadata.character,
        run.metadata.ascension,
    )

    for current_floor in range(1, floor + 1):
        apply_run_card_activity(
            run,
            card_states,
            current_floor,
        )

    return card_states


def reconstruct_card_states(
    run: RunData,
) -> list[CardState]:
    """Return the card states at the end of the run."""

    return get_card_states_at_floor(
        run,
        run.floor_reached,
    )