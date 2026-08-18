import json
from pathlib import Path

from data_models.run_data import RunData
from parsers.metadata_parser import parse_metadata
from data_models.death_data import DeathData


def parse_neow_relic_choices(
    data: dict,
) -> tuple[list[str], str | None]:
    """Return the Neow relic choices and selected relic."""

    for map_point_group in data.get("map_point_history", []):
        for map_point in map_point_group:

            rooms = map_point.get("rooms", [])

            if not any(
                room.get("model_id") == "EVENT.NEOW"
                for room in rooms
            ):
                continue

            player_stats = map_point.get("player_stats", [])

            if not player_stats:
                return [], None

            ancient_choices = player_stats[0].get(
                "ancient_choice",
                []
            )

            choices = []
            selected = None

            for choice in ancient_choices:
                relic = choice.get("TextKey")

                if relic is None:
                    continue

                choices.append(relic)

                if choice.get("was_chosen") is True:
                    selected = relic

            return choices, selected

    return [], None


def parse_run(path: Path) -> RunData:
    """Parse a Slay the Spire 2 .run file into a RunData object."""

    with path.open("r", encoding="utf-8") as file:
        data: dict = json.load(file)

    metadata = parse_metadata(path)

    neow_relic_choices, neow_bonus_relic = (
        parse_neow_relic_choices(data)
    )

    floor_reached = parse_floor_reached(data)
    death_data = parse_death_data(data)

    return RunData(
        metadata=metadata,
        floor_reached=floor_reached,
        neow_bonus_relic=neow_bonus_relic,
        neow_relic_choices=neow_relic_choices,
        death_data=death_data,
    )

def parse_death_data(data: dict) -> DeathData | None:
    """Extract death information from a run."""

    if data["win"]:
        return None

    map_point_history = data.get(
        "map_point_history",
        []
    )


    return DeathData(
        killed_by_encounter=data.get(
            "killed_by_encounter"
        ),
        killed_by_event=data.get(
            "killed_by_event"
        ),
    )

def parse_floor_reached(data: dict) -> int:
    map_point_history = data.get(
        "map_point_history",
        []
    )

    return sum(
        len(act)
        for act in map_point_history
    )

def parse_floor_reached(data: dict) -> int:
    """Return the number of map points reached during the run."""

    map_point_history = data.get(
        "map_point_history",
        []
    )

    return sum(
        len(act)
        for act in map_point_history
    )