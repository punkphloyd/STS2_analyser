from collections import defaultdict
from statistics import median

from data_models.encounter_data import EncounterData
from data_models.encounter_statistics import EncounterStatistics
from data_models.run_data import RunData


def encounter_won(
    encounter: EncounterData,
) -> bool:
    return encounter.current_hp > 0


def calculate_elite_boss_statistics(
    runs: list[RunData],
) -> dict[str, EncounterStatistics]:
    """Calculate success statistics for elite and boss encounters."""

    return {
        encounter: statistics
        for encounter, statistics
        in calculate_encounter_statistics(runs).items()
        if statistics.encounter_type in {
            "elite",
            "boss",
        }
    }


def filter_encounters(
    runs: list[RunData],
    act: int | None = None,
    encounter_type: str | None = None,
    encounter_name: str | None = None,
):
    """Return encounters matching the requested combat filters."""

    encounters = []

    for run in runs:
        for encounter in run.encounters:

            if act is not None and encounter.act != act:
                continue

            if (
                encounter_type is not None
                and encounter.encounter_type != encounter_type
            ):
                continue

            if (
                encounter_name is not None
                and encounter.encounter != encounter_name
            ):
                continue

            encounters.append(encounter)

    return encounters


def calculate_encounter_statistics(
    runs: list[RunData],
    act: int | None = None,
    encounter_type: str | None = None,
    encounter_name: str | None = None,
) -> dict[str, EncounterStatistics]:
    """Calculate combat statistics for filtered encounters."""

    encounters = filter_encounters(
        runs,
        act=act,
        encounter_type=encounter_type,
        encounter_name=encounter_name,
    )

    grouped: dict[str, list] = defaultdict(list)

    for encounter in encounters:
        grouped[encounter.encounter].append(
            encounter
        )

    statistics = {}

    for encounter_name, encounter_list in grouped.items():

        fights = len(encounter_list)

        wins = sum(
            encounter_won(encounter)
            for encounter in encounter_list
        )

        damages = [
            encounter.damage_taken
            for encounter in encounter_list
        ]

        turns = [
            encounter.turns_taken
            for encounter in encounter_list
        ]

        damage_per_turn = [
            encounter.damage_taken / encounter.turns_taken
            for encounter in encounter_list
            if encounter.turns_taken > 0
        ]

        statistics[encounter_name] = EncounterStatistics(
            encounter_type=encounter_list[0].encounter_type,
            fights=fights,
            wins=wins,
            win_rate=wins / fights,
            average_damage=sum(damages) / fights,
            median_damage=median(damages),
            minimum_damage=min(damages),
            maximum_damage=max(damages),
            average_turns=sum(turns) / fights,
            minimum_turns=min(turns),
            maximum_turns=max(turns),
            average_damage_per_turn=(
                sum(damage_per_turn)
                / len(damage_per_turn)
                if damage_per_turn
                else 0
            ),
        )

    return statistics