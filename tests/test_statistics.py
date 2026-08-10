from datetime import datetime
from pathlib import Path

from data_models.run_metadata import RunMetadata
from analysis.statistics import (
    calculate_win_rate,
    calculate_win_rate_by_character,
    calculate_win_rate_by_ascension,
    calculate_win_rate_by_character_and_ascension,
)


def make_run(
    character: str,
    ascension: int,
    victory: bool,
) -> RunMetadata:
    return RunMetadata(
        file_path=Path("test.run"),
        start_time=datetime(2026, 8, 1),
        character=character,
        ascension=ascension,
        victory=victory,
    )


def test_calculate_win_rate():
    runs = [
        make_run("Ironclad", 0, True),
        make_run("Ironclad", 0, True),
        make_run("Ironclad", 0, False),
        make_run("Ironclad", 0, False),
    ]

    assert calculate_win_rate(runs) == 0.5


def test_calculate_win_rate_all_wins():
    runs = [
        make_run("Ironclad", 0, True),
        make_run("Ironclad", 0, True),
    ]

    assert calculate_win_rate(runs) == 1.0


def test_calculate_win_rate_no_wins():
    runs = [
        make_run("Ironclad", 0, False),
        make_run("Ironclad", 0, False),
    ]

    assert calculate_win_rate(runs) == 0.0


def test_calculate_win_rate_empty():
    assert calculate_win_rate([]) is None


def test_calculate_win_rate_by_character():
    runs = [
        make_run("Ironclad", 0, True),
        make_run("Ironclad", 0, False),
        make_run("Silent", 0, True),
        make_run("Silent", 0, True),
    ]

    result = calculate_win_rate_by_character(runs)

    assert result == {
        "Ironclad": 0.5,
        "Silent": 1.0,
    }


def test_calculate_win_rate_by_ascension():
    runs = [
        make_run("Ironclad", 0, True),
        make_run("Ironclad", 0, False),
        make_run("Silent", 1, True),
        make_run("Silent", 1, True),
        make_run("Defect", 2, False),
    ]

    result = calculate_win_rate_by_ascension(runs)

    assert result == {
        0: 0.5,
        1: 1.0,
        2: 0.0,
    }


def test_calculate_win_rate_by_character_and_ascension():
    runs = [
        make_run("Ironclad", 0, True),
        make_run("Ironclad", 0, False),
        make_run("Ironclad", 1, True),
        make_run("Silent", 0, True),
        make_run("Silent", 1, False),
    ]

    result = calculate_win_rate_by_character_and_ascension(runs)

    assert result == {
        ("Ironclad", 0): 0.5,
        ("Ironclad", 1): 1.0,
        ("Silent", 0): 1.0,
        ("Silent", 1): 0.0,
    }


def test_character_and_ascension_omits_empty_combinations():
    runs = [
        make_run("Ironclad", 0, True),
        make_run("Silent", 1, True),
    ]

    result = calculate_win_rate_by_character_and_ascension(runs)

    assert ("Ironclad", 1) not in result
    assert ("Silent", 0) not in result