from matplotlib.figure import Figure

from analysis.statistics import (
    calculate_win_rate,
    calculate_win_rate_by_character,
    calculate_win_rate_by_ascension,
    calculate_win_rate_by_character_and_ascension,
)
from data_models.run_metadata import RunMetadata


def plot_overall_win_rate(runs: list[RunMetadata]):
    """Create a bar chart showing the overall win rate."""

    win_rate = calculate_win_rate(runs)

    if win_rate is None:
        return None

    figure = Figure(figsize=(6, 4))
    axis = figure.add_subplot(111)

    axis.bar(
        ["Overall"],
        [win_rate * 100]
    )

    axis.set_ylim(0, 100)
    axis.set_ylabel("Win Rate (%)")
    axis.set_title("Overall Win Rate")

    axis.bar_label(
        axis.containers[0],
        fmt="%.1f%%"
    )

    figure.tight_layout()

    return figure

def plot_win_rate_by_character(
    runs: list[RunMetadata],
):
    """Create a bar chart showing win rate by character."""

    win_rates = calculate_win_rate_by_character(runs)

    if not win_rates:
        return None

    figure = Figure(figsize=(8, 4))
    axis = figure.add_subplot(111)

    characters = list(win_rates.keys())
    values = [
        win_rates[character] * 100
        for character in characters
    ]

    axis.bar(
        characters,
        values,
    )

    axis.set_ylim(0, 100)
    axis.set_ylabel("Win Rate (%)")
    axis.set_title("Win Rate by Character")

    axis.bar_label(
        axis.containers[0],
        fmt="%.1f%%",
    )

    figure.tight_layout()

    return figure


def plot_win_rate_by_ascension(
    runs: list[RunMetadata],
):
    """Create a line chart showing win rate by ascension."""

    win_rates = calculate_win_rate_by_ascension(runs)

    if not win_rates:
        return None

    figure = Figure(figsize=(8, 4))
    axis = figure.add_subplot(111)

    ascensions = sorted(win_rates.keys())

    values = [
        win_rates[ascension] * 100
        for ascension in ascensions
    ]

    axis.plot(
        ascensions,
        values,
        marker="o",
    )

    axis.set_ylim(0, 100)
    axis.set_xlabel("Ascension")
    axis.set_ylabel("Win Rate (%)")
    axis.set_title("Win Rate by Ascension")

    figure.tight_layout()

    return figure

def plot_win_rate_by_character_and_ascension(
    runs: list[RunMetadata],
):
    """Create a heatmap showing win rate by character and ascension."""

    win_rates = calculate_win_rate_by_character_and_ascension(runs)

    if not win_rates:
        return None

    characters = sorted(
        {character for character, _ in win_rates}
    )

    ascensions = sorted(
        {ascension for _, ascension in win_rates}
    )

    figure = Figure(figsize=(10, 5))
    axis = figure.add_subplot(111)

    values = [
        [
            (
                win_rates.get((character, ascension), float("nan"))
                * 100
                if (character, ascension) in win_rates
                else float("nan")
            )
            for ascension in ascensions
        ]
        for character in characters
    ]

    image = axis.imshow(
        values,
        vmin=0,
        vmax=100,
        aspect="auto",
    )

    axis.set_xticks(range(len(ascensions)))
    axis.set_xticklabels(ascensions)

    axis.set_yticks(range(len(characters)))
    axis.set_yticklabels(characters)

    axis.set_xlabel("Ascension")
    axis.set_ylabel("Character")
    axis.set_title("Win Rate by Character and Ascension")

    figure.colorbar(
        image,
        ax=axis,
        label="Win Rate (%)",
    )

    for row_index, character in enumerate(characters):
        for column_index, ascension in enumerate(ascensions):

            value = win_rates.get(
                (character, ascension)
            )

            if value is not None:
                axis.text(
                    column_index,
                    row_index,
                    f"{value * 100:.1f}%",
                    ha="center",
                    va="center",
                )

    figure.tight_layout()

    return figure