from dataclasses import dataclass
from statistics import median

from analysis.combat_analysis import (
    encounter_won,
    filter_run_encounters,
)
from analysis.encounter_analysis import (
    relic_present_at_encounter,
)
from data_models.encounter_statistics import EncounterStatistics
from data_models.run_data import RunData


@dataclass(slots=True)
class ChoiceStatistics:
    offered: int
    picks: int
    pick_rate: float
    wins: int
    win_rate: float | None


@dataclass(slots=True)
class RelicStatistics:
    runs_acquired: int
    wins: int

    @property
    def win_rate(self) -> float | None:
        if self.runs_acquired == 0:
            return None

        return self.wins / self.runs_acquired


def calculate_neow_relic_statistics(
    runs: list[RunData],
) -> dict[str, ChoiceStatistics]:
    """Calculate pick and win statistics for Neow bonus relics."""

    if not runs:
        return {}

    offered_counts: dict[str, int] = {}
    pick_counts: dict[str, int] = {}
    win_counts: dict[str, int] = {}

    for run in runs:

        for relic in run.neow_relic_choices:
            offered_counts[relic] = (
                offered_counts.get(relic, 0) + 1
            )

        relic = run.neow_bonus_relic

        if relic is None:
            continue

        pick_counts[relic] = (
            pick_counts.get(relic, 0) + 1
        )

        if run.metadata.victory:
            win_counts[relic] = (
                win_counts.get(relic, 0) + 1
            )

    result: dict[str, ChoiceStatistics] = {}

    for relic, offered in offered_counts.items():

        picks = pick_counts.get(relic, 0)
        wins = win_counts.get(relic, 0)

        result[relic] = ChoiceStatistics(
            offered=offered,
            picks=picks,
            pick_rate=picks / offered,
            wins=wins,
            win_rate=(
                wins / picks
                if picks > 0
                else None
            ),
        )

    return result


def calculate_relic_statistics(
    runs: list[RunData],
) -> dict[str, RelicStatistics]:
    """Calculate acquisition and win statistics for relics."""

    if not runs:
        return {}

    acquisition_counts: dict[str, int] = {}
    win_counts: dict[str, int] = {}

    for run in runs:

        acquired_relics = {
            acquisition.relic
            for acquisition in run.relic_acquisitions
        }

        for relic in acquired_relics:

            acquisition_counts[relic] = (
                acquisition_counts.get(relic, 0) + 1
            )

            if run.metadata.victory:
                win_counts[relic] = (
                    win_counts.get(relic, 0) + 1
                )

    result: dict[str, RelicStatistics] = {}

    for relic, runs_acquired in acquisition_counts.items():

        wins = win_counts.get(relic, 0)

        result[relic] = RelicStatistics(
            runs_acquired=runs_acquired,
            wins=wins,
        )

    return result


def calculate_relic_encounter_statistics(
    runs: list[RunData],
    encounter_type: str | None = None,
    encounter_name: str | None = None,
    act: int | None = None,
) -> dict[str, EncounterStatistics]:
    """Calculate encounter statistics for relics present during fights."""

    if not runs:
        return {}

    grouped: dict[str, list] = {}

    run_encounters = filter_run_encounters(
        runs,
        act=act,
        encounter_type=encounter_type,
        encounter_name=encounter_name,
    )

    for run, encounter in run_encounters:

        relics = {
            acquisition.relic
            for acquisition in run.relic_acquisitions
            if relic_present_at_encounter(
                acquisition.relic,
                run,
                encounter,
            )
        }

        for relic in relics:
            grouped.setdefault(
                relic,
                [],
            ).append(encounter)

    result: dict[str, EncounterStatistics] = {}

    for relic, encounters in grouped.items():

        fights = len(encounters)

        wins = sum(
            encounter_won(encounter)
            for encounter in encounters
        )

        damages = [
            encounter.damage_taken
            for encounter in encounters
        ]

        turns = [
            encounter.turns_taken
            for encounter in encounters
        ]

        damage_per_turn = [
            encounter.damage_taken / encounter.turns_taken
            for encounter in encounters
            if encounter.turns_taken > 0
        ]

        result[relic] = EncounterStatistics(
            encounter_type=encounters[0].encounter_type,
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

    return result