from datetime import datetime
from pathlib import Path

from analysis.card_analysis import (
    calculate_card_choice_statistics,
    calculate_card_skip_statistics,
    calculate_card_statistics,
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

EXAMPLE_RUNFILES = Path("example_runfiles")


def make_run(
    *,
    victory: bool,
    card_rewards: list[CardReward] | None = None,
    card_acquisitions: list[CardAcquisition] | None = None,
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