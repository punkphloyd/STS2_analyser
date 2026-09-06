from datetime import datetime
from pathlib import Path

from analysis.run_success_analysis import (
    FloorWinProbability,
    calculate_conditional_win_probability,
    calculate_conditional_win_probability_by_character,
    calculate_conditional_win_probability_by_character_and_ascension,
)
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata


def make_run(
    *,
    victory: bool,
    floor_reached: int,
    character: str = "Silent",
    ascension: int = 0,
) -> RunData:
    return RunData(
        metadata=RunMetadata(
            file_path=Path("test.run"),
            start_time=datetime(2026, 8, 1),
            character=character,
            ascension=ascension,
            victory=victory,
            game_version="v0.107.1",
            game_mode="standard",
            multiplayer=False,
        ),
        floor_reached=floor_reached,
    )


def test_floor_win_probability_returns_none_with_no_runs():
    statistics = FloorWinProbability(
        floor=10,
        runs_reached=0,
        wins=0,
    )

    assert statistics.win_probability is None


def test_floor_win_probability_returns_win_rate():
    statistics = FloorWinProbability(
        floor=10,
        runs_reached=4,
        wins=3,
    )

    assert statistics.win_probability == 0.75


def test_conditional_win_probability_empty_runs():
    result = calculate_conditional_win_probability([])

    assert result == {}


def test_conditional_win_probability_counts_runs_reaching_each_floor():
    runs = [
        make_run(victory=True, floor_reached=10),
        make_run(victory=False, floor_reached=10),
        make_run(victory=True, floor_reached=5),
        make_run(victory=False, floor_reached=3),
    ]

    result = calculate_conditional_win_probability(runs)

    assert result[3].runs_reached == 4
    assert result[3].wins == 2
    assert result[3].win_probability == 0.5

    assert result[5].runs_reached == 3
    assert result[5].wins == 2
    assert result[5].win_probability == 2 / 3

    assert result[10].runs_reached == 2
    assert result[10].wins == 1
    assert result[10].win_probability == 0.5


def test_conditional_win_probability_includes_run_at_final_floor():
    runs = [
        make_run(victory=True, floor_reached=5),
    ]

    result = calculate_conditional_win_probability(runs)

    assert result[5].runs_reached == 1
    assert result[5].wins == 1
    assert result[5].win_probability == 1.0

    assert 6 not in result


def test_conditional_win_probability_counts_wins_only_after_reaching_floor():
    runs = [
        make_run(victory=True, floor_reached=10),
        make_run(victory=False, floor_reached=5),
    ]

    result = calculate_conditional_win_probability(runs)

    assert result[5].runs_reached == 2
    assert result[5].wins == 1

    assert result[10].runs_reached == 1
    assert result[10].wins == 1


def test_conditional_win_probability_counts_every_floor_for_long_run():
    runs = [
        make_run(victory=True, floor_reached=5),
    ]

    result = calculate_conditional_win_probability(runs)

    assert set(result) == {1, 2, 3, 4, 5}

    for floor in range(1, 6):
        assert result[floor].floor == floor
        assert result[floor].runs_reached == 1
        assert result[floor].wins == 1
        assert result[floor].win_probability == 1.0


def test_conditional_win_probability_does_not_count_run_beyond_final_floor():
    runs = [
        make_run(victory=False, floor_reached=3),
    ]

    result = calculate_conditional_win_probability(runs)

    assert set(result) == {1, 2, 3}

    for floor in range(1, 4):
        assert result[floor].runs_reached == 1
        assert result[floor].wins == 0
        assert result[floor].win_probability == 0.0


def test_conditional_win_probability_mixes_runs_with_different_floor_reached():
    runs = [
        make_run(victory=True, floor_reached=10),
        make_run(victory=False, floor_reached=7),
        make_run(victory=True, floor_reached=5),
        make_run(victory=False, floor_reached=3),
    ]

    result = calculate_conditional_win_probability(runs)

    assert result[3].runs_reached == 4
    assert result[3].wins == 2
    assert result[3].win_probability == 0.5

    assert result[5].runs_reached == 3
    assert result[5].wins == 2
    assert result[5].win_probability == 2 / 3

    assert result[7].runs_reached == 2
    assert result[7].wins == 1
    assert result[7].win_probability == 0.5

    assert result[10].runs_reached == 1
    assert result[10].wins == 1
    assert result[10].win_probability == 1.0


def test_conditional_win_probability_returns_statistics_for_every_floor():
    runs = [
        make_run(victory=True, floor_reached=10),
        make_run(victory=False, floor_reached=5),
    ]

    result = calculate_conditional_win_probability(runs)

    assert set(result) == set(range(1, 11))


def test_conditional_win_probability_uses_highest_floor_reached():
    runs = [
        make_run(victory=False, floor_reached=7),
        make_run(victory=True, floor_reached=12),
    ]

    result = calculate_conditional_win_probability(runs)

    assert max(result) == 12
    assert 13 not in result


def test_conditional_win_probability_filters_by_character():
    runs = [
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
        ),
        make_run(
            victory=False,
            floor_reached=10,
            character="Silent",
        ),
        make_run(
            victory=False,
            floor_reached=10,
            character="Ironclad",
        ),
    ]

    result = calculate_conditional_win_probability(
        runs,
        character="Silent",
    )

    assert result[10].runs_reached == 2
    assert result[10].wins == 1
    assert result[10].win_probability == 0.5


def test_conditional_win_probability_filters_by_ascension():
    runs = [
        make_run(
            victory=True,
            floor_reached=10,
            ascension=0,
        ),
        make_run(
            victory=False,
            floor_reached=10,
            ascension=0,
        ),
        make_run(
            victory=True,
            floor_reached=10,
            ascension=10,
        ),
        make_run(
            victory=True,
            floor_reached=10,
            ascension=10,
        ),
        make_run(
            victory=False,
            floor_reached=10,
            ascension=10,
        ),
    ]

    result = calculate_conditional_win_probability(
        runs,
        ascension=10,
    )

    assert result[10].runs_reached == 3
    assert result[10].wins == 2
    assert result[10].win_probability == 2 / 3


def test_conditional_win_probability_filters_by_character_and_ascension():
    runs = [
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
            ascension=10,
        ),
        make_run(
            victory=False,
            floor_reached=10,
            character="Silent",
            ascension=10,
        ),
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
            ascension=5,
        ),
        make_run(
            victory=True,
            floor_reached=10,
            character="Ironclad",
            ascension=10,
        ),
    ]

    result = calculate_conditional_win_probability(
        runs,
        character="Silent",
        ascension=10,
    )

    assert result[10].runs_reached == 2
    assert result[10].wins == 1
    assert result[10].win_probability == 0.5


def test_conditional_win_probability_filter_with_no_matching_runs():
    runs = [
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
            ascension=0,
        ),
    ]

    result = calculate_conditional_win_probability(
        runs,
        character="Defect",
    )

    assert result == {}


def test_conditional_win_probability_by_character():
    runs = [
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
        ),
        make_run(
            victory=False,
            floor_reached=10,
            character="Silent",
        ),
        make_run(
            victory=True,
            floor_reached=5,
            character="Ironclad",
        ),
        make_run(
            victory=False,
            floor_reached=5,
            character="Ironclad",
        ),
    ]

    result = calculate_conditional_win_probability_by_character(runs)

    assert set(result) == {"Silent", "Ironclad"}

    assert result["Silent"][10].runs_reached == 2
    assert result["Silent"][10].wins == 1
    assert result["Silent"][10].win_probability == 0.5

    assert result["Ironclad"][5].runs_reached == 2
    assert result["Ironclad"][5].wins == 1
    assert result["Ironclad"][5].win_probability == 0.5

    assert 6 not in result["Ironclad"]


def test_conditional_win_probability_by_character_and_ascension():
    runs = [
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
            ascension=0,
        ),
        make_run(
            victory=False,
            floor_reached=10,
            character="Silent",
            ascension=0,
        ),
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
            ascension=10,
        ),
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
            ascension=10,
        ),
        make_run(
            victory=False,
            floor_reached=10,
            character="Ironclad",
            ascension=10,
        ),
    ]

    result = calculate_conditional_win_probability_by_character_and_ascension(
        runs
    )

    assert set(result) == {
        ("Silent", 0),
        ("Silent", 10),
        ("Ironclad", 10),
    }

    assert result[("Silent", 0)][10].runs_reached == 2
    assert result[("Silent", 0)][10].wins == 1
    assert result[("Silent", 0)][10].win_probability == 0.5

    assert result[("Silent", 10)][10].runs_reached == 2
    assert result[("Silent", 10)][10].wins == 2
    assert result[("Silent", 10)][10].win_probability == 1.0


def test_conditional_win_probability_by_character_omits_empty_combinations():
    runs = [
        make_run(
            victory=True,
            floor_reached=10,
            character="Silent",
            ascension=0,
        ),
        make_run(
            victory=True,
            floor_reached=10,
            character="Ironclad",
            ascension=5,
        ),
    ]

    result = calculate_conditional_win_probability_by_character_and_ascension(
        runs
    )

    assert set(result) == {
        ("Silent", 0),
        ("Ironclad", 5),
    }

    assert ("Silent", 5) not in result
    assert ("Ironclad", 0) not in result