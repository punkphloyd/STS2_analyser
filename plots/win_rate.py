from matplotlib.figure import Figure

from data_models.run_metadata import RunMetadata
from analysis.statistics import calculate_win_rate


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