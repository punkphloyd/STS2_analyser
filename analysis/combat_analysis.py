from collections import defaultdict
from dataclasses import dataclass

from data_models.run_data import RunData


@dataclass(slots=True)
class EncounterStatistics:
    encounter_type: str
    faced: int
    wins: int
    success_rate: float


def calculate_elite_boss_statistics(
    runs: list[RunData],
) -> dict[str, EncounterStatistics]:
    """Calculate success statistics for elite and boss encounters."""

    encounter_counts: dict[
        str,
        list[bool],
    ] = defaultdict(list)

    encounter_types: dict[
        str,
        str,
    ] = {}

    for run in runs:
        for encounter in run.encounters:

            encounter_counts[
                encounter.encounter
            ].append(
                encounter.current_hp > 0
            )

            encounter_types[
                encounter.encounter
            ] = encounter.encounter_type

    statistics = {}

    for encounter, results in encounter_counts.items():

        faced = len(results)
        wins = sum(results)

        statistics[encounter] = EncounterStatistics(
            encounter_type=encounter_types[encounter],
            faced=faced,
            wins=wins,
            success_rate=wins / faced,
        )

    return statistics