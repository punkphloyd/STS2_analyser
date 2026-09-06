from datetime import datetime
from pathlib import Path

from analysis.card_timing_analysis import (
    CardAcquisitionTimingStatistics,
    CardChoiceTimingStatistics,
    calculate_card_acquisition_timing_statistics,
    calculate_card_choice_timing_statistics,
)
from data_models.card_acquisition import CardAcquisition
from data_models.card_reward import CardReward
from data_models.run_data import RunData
from data_models.run_metadata import RunMetadata


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
        card_transformations=[],
    )


def make_reward(
    *,
    offered_cards: list[str],
    picked_cards: list[str],
    floor: int = 1,
    act: int = 1,
    act_floor: int | None = None,
    source: str = "monster",
) -> CardReward:
    if act_floor is None:
        act_floor = floor

    return CardReward(
        source=source,
        act=act,
        floor=floor,
        act_floor=act_floor,
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


# ---------------------------------------------------------------------------
# Card acquisition timing
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Card choice timing
# ---------------------------------------------------------------------------


def test_card_choice_timing_empty_runs():
    result = calculate_card_choice_timing_statistics([])

    assert result == {}


def test_card_choice_timing_groups_choices_by_act():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=["CARD.A"],
                picked_cards=["CARD.A"],
                act=1,
                floor=5,
                act_floor=5,
            ),
            make_reward(
                offered_cards=["CARD.A"],
                picked_cards=["CARD.A"],
                act=2,
                floor=20,
                act_floor=3,
            ),
            make_reward(
                offered_cards=["CARD.A"],
                picked_cards=["CARD.A"],
                act=3,
                floor=35,
                act_floor=7,
            ),
        ],
    )

    result = calculate_card_choice_timing_statistics([run])

    assert set(result["CARD.A"]) == {1, 2, 3}

    assert result["CARD.A"][1].offered == 1
    assert result["CARD.A"][2].offered == 1
    assert result["CARD.A"][3].offered == 1


def test_card_choice_timing_uses_act_not_act_floor():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=["CARD.A"],
                picked_cards=["CARD.A"],
                act=1,
                floor=10,
                act_floor=10,
            ),
            make_reward(
                offered_cards=["CARD.A"],
                picked_cards=["CARD.A"],
                act=2,
                floor=11,
                act_floor=1,
            ),
        ],
    )

    result = calculate_card_choice_timing_statistics([run])

    assert set(result["CARD.A"]) == {1, 2}

    assert result["CARD.A"][1].offered == 1
    assert result["CARD.A"][2].offered == 1


def test_card_choice_timing_counts_offers():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                    "CARD.C",
                ],
                picked_cards=[],
                act=1,
            ),
        ],
    )

    result = calculate_card_choice_timing_statistics([run])

    assert result["CARD.A"][1].offered == 1
    assert result["CARD.B"][1].offered == 1
    assert result["CARD.C"][1].offered == 1


def test_card_choice_timing_counts_picks_and_skips():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                ],
                picked_cards=["CARD.A"],
                act=1,
            ),
        ],
    )

    result = calculate_card_choice_timing_statistics([run])

    assert result["CARD.A"][1].picked == 1
    assert result["CARD.A"][1].skipped == 0

    assert result["CARD.B"][1].picked == 0
    assert result["CARD.B"][1].skipped == 1


def test_card_choice_timing_tracks_wins_when_picked():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                    act=1,
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                    act=1,
                ),
            ],
        ),
    ]

    result = calculate_card_choice_timing_statistics(runs)

    stats = result["CARD.A"][1]

    assert stats.picked == 2
    assert stats.wins_when_picked == 1
    assert stats.pick_win_rate == 0.5


def test_card_choice_timing_tracks_wins_when_skipped():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                    act=1,
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                    act=1,
                ),
            ],
        ),
    ]

    result = calculate_card_choice_timing_statistics(runs)

    stats = result["CARD.A"][1]

    assert stats.skipped == 2
    assert stats.wins_when_skipped == 1
    assert stats.skip_win_rate == 0.5


def test_card_choice_timing_calculates_pick_and_skip_rates():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                    act=1,
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                    act=1,
                ),
            ],
        ),
    ]

    result = calculate_card_choice_timing_statistics(runs)

    stats = result["CARD.A"][1]

    assert stats.offered == 2
    assert stats.picked == 1
    assert stats.skipped == 1
    assert stats.pick_rate == 0.5
    assert stats.skip_rate == 0.5


def test_card_choice_timing_calculates_win_rate_difference():
    stat = CardChoiceTimingStatistics(
        offered=10,
        picked=6,
        skipped=4,
        wins_when_picked=4,
        wins_when_skipped=1,
    )

    assert stat.pick_win_rate == 4 / 6
    assert stat.skip_win_rate == 0.25
    assert stat.win_rate_difference == (4 / 6) - 0.25


def test_card_choice_timing_handles_zero_counts():
    stats = CardChoiceTimingStatistics()

    assert stats.pick_rate is None
    assert stats.skip_rate is None
    assert stats.pick_win_rate is None
    assert stats.skip_win_rate is None
    assert stats.win_rate_difference is None


def test_card_choice_timing_keeps_cards_independent():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=["CARD.A", "CARD.B"],
                picked_cards=["CARD.A"],
                act=1,
            ),
            make_reward(
                offered_cards=["CARD.B", "CARD.C"],
                picked_cards=["CARD.C"],
                act=2,
            ),
        ],
    )

    result = calculate_card_choice_timing_statistics([run])

    assert set(result) == {
        "CARD.A",
        "CARD.B",
        "CARD.C",
    }

    assert set(result["CARD.A"]) == {1}
    assert set(result["CARD.B"]) == {1, 2}
    assert set(result["CARD.C"]) == {2}


def test_card_choice_timing_accumulates_multiple_choices_in_same_act():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                    act=1,
                ),
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                    act=1,
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                    act=1,
                ),
            ],
        ),
    ]

    result = calculate_card_choice_timing_statistics(runs)

    stats = result["CARD.A"][1]

    assert stats.offered == 3
    assert stats.picked == 2
    assert stats.skipped == 1
    assert stats.wins_when_picked == 1
    assert stats.wins_when_skipped == 1


def test_card_choice_timing_duplicate_offered_cards_do_not_inflate_counts():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.A",
                    "CARD.B",
                ],
                picked_cards=["CARD.A"],
                act=1,
            ),
        ],
    )

    result = calculate_card_choice_timing_statistics([run])

    assert result["CARD.A"][1].offered == 1
    assert result["CARD.A"][1].picked == 1

    assert result["CARD.B"][1].offered == 1
    assert result["CARD.B"][1].skipped == 1


def test_card_choice_timing_offered_equals_picked_plus_skipped():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                ],
                picked_cards=["CARD.A"],
                act=1,
            ),
        ],
    )

    result = calculate_card_choice_timing_statistics([run])

    for stats in result["CARD.A"].values():
        assert stats.offered == stats.picked + stats.skipped

    for stats in result["CARD.B"].values():
        assert stats.offered == stats.picked + stats.skipped


def test_card_choice_timing_pick_and_skip_rates_sum_to_one():
    stat = CardChoiceTimingStatistics(
        offered=10,
        picked=6,
        skipped=4,
    )

    assert stat.pick_rate + stat.skip_rate == 1.0