from collections import defaultdict
from statistics import median

from data_models.encounter_data import EncounterData
from data_models.encounter_filter import EncounterFilter
from data_models.encounter_statistics import EncounterStatistics
from data_models.run_data import RunData


def encounter_won(encounter: EncounterData) -> bool:
    return encounter.current_hp > 0


def filter_encounters(
    runs: list[RunData],
    encounter_filter: EncounterFilter | None = None,
) -> list[EncounterData]:
    """Return encounters matching the requested filters."""

    encounters = []

    for run in runs:
        for encounter in run.encounters:

            if encounter_filter is not None:

                if (
                    encounter_filter.act is not None
                    and encounter.act != encounter_filter.act
                ):
                    continue

                if (
                    encounter_filter.encounter_type is not None
                    and encounter.encounter_type
                    != encounter_filter.encounter_type
                ):
                    continue

                if (
                    encounter_filter.encounter_name is not None
                    and encounter.encounter
                    != encounter_filter.encounter_name
                ):
                    continue

            encounters.append(encounter)

    return encounters


def filter_run_encounters(
    runs: list[RunData],
    encounter_filter: EncounterFilter | None = None,
) -> list[tuple[RunData, EncounterData]]:
    """Return matching encounters while retaining their parent runs."""

    results = []

    for run in runs:
        for encounter in run.encounters:

            if encounter_filter is not None:

                if (
                    encounter_filter.act is not None
                    and encounter.act != encounter_filter.act
                ):
                    continue

                if (
                    encounter_filter.encounter_type is not None
                    and encounter.encounter_type
                    != encounter_filter.encounter_type
                ):
                    continue

                if (
                    encounter_filter.encounter_name is not None
                    and encounter.encounter
                    != encounter_filter.encounter_name
                ):
                    continue

            results.append(
                (run, encounter)
            )

    return results


def filter_runs_by_encounter(
    runs: list[RunData],
    encounter_filter: EncounterFilter | None = None,
) -> list[RunData]:
    """Return runs containing at least one matching encounter."""

    results = []

    for run in runs:

        for encounter in run.encounters:

            if encounter_filter is not None:

                if (
                    encounter_filter.act is not None
                    and encounter.act != encounter_filter.act
                ):
                    continue

                if (
                    encounter_filter.encounter_type is not None
                    and encounter.encounter_type
                    != encounter_filter.encounter_type
                ):
                    continue

                if (
                    encounter_filter.encounter_name is not None
                    and encounter.encounter
                    != encounter_filter.encounter_name
                ):
                    continue

            results.append(run)
            break

    return results


def get_available_acts(
    runs: list[RunData],
) -> list[int]:
    """Return acts represented by encounters in the supplied runs."""

    acts = {
        encounter.act
        for run in runs
        for encounter in run.encounters
    }

    return sorted(acts)


def get_available_encounter_types(
    runs: list[RunData],
    encounter_filter: EncounterFilter | None = None,
) -> list[str]:
    """Return encounter types matching the supplied filter."""

    encounters = filter_encounters(
        runs,
        encounter_filter=EncounterFilter(
            act=(
                encounter_filter.act
                if encounter_filter is not None
                else None
            ),
        ),
    )

    encounter_types = {
        encounter.encounter_type
        for encounter in encounters
    }

    return sorted(encounter_types)


def get_available_encounters(
    runs: list[RunData],
    encounter_filter: EncounterFilter | None = None,
) -> list[str]:
    """Return encounter names matching the supplied filters."""

    encounters = filter_encounters(
        runs,
        encounter_filter=EncounterFilter(
            act=(
                encounter_filter.act
                if encounter_filter is not None
                else None
            ),
            encounter_type=(
                encounter_filter.encounter_type
                if encounter_filter is not None
                else None
            ),
        ),
    )

    encounter_names = {
        encounter.encounter
        for encounter in encounters
    }

    return sorted(encounter_names)


def calculate_encounter_statistics(
    runs: list[RunData],
    encounter_filter: EncounterFilter | None = None,
) -> dict[str, EncounterStatistics]:
    """Calculate combat statistics for filtered encounters."""

    encounters = filter_encounters(
        runs,
        encounter_filter=encounter_filter,
    )

    grouped: dict[str, list[EncounterData]] = defaultdict(list)

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