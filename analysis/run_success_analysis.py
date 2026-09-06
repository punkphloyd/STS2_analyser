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
    *,
    character: str | None = None,
    ascension: int | None = None,
) -> dict[int, FloorWinProbability]:
    """
    Calculate conditional run win probability by floor.

    For floor N:

        P(win | reached N) =
            wins among runs reaching N
            -------------------------
            all runs reaching N

    Optional character and ascension filters can be used to calculate
    the baseline for a specific character, ascension, or both.

    Examples:

        calculate_conditional_win_probability(runs)

        calculate_conditional_win_probability(
            runs,
            character="Silent",
        )

        calculate_conditional_win_probability(
            runs,
            character="Silent",
            ascension=10,
        )
    """
    filtered_runs = [
        run
        for run in runs
        if (
            character is None
            or run.metadata.character == character
        )
        and (
            ascension is None
            or run.metadata.ascension == ascension
        )
    ]

    if not filtered_runs:
        return {}

    maximum_floor = max(
        run.floor_reached
        for run in filtered_runs
    )

    statistics = {
        floor: FloorWinProbability(
            floor=floor,
            runs_reached=0,
            wins=0,
        )
        for floor in range(1, maximum_floor + 1)
    }

    for run in filtered_runs:
        for floor in range(1, run.floor_reached + 1):
            result = statistics[floor]

            result.runs_reached += 1

            if run.metadata.victory:
                result.wins += 1

    return statistics


def calculate_conditional_win_probability_by_character(
    runs: list[RunData],
) -> dict[str, dict[int, FloorWinProbability]]:
    """
    Calculate conditional run win probability by character and floor.

    Returns:

        {
            "Ironclad": {
                1: FloorWinProbability(...),
                2: FloorWinProbability(...),
                ...
            },
            "Silent": {
                ...
            },
        }

    Only character/floor combinations represented by the supplied runs
    are included.
    """
    characters = {
        run.metadata.character
        for run in runs
    }

    return {
        character: calculate_conditional_win_probability(
            runs,
            character=character,
        )
        for character in sorted(characters)
    }


def calculate_conditional_win_probability_by_character_and_ascension(
    runs: list[RunData],
) -> dict[tuple[str, int], dict[int, FloorWinProbability]]:
    """
    Calculate conditional run win probability by character,
    ascension, and floor.

    Returns:

        {
            ("Ironclad", 0): {
                1: FloorWinProbability(...),
                ...
            },
            ("Ironclad", 10): {
                ...
            },
            ("Silent", 0): {
                ...
            },
        }

    Only character/ascension combinations represented by the supplied
    runs are included.
    """
    combinations = {
        (
            run.metadata.character,
            run.metadata.ascension,
        )
        for run in runs
    }

    return {
        (character, ascension): calculate_conditional_win_probability(
            runs,
            character=character,
            ascension=ascension,
        )
        for character, ascension in sorted(combinations)
    }