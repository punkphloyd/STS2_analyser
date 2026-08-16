import json
from pathlib import Path

from data_models.run_data import RunData
from parsers.metadata_parser import parse_metadata


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

    return RunData(
        metadata=metadata,
        neow_bonus_relic=neow_bonus_relic,
        neow_relic_choices=neow_relic_choices,
    )