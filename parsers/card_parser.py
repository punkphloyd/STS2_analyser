from data_models.card_acquisition import CardAcquisition
from data_models.card_reward import CardReward
from data_models.card_transformation import CardTransformation
from data_models.card_upgrade import CardUpgrade


def parse_card_data(
    data: dict,
) -> tuple[
    list[CardReward],
    list[CardAcquisition],
    list[CardUpgrade],
    list[CardTransformation],
]:
    """Parse card activity from map point history."""

    rewards: list[CardReward] = []
    acquisitions: list[CardAcquisition] = []
    upgrades: list[CardUpgrade] = []
    transformations: list[CardTransformation] = []

    floor = 0

    for act_index, map_point_group in enumerate(
        data.get("map_point_history", [])
    ):
        act = act_index + 1

        for act_floor, map_point in enumerate(
            map_point_group,
            start=1,
        ):
            floor += 1

            source = get_card_source(map_point)

            if source is None:
                continue

            stats = get_player_stats(map_point)

            if stats is None:
                continue

            if source == "shop":
                parse_shop_cards(
                    stats=stats,
                    act=act,
                    floor=floor,
                    act_floor=act_floor,
                    rewards=rewards,
                    acquisitions=acquisitions,
                )
            else:
                parse_reward_cards(
                    stats=stats,
                    source=source,
                    act=act,
                    floor=floor,
                    act_floor=act_floor,
                    rewards=rewards,
                    acquisitions=acquisitions,
                )

            parse_upgrades(
                stats=stats,
                source=source,
                act=act,
                floor=floor,
                act_floor=act_floor,
                upgrades=upgrades,
            )

            parse_transformations(
                stats=stats,
                source=source,
                act=act,
                floor=floor,
                act_floor=act_floor,
                transformations=transformations,
            )

    return (
        rewards,
        acquisitions,
        upgrades,
        transformations,
    )


def get_card_source(
    map_point: dict,
) -> str | None:
    """Determine the source of card activity at a map point."""
    map_point_type = map_point.get(
        "map_point_type"
    )

    if map_point_type in {
        "monster",
        "elite",
        "boss",
        "shop",
        "rest_site",
    }:
        return map_point_type

    rooms = map_point.get(
        "rooms",
        []
    )

    for room in rooms:
        room_type = room.get("room_type")

        if room_type in {
            "monster",
            "elite",
            "boss",
            "shop",
            "rest_site",
        }:
            return room_type

        if room_type == "event":
            return "event"

    return None


def get_player_stats(
    map_point: dict,
) -> dict | None:
    """Return the first player's statistics."""

    player_stats = map_point.get(
        "player_stats",
        []
    )

    if not player_stats:
        return None

    return player_stats[0]


def parse_reward_cards(
    stats: dict,
    source: str,
    act: int,
    floor: int,
    act_floor: int,
    rewards: list[CardReward],
    acquisitions: list[CardAcquisition],
) -> None:
    """Parse card rewards and card acquisitions at a map point."""

    card_choices = stats.get(
        "card_choices",
        []
    )

    cards_gained = stats.get(
        "cards_gained",
        []
    )

    if card_choices:
        offered_cards: list[str] = []
        picked_cards: list[str] = []

        for choice in card_choices:
            card = choice.get(
                "card",
                {}
            )

            card_id = card.get("id")

            if card_id is None:
                continue

            offered_cards.append(card_id)

            if choice.get("was_picked") is True:
                picked_cards.append(card_id)

        rewards.append(
            CardReward(
                source=source,
                act=act,
                floor=floor,
                act_floor=act_floor,
                offered_cards=offered_cards,
                picked_cards=picked_cards,
            )
        )

    for card in cards_gained:
        card_id = card.get("id")

        if card_id is None:
            continue

        acquisitions.append(
            CardAcquisition(
                card=card_id,
                source=source,
                act=act,
                floor=floor,
                act_floor=act_floor,
                upgraded=(
                    card.get(
                        "current_upgrade_level",
                        0,
                    )
                    > 0
                ),
            )
        )

def parse_shop_cards(
    stats: dict,
    act: int,
    floor: int,
    act_floor: int,
    rewards: list[CardReward],
    acquisitions: list[CardAcquisition],
) -> None:
    """Parse cards offered and purchased at a shop."""

    card_choices = stats.get(
        "card_choices",
        []
    )

    cards_gained = stats.get(
        "cards_gained",
        []
    )

    offered_cards: list[str] = []

    for choice in card_choices:
        card = choice.get(
            "card",
            {}
        )

        card_id = card.get("id")

        if card_id is None:
            continue

        offered_cards.append(card_id)

    purchased_cards: list[str] = []

    for card in cards_gained:
        card_id = card.get("id")

        if card_id is None:
            continue

        purchased_cards.append(card_id)

        acquisitions.append(
            CardAcquisition(
                card=card_id,
                source="shop",
                act=act,
                floor=floor,
                act_floor=act_floor,
                upgraded=(
                    card.get(
                        "current_upgrade_level",
                        0,
                    )
                    > 0
                ),
            )
        )

    if not offered_cards and not purchased_cards:
        return

    rewards.append(
        CardReward(
            source="shop",
            act=act,
            floor=floor,
            act_floor=act_floor,
            offered_cards=(
                offered_cards + purchased_cards
            ),
            picked_cards=purchased_cards,
        )
    )


def parse_upgrades(
    stats: dict,
    source: str,
    act: int,
    floor: int,
    act_floor: int,
    upgrades: list[CardUpgrade],
) -> None:
    """Parse cards upgraded at a map point."""

    for card in stats.get(
        "upgraded_cards",
        [],
    ):
        upgrades.append(
            CardUpgrade(
                card=card,
                source=source,
                act=act,
                floor=floor,
                act_floor=act_floor,
            )
        )


def parse_transformations(
    stats: dict,
    source: str,
    act: int,
    floor: int,
    act_floor: int,
    transformations: list[CardTransformation],
) -> None:
    """Parse card transformations."""

    for transformation in stats.get(
        "cards_transformed",
        [],
    ):
        original_card = transformation.get(
            "original_card",
            {}
        )

        final_card = transformation.get(
            "final_card",
            {}
        )

        original_id = original_card.get("id")
        final_id = final_card.get("id")

        if (
            original_id is None
            or final_id is None
        ):
            continue

        transformations.append(
            CardTransformation(
                original_card=original_id,
                final_card=final_id,
                source=source,
                act=act,
                floor=floor,
                act_floor=act_floor,
            )
        )