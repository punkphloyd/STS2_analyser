from dataclasses import dataclass

from data_models.run_data import RunData


@dataclass(slots=True)
class FloorWinProbability:
    """Conditional run win probability for a floor."""

    floor: int
    runs_reached: int
    wins: int

    @property
    def win_probability(self) -> float | None:
        """Return P(win | reached this floor)."""

        if self.runs_reached == 0:
            return None

        return self.wins / self.runs_reached


def calculate_conditional_win_probability(
    runs: list[RunData],
) -> dict[int, FloorWinProbability]:
    """
    Calculate the probability of eventually winning given that
    a run reached each floor.

    Each run contributes to every floor up to and including its
    final reached floor.

    For floor N:

        P(win | reached N) =
            wins among runs reaching N
            -------------------------
            all runs reaching N
    """

    if not runs:
        return {}

    maximum_floor = max(
        run.floor_reached
        for run in runs
    )

    statistics = {
        floor: FloorWinProbability(
            floor=floor,
            runs_reached=0,
            wins=0,
        )
        for floor in range(1, maximum_floor + 1)
    }

    for run in runs:
        for floor in range(
            1,
            run.floor_reached + 1,
        ):
            result = statistics[floor]

            result.runs_reached += 1

            if run.metadata.victory:
                result.wins += 1

    return statistics