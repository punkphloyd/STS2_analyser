import json
from pathlib import Path

from data_models.run_data import RunData
from parsers.metadata_parser import parse_metadata
from data_models.encounter_data import EncounterData
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
    encounters = parse_encounter_data(data)

    return RunData(
        metadata=metadata,
        floor_reached=floor_reached,
        neow_bonus_relic=neow_bonus_relic,
        neow_relic_choices=neow_relic_choices,
        death_data=death_data,
        encounters=encounters
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

def parse_encounter_data(
    data: dict,
) -> list[EncounterData]:
    """Extract combat encounters from a run."""

    encounters = []

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

            map_point_type = map_point.get(
                "map_point_type"
            )

            if map_point_type not in {
                "monster",
                "elite",
                "boss",
            }:
                continue

            rooms = map_point.get(
                "rooms",
                []
            )

            player_stats = map_point.get(
                "player_stats",
                []
            )

            if not player_stats:
                continue

            stats = player_stats[0]

            for room in rooms:

                if room.get("room_type") != map_point_type:
                    continue

                encounter = room.get(
                    "model_id"
                )

                if encounter is None:
                    continue

                encounters.append(
                    EncounterData(
                        encounter=encounter,
                        encounter_type=map_point_type,
                        act=act,
                        floor=floor,
                        act_floor=act_floor,
                        turns_taken=room.get(
                            "turns_taken",
                            0,
                        ),
                        damage_taken=stats.get(
                            "damage_taken",
                            0,
                        ),
                        current_hp=stats.get(
                            "current_hp",
                            0,
                        ),
                        max_hp=stats.get(
                            "max_hp",
                            0,
                        ),
                        hp_healed=stats.get(
                            "hp_healed",
                            0,
                        ),
                        max_hp_gained=stats.get(
                            "max_hp_gained",
                            0,
                        ),
                        max_hp_lost=stats.get(
                            "max_hp_lost",
                            0,
                        ),
                    )
                )

    return encounters