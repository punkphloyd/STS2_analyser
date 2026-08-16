from dataclasses import dataclass

from data_models.run_data import RunData


@dataclass(slots=True)
class ChoiceStatistics:
    offered: int
    picks: int
    pick_rate: float
    wins: int
    win_rate: float | None


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