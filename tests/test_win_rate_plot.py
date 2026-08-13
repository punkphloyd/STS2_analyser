from datetime import datetime
from pathlib import Path

from data_models.run_metadata import RunMetadata
from plots.win_rate import (
    plot_overall_win_rate,
    plot_win_rate_by_character,
    plot_win_rate_by_ascension,
    plot_win_rate_by_character_and_ascension,
)


def make_run(
    victory: bool,
    character: str = "Ironclad",
    ascension: int = 0,
) -> RunMetadata:
    return RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026, 8, 1),
        character=character,
        ascension=ascension,
        victory=victory,
        game_version="v0.107.1",
        game_mode="standard",
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

def test_plot_win_rate_by_character_and_ascension():

    runs = [
        make_run(True, "Ironclad", 0),
        make_run(False, "Ironclad", 0),
        make_run(False, "Silent", 1),
    ]

    figure = plot_win_rate_by_character_and_ascension(runs)

    assert figure is not None
    assert len(figure.axes) == 2

def test_plot_win_rate_by_character():

    runs = [
        make_run(True),
        make_run(True),
        make_run(False),
        make_run(False),
    ]

    figure = plot_win_rate_by_character(runs)

    assert figure is not None
    assert len(figure.axes) == 1

def test_plot_win_rate_by_ascension():

    runs = [
        make_run(True),
        make_run(True),
        make_run(False),
        make_run(False),
    ]

    figure = plot_win_rate_by_ascension(runs)

    assert figure is not None
    assert len(figure.axes) == 1