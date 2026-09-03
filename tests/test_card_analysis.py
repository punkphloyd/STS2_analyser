from datetime import datetime
from pathlib import Path

from analysis.card_analysis import (
    CardAcquisitionSourceStatistics,
    CardChoiceStatistics,
    CardCopyCountStatistics,
    CardFinalCopyCountStatistics,
    CardSkipStatistics,
    CardStatistics,
    calculate_card_acquisition_source_statistics,
    calculate_card_choice_statistics,
    calculate_card_copy_count_statistics,
    calculate_card_final_copy_count_statistics,
    calculate_card_skip_statistics,
    calculate_card_statistics,
    calculate_card_correlation,
    calculate_all_card_correlations,
    CardAcquisitionTimingStatistics,
    calculate_card_acquisition_timing_statistics,
)
from data_models.card_acquisition import CardAcquisition
from data_models.card_reward import CardReward
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata
from parsers.run_parser import parse_run
from analysis.card_analysis import (
    CardAcquisitionSourceStatistics,
    calculate_card_acquisition_source_statistics,
)
from data_models.card_transformation import CardTransformation
EXAMPLE_RUNFILES = Path("example_runfiles")


def make_run(
    *,
    victory: bool,
    card_rewards: list[CardReward] | None = None,
    card_acquisitions: list[CardAcquisition] | None = None,
    card_transformations: list[CardTransformation] | None = None,
) -> RunData:
    return RunData(
        metadata=RunMetadata(
            file_path=Path("test.run"),
            start_time=datetime(2026, 8, 1),
            character="Silent",
            ascension=0,
            victory=victory,
            game_version="v0.107.1",
            game_mode="standard",
            multiplayer=False,
        ),
        floor_reached=30,
        card_rewards=(
            card_rewards
            if card_rewards is not None
            else []
        ),
        card_acquisitions=(
            card_acquisitions
            if card_acquisitions is not None
            else []
        ),
        card_transformations=(
            card_transformations
            if card_transformations is not None
            else []
        ),
    )


def make_reward(
    *,
    offered_cards: list[str],
    picked_cards: list[str],
    floor: int = 1,
    source: str = "monster",
) -> CardReward:
    return CardReward(
        source=source,
        act=1,
        floor=floor,
        act_floor=floor,
        offered_cards=offered_cards,
        picked_cards=picked_cards,
    )


def make_acquisition(
    card: str,
    floor: int = 1,
    source: str = "monster",
) -> CardAcquisition:
    return CardAcquisition(
        card=card,
        source=source,
        act=1,
        floor=floor,
        act_floor=floor,
    )


def test_card_choice_statistics():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                    ],
                    picked_cards=[
                        "CARD.A",
                    ],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.C",
                    ],
                    picked_cards=[
                        "CARD.A",
                    ],
                ),
            ],
        ),
    ]

    result = calculate_card_choice_statistics(runs)

    assert result["CARD.A"].offered == 2
    assert result["CARD.A"].picks == 2
    assert result["CARD.A"].pick_rate == 1.0
    assert result["CARD.A"].wins == 1
    assert result["CARD.A"].win_rate == 0.5

    assert result["CARD.B"].offered == 1
    assert result["CARD.B"].picks == 0
    assert result["CARD.B"].pick_rate == 0.0
    assert result["CARD.B"].wins == 0
    assert result["CARD.B"].win_rate is None

    assert result["CARD.C"].offered == 1
    assert result["CARD.C"].picks == 0
    assert result["CARD.C"].pick_rate == 0.0
    assert result["CARD.C"].wins == 0
    assert result["CARD.C"].win_rate is None


def test_card_choice_statistics_empty_runs():
    assert calculate_card_choice_statistics([]) == {}


def test_card_statistics_counts_a_card_once_per_run():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[
                make_acquisition("CARD.A", floor=3),
                make_acquisition("CARD.A", floor=7),
            ],
        ),
        make_run(
            victory=False,
            card_acquisitions=[
                make_acquisition("CARD.A", floor=4),
            ],
        ),
    ]

    result = calculate_card_statistics(runs)

    assert result["CARD.A"].runs_acquired == 2
    assert result["CARD.A"].wins == 1
    assert result["CARD.A"].win_rate == 0.5


def test_card_statistics_distinguishes_cards():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[
                make_acquisition("CARD.A"),
                make_acquisition("CARD.B"),
            ],
        ),
        make_run(
            victory=False,
            card_acquisitions=[
                make_acquisition("CARD.A"),
            ],
        ),
    ]

    result = calculate_card_statistics(runs)

    assert result["CARD.A"].runs_acquired == 2
    assert result["CARD.A"].wins == 1
    assert result["CARD.A"].win_rate == 0.5

    assert result["CARD.B"].runs_acquired == 1
    assert result["CARD.B"].wins == 1
    assert result["CARD.B"].win_rate == 1.0


def test_card_statistics_empty_runs():
    assert calculate_card_statistics([]) == {}


def test_card_skip_statistics():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                    ],
                    picked_cards=[
                        "CARD.A",
                    ],
                    floor=1,
                ),
                make_reward(
                    offered_cards=[
                        "CARD.C",
                        "CARD.D",
                    ],
                    picked_cards=[],
                    floor=2,
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.E",
                        "CARD.F",
                    ],
                    picked_cards=[],
                    floor=1,
                ),
                make_reward(
                    offered_cards=[
                        "CARD.G",
                        "CARD.H",
                    ],
                    picked_cards=[
                        "CARD.G",
                    ],
                    floor=2,
                ),
            ],
        ),
    ]

    result = calculate_card_skip_statistics(runs)

    assert result.rewards == 4
    assert result.skipped == 2
    assert result.skip_rate == 0.5

    assert result.winning_rewards == 2
    assert result.winning_skips == 1
    assert result.winning_skip_rate == 0.5

    assert result.losing_rewards == 2
    assert result.losing_skips == 1
    assert result.losing_skip_rate == 0.5


def test_card_skip_statistics_all_rewards_picked():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                    ],
                    picked_cards=[
                        "CARD.A",
                    ],
                ),
                make_reward(
                    offered_cards=[
                        "CARD.C",
                        "CARD.D",
                    ],
                    picked_cards=[
                        "CARD.D",
                    ],
                ),
            ],
        ),
    ]

    result = calculate_card_skip_statistics(runs)

    assert result.rewards == 2
    assert result.skipped == 0
    assert result.skip_rate == 0.0

    assert result.winning_rewards == 2
    assert result.winning_skips == 0
    assert result.winning_skip_rate == 0.0

    assert result.losing_rewards == 0
    assert result.losing_skips == 0
    assert result.losing_skip_rate is None


def test_card_skip_statistics_all_rewards_skipped():
    runs = [
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                    ],
                    picked_cards=[],
                ),
                make_reward(
                    offered_cards=[
                        "CARD.C",
                        "CARD.D",
                    ],
                    picked_cards=[],
                ),
            ],
        ),
    ]

    result = calculate_card_skip_statistics(runs)

    assert result.rewards == 2
    assert result.skipped == 2
    assert result.skip_rate == 1.0

    assert result.winning_rewards == 0
    assert result.winning_skips == 0
    assert result.winning_skip_rate is None

    assert result.losing_rewards == 2
    assert result.losing_skips == 2
    assert result.losing_skip_rate == 1.0


def test_card_skip_statistics_empty_runs():
    result = calculate_card_skip_statistics([])

    assert result.rewards == 0
    assert result.skipped == 0
    assert result.skip_rate == 0

    assert result.winning_rewards == 0
    assert result.winning_skips == 0
    assert result.winning_skip_rate is None

    assert result.losing_rewards == 0
    assert result.losing_skips == 0
    assert result.losing_skip_rate is None


def test_real_run_card_choice_statistics():
    path = EXAMPLE_RUNFILES / "1780143874.run"

    run = parse_run(path)

    result = calculate_card_choice_statistics([run])

    cloak = result["CARD.CLOAK_AND_DAGGER"]

    assert cloak.offered == 1
    assert cloak.picks == 1
    assert cloak.pick_rate == 1.0


def test_real_run_skipped_reward_is_counted():
    path = EXAMPLE_RUNFILES / "1780143874.run"

    run = parse_run(path)

    result = calculate_card_skip_statistics([run])

    floor_25_reward = next(
        reward
        for reward in run.card_rewards
        if reward.floor == 25
    )

    assert floor_25_reward.picked_cards == []

    assert result.skipped >= 1
    assert result.rewards >= result.skipped


def test_real_run_card_acquisition_statistics():
    path = EXAMPLE_RUNFILES / "1780143874.run"

    run = parse_run(path)

    result = calculate_card_statistics([run])

    assert "CARD.CLOAK_AND_DAGGER" in result

    cloak = result["CARD.CLOAK_AND_DAGGER"]

    assert cloak.runs_acquired == 1

    if run.metadata.victory:
        assert cloak.wins == 1
        assert cloak.win_rate == 1.0
    else:
        assert cloak.wins == 0
        assert cloak.win_rate == 0.0

def test_card_acquisition_source_statistics_empty_runs():
    result = calculate_card_acquisition_source_statistics([])

    assert result == {}


def test_card_acquisition_source_statistics_single_acquisition():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
        ],
    )

    result = calculate_card_acquisition_source_statistics(
        [run]
    )

    assert result == {
        "CARD.CLOAK_AND_DAGGER": {
            "monster": CardAcquisitionSourceStatistics(
                acquisitions=1,
                runs_acquired=1,
                wins=1,
            ),
        },
    }


def test_card_acquisition_source_statistics_multiple_copies_same_source():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=6,
                source="monster",
            ),
        ],
    )

    result = calculate_card_acquisition_source_statistics(
        [run]
    )

    stats = result[
        "CARD.CLOAK_AND_DAGGER"
    ]["monster"]

    assert stats.acquisitions == 2
    assert stats.runs_acquired == 1
    assert stats.wins == 1
    assert stats.win_rate == 1.0


def test_card_acquisition_source_statistics_same_card_multiple_sources():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=5,
                source="shop",
            ),
        ],
    )

    result = calculate_card_acquisition_source_statistics(
        [run]
    )

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ]["monster"] == CardAcquisitionSourceStatistics(
        acquisitions=1,
        runs_acquired=1,
        wins=1,
    )

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ]["shop"] == CardAcquisitionSourceStatistics(
        acquisitions=1,
        runs_acquired=1,
        wins=1,
    )


def test_card_acquisition_source_statistics_multiple_runs():
    winning_run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
        ],
    )

    losing_run = make_run(
        victory=False,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=4,
                source="monster",
            ),
        ],
    )

    result = calculate_card_acquisition_source_statistics(
        [
            winning_run,
            losing_run,
        ]
    )

    stats = result[
        "CARD.CLOAK_AND_DAGGER"
    ]["monster"]

    assert stats.acquisitions == 2
    assert stats.runs_acquired == 2
    assert stats.wins == 1
    assert stats.win_rate == 0.5


def test_card_acquisition_source_statistics_multiple_copies_count_one_win():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="shop",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="shop",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="shop",
            ),
        ],
    )

    result = calculate_card_acquisition_source_statistics(
        [run]
    )

    stats = result[
        "CARD.CLOAK_AND_DAGGER"
    ]["shop"]

    assert stats.acquisitions == 3
    assert stats.runs_acquired == 1
    assert stats.wins == 1


def test_card_acquisition_source_statistics_same_card_source_across_runs():
    first_run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=5,
                source="monster",
            ),
        ],
    )

    second_run = make_run(
        victory=False,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=4,
                source="monster",
            ),
        ],
    )

    result = calculate_card_acquisition_source_statistics(
        [
            first_run,
            second_run,
        ]
    )

    stats = result[
        "CARD.CLOAK_AND_DAGGER"
    ]["monster"]

    assert stats.acquisitions == 3
    assert stats.runs_acquired == 2
    assert stats.wins == 1
    assert stats.win_rate == 0.5


def test_card_acquisition_source_statistics_keeps_cards_independent():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.DEADLY_POISON",
                floor=4,
                source="shop",
            ),
        ],
    )

    result = calculate_card_acquisition_source_statistics(
        [run]
    )

    assert set(result) == {
        "CARD.CLOAK_AND_DAGGER",
        "CARD.DEADLY_POISON",
    }

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ]["monster"].acquisitions == 1

    assert result[
        "CARD.DEADLY_POISON"
    ]["shop"].acquisitions == 1


def test_card_copy_count_statistics_empty_runs():
    result = calculate_card_copy_count_statistics([])

    assert result == {}


def test_card_copy_count_statistics_one_copy():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics([run])

    assert result == {
        "CARD.CLOAK_AND_DAGGER": {
            1: CardCopyCountStatistics(
                runs=1,
                wins=1,
            ),
        },
    }


def test_card_copy_count_statistics_two_copies():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=7,
                source="shop",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics([run])

    assert result == {
        "CARD.CLOAK_AND_DAGGER": {
            2: CardCopyCountStatistics(
                runs=1,
                wins=1,
            ),
        },
    }


def test_card_copy_count_statistics_multiple_runs_same_copy_count():
    winning_run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
        ],
    )

    losing_run = make_run(
        victory=False,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=5,
                source="shop",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics(
        [
            winning_run,
            losing_run,
        ]
    )

    stats = result[
        "CARD.CLOAK_AND_DAGGER"
    ][1]

    assert stats.runs == 2
    assert stats.wins == 1
    assert stats.win_rate == 0.5


def test_card_copy_count_statistics_separates_copy_counts():
    one_copy_run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
        ],
    )

    two_copy_run = make_run(
        victory=False,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=6,
                source="shop",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics(
        [
            one_copy_run,
            two_copy_run,
        ]
    )

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ][1] == CardCopyCountStatistics(
        runs=1,
        wins=1,
    )

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ][2] == CardCopyCountStatistics(
        runs=1,
        wins=0,
    )


def test_card_copy_count_statistics_three_copies():
    run = make_run(
        victory=False,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=5,
                source="shop",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=9,
                source="monster",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics([run])

    stats = result[
        "CARD.CLOAK_AND_DAGGER"
    ][3]

    assert stats.runs == 1
    assert stats.wins == 0
    assert stats.win_rate == 0.0


def test_card_copy_count_statistics_multiple_cards():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=5,
                source="shop",
            ),
            make_acquisition(
                "CARD.DEADLY_POISON",
                floor=7,
                source="monster",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics([run])

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ][2] == CardCopyCountStatistics(
        runs=1,
        wins=1,
    )

    assert result[
        "CARD.DEADLY_POISON"
    ][1] == CardCopyCountStatistics(
        runs=1,
        wins=1,
    )


def test_card_copy_count_statistics_counts_copies_regardless_of_source():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=4,
                source="shop",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=6,
                source="event",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics([run])

    assert 3 in result[
        "CARD.CLOAK_AND_DAGGER"
    ]

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ][3].runs == 1


def test_card_copy_count_statistics_one_run_only_contributes_once():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=3,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=4,
                source="monster",
            ),
            make_acquisition(
                "CARD.CLOAK_AND_DAGGER",
                floor=5,
                source="shop",
            ),
        ],
    )

    result = calculate_card_copy_count_statistics([run])

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ][3].runs == 1

    assert result[
        "CARD.CLOAK_AND_DAGGER"
    ][3].wins == 1

def test_card_final_copy_count_statistics_uses_final_card_state_after_transformation():
    run = make_run(
        victory=True,
        card_transformations=[
            CardTransformation(
                original_card="CARD.STRIKE_SILENT",
                final_card="CARD.BASH",
                source="transform",
                act=1,
                floor=3,
                act_floor=3,
            ),
        ],
    )

    result = calculate_card_final_copy_count_statistics([run])

    assert result[
        "CARD.STRIKE_SILENT"
    ][4] == CardFinalCopyCountStatistics(
        card="CARD.STRIKE_SILENT",
        copy_count=4,
        runs=1,
        wins=1,
        losses=0,
    )

    assert result[
        "CARD.BASH"
    ][1] == CardFinalCopyCountStatistics(
        card="CARD.BASH",
        copy_count=1,
        runs=1,
        wins=1,
        losses=0,
    )

def test_card_final_copy_count_statistics_real_run():
    path = (
        Path("example_runfiles")
        / "1780143874.run"
    )

    run = parse_run(path)

    result = calculate_card_final_copy_count_statistics(
        [run],
    )

    assert result[
        "CARD.DAGGER_THROW"
    ][2] == CardFinalCopyCountStatistics(
        card="CARD.DAGGER_THROW",
        copy_count=2,
        runs=1,
        wins=0,
        losses=1,
    )

    assert result[
        "CARD.ACROBATICS"
    ][2] == CardFinalCopyCountStatistics(
        card="CARD.ACROBATICS",
        copy_count=2,
        runs=1,
        wins=0,
        losses=1,
    )

def test_card_correlation_counts_runs_with_and_without_card():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[make_acquisition("CARD.A")],
        ),
        make_run(
            victory=False,
            card_acquisitions=[make_acquisition("CARD.A")],
        ),
        make_run(victory=True),
        make_run(victory=False),
    ]

    result = calculate_card_correlation("CARD.A", runs)

    assert result.runs_with_card == 2
    assert result.wins_with_card == 1
    assert result.win_rate_with_card == 0.5

    assert result.runs_without_card == 2
    assert result.wins_without_card == 1
    assert result.win_rate_without_card == 0.5

def test_card_correlation_counts_run_once_when_card_has_multiple_copies():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[
                make_acquisition("CARD.A"),
                make_acquisition("CARD.A"),
            ],
        ),
        make_run(victory=False),
    ]

    result = calculate_card_correlation("CARD.A", runs)

    assert result.runs_with_card == 1
    assert result.wins_with_card == 1
    assert result.runs_without_card == 1
    assert result.wins_without_card == 0

def test_card_correlation_returns_none_when_no_runs_contain_card():
    runs = [
        make_run(victory=True),
        make_run(victory=False),
    ]

    result = calculate_card_correlation("CARD.A", runs)

    assert result.win_rate_with_card is None
    assert result.win_rate_without_card == 0.5

def test_card_correlation_returns_none_when_all_runs_contain_card():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[make_acquisition("CARD.A")],
        ),
        make_run(
            victory=False,
            card_acquisitions=[make_acquisition("CARD.A")],
        ),
    ]

    result = calculate_card_correlation("CARD.A", runs)

    assert result.win_rate_with_card == 0.5
    assert result.win_rate_without_card is None

def test_card_correlation_win_rate_difference():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[make_acquisition("CARD.A")],
        ),
        make_run(
            victory=True,
            card_acquisitions=[make_acquisition("CARD.A")],
        ),
        make_run(
            victory=False,
            card_acquisitions=[make_acquisition("CARD.A")],
        ),
        make_run(victory=False),
        make_run(victory=False),
        make_run(victory=True),
    ]

    result = calculate_card_correlation("CARD.A", runs)

    assert result.win_rate_with_card == 2 / 3
    assert result.win_rate_without_card == 1 / 3
    assert result.win_rate_difference == 1 / 3


def test_all_card_correlations():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[
                make_acquisition("CARD.A"),
            ],
        ),
        make_run(
            victory=False,
            card_acquisitions=[
                make_acquisition("CARD.A"),
                make_acquisition("CARD.B"),
            ],
        ),
        make_run(
            victory=True,
            card_acquisitions=[
                make_acquisition("CARD.B"),
            ],
        ),
        make_run(victory=False),
    ]

    result = calculate_all_card_correlations(runs)

    assert set(result) == {
        "CARD.A",
        "CARD.B",
    }

    assert result["CARD.A"].runs_with_card == 2
    assert result["CARD.A"].wins_with_card == 1
    assert result["CARD.A"].runs_without_card == 2
    assert result["CARD.A"].wins_without_card == 1

    assert result["CARD.B"].runs_with_card == 2
    assert result["CARD.B"].wins_with_card == 1
    assert result["CARD.B"].runs_without_card == 2
    assert result["CARD.B"].wins_without_card == 1

def test_all_card_correlations_empty_runs():
    assert calculate_all_card_correlations([]) == {}

def test_card_acquisition_timing_statistics_empty_runs():
    result = calculate_card_acquisition_timing_statistics([])

    assert result == {}


def test_card_acquisition_timing_statistics_winning_run():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition(
                "CARD.A",
                floor=7,
            ),
        ],
    )

    result = calculate_card_acquisition_timing_statistics([run])

    stats = result["CARD.A"]

    assert stats.winning_runs == 1
    assert stats.losing_runs == 0
    assert stats.average_winning_acquisition_floor == 7
    assert stats.average_losing_acquisition_floor is None
    assert stats.average_acquisition_floor_difference is None


def test_card_acquisition_timing_statistics_losing_run():
    run = make_run(
        victory=False,
        card_acquisitions=[
            make_acquisition(
                "CARD.A",
                floor=12,
            ),
        ],
    )

    result = calculate_card_acquisition_timing_statistics([run])

    stats = result["CARD.A"]

    assert stats.winning_runs == 0
    assert stats.losing_runs == 1
    assert stats.average_winning_acquisition_floor is None
    assert stats.average_losing_acquisition_floor == 12
    assert stats.average_acquisition_floor_difference is None


def test_card_acquisition_timing_statistics_compares_winning_and_losing_runs():
    runs = [
        make_run(
            victory=True,
            card_acquisitions=[
                make_acquisition("CARD.A", floor=6),
            ],
        ),
        make_run(
            victory=True,
            card_acquisitions=[
                make_acquisition("CARD.A", floor=10),
            ],
        ),
        make_run(
            victory=False,
            card_acquisitions=[
                make_acquisition("CARD.A", floor=12),
            ],
        ),
        make_run(
            victory=False,
            card_acquisitions=[
                make_acquisition("CARD.A", floor=16),
            ],
        ),
    ]

    result = calculate_card_acquisition_timing_statistics(runs)

    stats = result["CARD.A"]

    assert stats.winning_runs == 2
    assert stats.losing_runs == 2

    assert stats.average_winning_acquisition_floor == 8
    assert stats.average_losing_acquisition_floor == 14

    assert stats.average_acquisition_floor_difference == -6


def test_card_acquisition_timing_statistics_only_uses_first_copy():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition("CARD.A", floor=5),
            make_acquisition("CARD.A", floor=12),
            make_acquisition("CARD.A", floor=20),
        ],
    )

    result = calculate_card_acquisition_timing_statistics([run])

    stats = result["CARD.A"]

    assert stats.winning_runs == 1
    assert stats.losing_runs == 0
    assert stats.average_winning_acquisition_floor == 5


def test_card_acquisition_timing_statistics_keeps_cards_independent():
    run = make_run(
        victory=True,
        card_acquisitions=[
            make_acquisition("CARD.A", floor=5),
            make_acquisition("CARD.B", floor=15),
        ],
    )

    result = calculate_card_acquisition_timing_statistics([run])

    assert result["CARD.A"].average_winning_acquisition_floor == 5
    assert result["CARD.B"].average_winning_acquisition_floor == 15