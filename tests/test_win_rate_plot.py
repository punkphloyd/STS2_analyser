from datetime import datetime
from pathlib import Path

from data_models.run_metadata import RunMetadata
from plots.win_rate import plot_overall_win_rate


def make_run(victory: bool) -> RunMetadata:
    return RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026, 8, 1),
        character="Ironclad",
        ascension=0,
        victory=victory,
    )


def test_plot_overall_win_rate():

    runs = [
        make_run(True),
        make_run(True),
        make_run(False),
        make_run(False),
    ]

    figure = plot_overall_win_rate(runs)

    assert figure is not None

    axis = figure.axes[0]

    assert axis.patches[0].get_height() == 50