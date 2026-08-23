from data_models.relic_data import RelicAcquisition


def parse_relic_acquisitions(
    data: dict,
) -> list[RelicAcquisition]:
    """Extract relics acquired during a run."""

    acquisitions = []

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

            source = get_relic_source(
                map_point
            )

            if source is None:
                continue

            relics = extract_acquired_relics(
                map_point,
                source,
            )

            for relic in relics:
                acquisitions.append(
                    RelicAcquisition(
                        relic=relic,
                        source=source,
                        act=act,
                        floor=floor,
                        act_floor=act_floor,
                    )
                )

    return acquisitions


def get_relic_source(
    map_point: dict,
) -> str | None:
    """Determine the source of relics at a map point."""

    map_point_type = map_point.get(
        "map_point_type"
    )

    if map_point_type == "ancient":

        rooms = map_point.get(
            "rooms",
            []
        )

        if any(
            room.get("model_id") == "EVENT.NEOW"
            for room in rooms
        ):
            return "neow"

        return "ancient"

    if map_point_type == "elite":
        return "elite"

    if map_point_type == "treasure":
        return "treasure"

    if map_point_type == "shop":
        return "shop"

    if map_point_type == "rest_site":
        return "rest_site"

    rooms = map_point.get(
        "rooms",
        []
    )

    if any(
        room.get("room_type") == "event"
        for room in rooms
    ):
        return "event"

    return None


def extract_acquired_relics(
    map_point: dict,
    source: str,
) -> list[str]:
    """Extract relics actually acquired at a map point."""

    player_stats = map_point.get(
        "player_stats",
        []
    )

    if not player_stats:
        return []

    stats = player_stats[0]

    if source == "shop":
        return stats.get(
            "bought_relics",
            []
        )

    return [
        choice["choice"]
        for choice in stats.get(
            "relic_choices",
            []
        )
        if choice.get("was_picked") is True
    ]