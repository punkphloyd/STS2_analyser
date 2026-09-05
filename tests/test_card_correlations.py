from datetime import datetime
from pathlib import Path

from analysis.card_analysis import (
    CardChoiceContextStatistics,
    calculate_card_choice_context_statistics,
)

from analysis.card_correlations import (
    calculate_card_correlation,
    calculate_card_pick_skip_correlations,
    calculate_all_card_correlations,
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

def test_all_card_correlations_includes_all_acquired_cards():
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
                make_acquisition("CARD.C"),
            ],
        ),
    ]

    result = calculate_all_card_correlations(runs)

    assert set(result) == {
        "CARD.A",
        "CARD.B",
        "CARD.C",
    }

    assert result["CARD.A"].runs_with_card == 1
    assert result["CARD.B"].runs_with_card == 1
    assert result["CARD.C"].runs_with_card == 1

    assert result["CARD.A"].wins_with_card == 1
    assert result["CARD.B"].wins_with_card == 1
    assert result["CARD.C"].wins_with_card == 0

def test_all_card_correlations_empty_runs():
    assert calculate_all_card_correlations([]) == {}

def test_all_card_correlations_card_present_in_every_run():
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
            ],
        ),
    ]

    result = calculate_all_card_correlations(runs)

    stats = result["CARD.A"]

    assert stats.runs_with_card == 2
    assert stats.wins_with_card == 1
    assert stats.win_rate_with_card == 0.5

    assert stats.runs_without_card == 0
    assert stats.wins_without_card == 0
    assert stats.win_rate_without_card is None

def test_card_pick_skip_correlation_empty_runs():
    result = calculate_card_pick_skip_correlations([])

    assert result == {}

def test_card_pick_skip_correlation_counts_picks_and_skips():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                        "CARD.C",
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
                        "CARD.B",
                    ],
                    picked_cards=[
                        "CARD.B",
                    ],
                ),
            ],
        ),
    ]

    result = calculate_card_pick_skip_correlations(runs)

    assert result["CARD.A"].offered == 2
    assert result["CARD.A"].picked == 1
    assert result["CARD.A"].skipped == 1

    assert result["CARD.B"].offered == 2
    assert result["CARD.B"].picked == 1
    assert result["CARD.B"].skipped == 1

    assert result["CARD.C"].offered == 1
    assert result["CARD.C"].picked == 0
    assert result["CARD.C"].skipped == 1

def test_card_pick_skip_correlation_tracks_wins_separately():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                ),
            ],
        ),
    ]

    result = calculate_card_pick_skip_correlations(runs)

    stats = result["CARD.A"]

    assert stats.offered == 4

    assert stats.picked == 2
    assert stats.wins_when_picked == 1
    assert stats.pick_win_rate == 0.5

    assert stats.skipped == 2
    assert stats.wins_when_skipped == 1
    assert stats.skip_win_rate == 0.5

    assert stats.win_rate_difference == 0.0

def test_card_pick_skip_correlation_calculates_win_rate_difference():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                ),
            ],
        ),
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                ),
            ],
        ),
    ]

    result = calculate_card_pick_skip_correlations(runs)

    stats = result["CARD.A"]

    assert stats.picked == 3
    assert stats.wins_when_picked == 2
    assert stats.pick_win_rate == 2 / 3

    assert stats.skipped == 3
    assert stats.wins_when_skipped == 1
    assert stats.skip_win_rate == 1 / 3

    assert stats.win_rate_difference == 1 / 3

def test_card_pick_skip_correlation_counts_each_offer_independently():
    run = make_run(
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
                    "CARD.A",
                    "CARD.C",
                ],
                picked_cards=[
                    "CARD.C",
                ],
            ),
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.D",
                ],
                picked_cards=[
                    "CARD.A",
                ],
            ),
        ],
    )

    result = calculate_card_pick_skip_correlations([run])

    stats = result["CARD.A"]

    assert stats.offered == 3
    assert stats.picked == 2
    assert stats.skipped == 1

    assert stats.wins_when_picked == 2
    assert stats.wins_when_skipped == 1

    assert stats.pick_win_rate == 1.0
    assert stats.skip_win_rate == 1.0
    assert stats.win_rate_difference == 0.0

def test_card_pick_skip_correlation_card_picked_when_other_cards_are_offered():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                    "CARD.C",
                ],
                picked_cards=[
                    "CARD.B",
                ],
            ),
        ],
    )

    result = calculate_card_pick_skip_correlations([run])

    assert result["CARD.A"].picked == 0
    assert result["CARD.A"].skipped == 1

    assert result["CARD.B"].picked == 1
    assert result["CARD.B"].skipped == 0

    assert result["CARD.C"].picked == 0
    assert result["CARD.C"].skipped == 1

def test_card_pick_skip_correlation_skipped_reward_counts_all_offered_cards_as_skipped():
    run = make_run(
        victory=False,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                    "CARD.C",
                ],
                picked_cards=[],
            ),
        ],
    )

    result = calculate_card_pick_skip_correlations([run])

    for card in [
        "CARD.A",
        "CARD.B",
        "CARD.C",
    ]:
        stats = result[card]

        assert stats.offered == 1
        assert stats.picked == 0
        assert stats.skipped == 1

        assert stats.wins_when_picked == 0
        assert stats.wins_when_skipped == 0

        assert stats.pick_win_rate is None
        assert stats.skip_win_rate == 0.0

def test_card_pick_skip_correlation_returns_none_when_never_picked():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=[],
                ),
            ],
        ),
    ]

    result = calculate_card_pick_skip_correlations(runs)

    stats = result["CARD.A"]

    assert stats.picked == 0
    assert stats.wins_when_picked == 0
    assert stats.pick_win_rate is None

    assert stats.skipped == 2
    assert stats.wins_when_skipped == 1
    assert stats.skip_win_rate == 0.5

    assert stats.win_rate_difference is None

def test_card_pick_skip_correlation_returns_none_when_never_skipped():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
    ]

    result = calculate_card_pick_skip_correlations(runs)

    stats = result["CARD.A"]

    assert stats.picked == 2
    assert stats.wins_when_picked == 1
    assert stats.pick_win_rate == 0.5

    assert stats.skipped == 0
    assert stats.wins_when_skipped == 0
    assert stats.skip_win_rate is None

    assert stats.win_rate_difference is None

def test_card_pick_skip_correlation_keeps_cards_independent():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                    ],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                    ],
                    picked_cards=["CARD.B"],
                ),
            ],
        ),
    ]

    result = calculate_card_pick_skip_correlations(runs)

    assert set(result) == {
        "CARD.A",
        "CARD.B",
    }

    assert result["CARD.A"].picked == 1
    assert result["CARD.A"].skipped == 1
    assert result["CARD.A"].wins_when_picked == 1
    assert result["CARD.A"].wins_when_skipped == 0

    assert result["CARD.B"].picked == 1
    assert result["CARD.B"].skipped == 1
    assert result["CARD.B"].wins_when_picked == 0
    assert result["CARD.B"].wins_when_skipped == 1

def test_card_choice_context_statistics_empty_runs():
    result = calculate_card_choice_context_statistics([])

    assert result == {}

def test_card_choice_context_statistics_creates_pairwise_context():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                    "CARD.C",
                ],
                picked_cards=[
                    "CARD.A",
                ],
            ),
        ],
    )

    result = calculate_card_choice_context_statistics([run])

    assert set(result) == {
        "CARD.A",
        "CARD.B",
        "CARD.C",
    }

    assert set(result["CARD.A"]) == {
        "CARD.B",
        "CARD.C",
    }

    assert set(result["CARD.B"]) == {
        "CARD.A",
        "CARD.C",
    }

    assert set(result["CARD.C"]) == {
        "CARD.A",
        "CARD.B",
    }

def test_card_choice_context_statistics_counts_offers():
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
            ),
        ],
    )

    result = calculate_card_choice_context_statistics([run])

    assert result["CARD.A"]["CARD.B"].offered == 1
    assert result["CARD.A"]["CARD.C"].offered == 1

    assert result["CARD.B"]["CARD.A"].offered == 1
    assert result["CARD.B"]["CARD.C"].offered == 1

    assert result["CARD.C"]["CARD.A"].offered == 1
    assert result["CARD.C"]["CARD.B"].offered == 1

def test_card_choice_context_statistics_counts_pick_for_each_competitor():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                    "CARD.C",
                ],
                picked_cards=[
                    "CARD.A",
                ],
            ),
        ],
    )

    result = calculate_card_choice_context_statistics([run])

    assert result["CARD.A"]["CARD.B"].picked == 1
    assert result["CARD.A"]["CARD.C"].picked == 1

    assert result["CARD.B"]["CARD.A"].picked == 0
    assert result["CARD.B"]["CARD.C"].picked == 0

    assert result["CARD.C"]["CARD.A"].picked == 0
    assert result["CARD.C"]["CARD.B"].picked == 0

def test_card_choice_context_statistics_pick_rate():
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
                        "CARD.B",
                    ],
                    picked_cards=[],
                ),
            ],
        ),
    ]

    result = calculate_card_choice_context_statistics(runs)

    stats = result["CARD.A"]["CARD.B"]

    assert stats.offered == 2
    assert stats.picked == 1
    assert stats.pick_rate == 0.5

def test_card_choice_context_statistics_skipped_card_is_not_counted_as_picked():
    run = make_run(
        victory=False,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.B",
                ],
                picked_cards=[
                    "CARD.B",
                ],
            ),
        ],
    )

    result = calculate_card_choice_context_statistics([run])

    assert result["CARD.A"]["CARD.B"].offered == 1
    assert result["CARD.A"]["CARD.B"].picked == 0

    assert result["CARD.B"]["CARD.A"].offered == 1
    assert result["CARD.B"]["CARD.A"].picked == 1

def test_card_choice_context_statistics_keeps_competitors_independent():
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
                    picked_cards=[],
                ),
            ],
        ),
    ]

    result = calculate_card_choice_context_statistics(runs)

    assert result["CARD.A"]["CARD.B"] == (
        CardChoiceContextStatistics(
            offered=1,
            picked=1,
            skipped=0,
            wins_when_picked=1,
            wins_when_skipped=0,
        )
    )

    assert result["CARD.A"]["CARD.C"] == (
        CardChoiceContextStatistics(
            offered=1,
            picked=0,
            skipped=1,
            wins_when_picked=0,
            wins_when_skipped=0,
        )
    )

def test_card_choice_context_statistics_accumulates_multiple_offers():
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
                        "CARD.B",
                    ],
                    picked_cards=[
                        "CARD.B",
                    ],
                ),
            ],
        ),
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
    ]

    result = calculate_card_choice_context_statistics(runs)

    stats = result["CARD.A"]["CARD.B"]

    assert stats.offered == 3
    assert stats.picked == 2
    assert stats.pick_rate == 2 / 3

def test_card_choice_context_statistics_is_directional():
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
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=[
                        "CARD.A",
                        "CARD.B",
                    ],
                    picked_cards=[
                        "CARD.B",
                    ],
                ),
            ],
        ),
    ]

    result = calculate_card_choice_context_statistics(runs)

    assert result["CARD.A"]["CARD.B"].offered == 2
    assert result["CARD.A"]["CARD.B"].picked == 1
    assert result["CARD.A"]["CARD.B"].pick_rate == 0.5

    assert result["CARD.B"]["CARD.A"].offered == 2
    assert result["CARD.B"]["CARD.A"].picked == 1
    assert result["CARD.B"]["CARD.A"].pick_rate == 0.5

def test_card_choice_context_statistics_does_not_create_self_pairs():
    run = make_run(
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
    )

    result = calculate_card_choice_context_statistics([run])

    assert "CARD.A" not in result["CARD.A"]
    assert "CARD.B" not in result["CARD.B"]

def test_card_choice_context_statistics_handles_single_card_offer():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                ],
                picked_cards=[
                    "CARD.A",
                ],
            ),
        ],
    )

    result = calculate_card_choice_context_statistics([run])

    assert result == {}

def test_card_choice_context_statistics_duplicate_offered_cards_do_not_inflate_pairs():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=[
                    "CARD.A",
                    "CARD.A",
                    "CARD.B",
                ],
                picked_cards=[
                    "CARD.A",
                ],
            ),
        ],
    )

    result = calculate_card_choice_context_statistics([run])

    assert result["CARD.A"]["CARD.B"].offered == 1
    assert result["CARD.A"]["CARD.B"].picked == 1

    assert result["CARD.B"]["CARD.A"].offered == 1
    assert result["CARD.B"]["CARD.A"].picked == 0

def test_card_choice_context_tracks_outcomes():
    run_win = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=["A", "B"],
                picked_cards=["A"],
            )
        ],
    )

    run_loss = make_run(
        victory=False,
        card_rewards=[
            make_reward(
                offered_cards=["A", "B"],
                picked_cards=["A"],
            )
        ],
    )

    statistics = calculate_card_choice_context_statistics(
        [run_win, run_loss]
    )

    stat = statistics["A"]["B"]

    assert stat.offered == 2
    assert stat.picked == 2
    assert stat.skipped == 0
    assert stat.wins_when_picked == 1
    assert stat.wins_when_skipped == 0

def test_card_choice_context_tracks_skipped_outcomes():
    run_win = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=["A", "B"],
                picked_cards=["B"],
            )
        ],
    )

    run_loss = make_run(
        victory=False,
        card_rewards=[
            make_reward(
                offered_cards=["A", "B"],
                picked_cards=["B"],
            )
        ],
    )

    statistics = calculate_card_choice_context_statistics(
        [run_win, run_loss]
    )

    stat = statistics["A"]["B"]

    assert stat.offered == 2
    assert stat.picked == 0
    assert stat.skipped == 2
    assert stat.wins_when_picked == 0
    assert stat.wins_when_skipped == 1


def test_card_choice_context_outcome_rates():
    stat = CardChoiceContextStatistics(
        offered=10,
        picked=6,
        skipped=4,
        wins_when_picked=4,
        wins_when_skipped=1,
    )

    assert stat.pick_rate == 0.6
    assert stat.skip_rate == 0.4
    assert stat.pick_win_rate == 4 / 6
    assert stat.skip_win_rate == 0.25
    assert stat.win_rate_difference == (4 / 6) - 0.25


def test_card_choice_context_outcome_rates_handle_zero_counts():
    stat = CardChoiceContextStatistics()

    assert stat.pick_rate is None
    assert stat.skip_rate is None
    assert stat.pick_win_rate is None
    assert stat.skip_win_rate is None
    assert stat.win_rate_difference is None

def test_card_choice_context_offers_equal_picks_plus_skips():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=[],
                ),
            ],
        ),
    ]

    stat = calculate_card_choice_context_statistics(runs)["CARD.A"]["CARD.B"]

    assert stat.offered == stat.picked + stat.skipped


def test_card_choice_context_pick_and_skip_rates_sum_to_one():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=[],
                ),
            ],
        ),
    ]

    stat = calculate_card_choice_context_statistics(runs)["CARD.A"]["CARD.B"]

    assert stat.pick_rate == 0.5
    assert stat.skip_rate == 0.5
    assert stat.pick_rate + stat.skip_rate == 1.0


def test_card_choice_context_only_picks():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=["CARD.A"],
                ),
            ],
        ),
    ]

    stat = calculate_card_choice_context_statistics(runs)["CARD.A"]["CARD.B"]

    assert stat.picked == 2
    assert stat.skipped == 0
    assert stat.pick_win_rate == 0.5
    assert stat.skip_win_rate is None

def test_card_choice_context_only_skips():
    runs = [
        make_run(
            victory=True,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=["CARD.B"],
                ),
            ],
        ),
        make_run(
            victory=False,
            card_rewards=[
                make_reward(
                    offered_cards=["CARD.A", "CARD.B"],
                    picked_cards=["CARD.B"],
                ),
            ],
        ),
    ]

    stat = calculate_card_choice_context_statistics(runs)["CARD.A"]["CARD.B"]

    assert stat.picked == 0
    assert stat.skipped == 2
    assert stat.pick_win_rate is None
    assert stat.skip_win_rate == 0.5

def test_card_choice_context_primary_card_pick_records_win():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=["CARD.A", "CARD.B"],
                picked_cards=["CARD.A"],
            ),
        ],
    )

    stat = calculate_card_choice_context_statistics([run])["CARD.A"]["CARD.B"]

    assert stat.offered == 1
    assert stat.picked == 1
    assert stat.skipped == 0
    assert stat.wins_when_picked == 1
    assert stat.wins_when_skipped == 0


def test_card_choice_context_competing_card_pick_records_skip():
    run = make_run(
        victory=True,
        card_rewards=[
            make_reward(
                offered_cards=["CARD.A", "CARD.B"],
                picked_cards=["CARD.B"],
            ),
        ],
    )

    stat = calculate_card_choice_context_statistics([run])["CARD.A"]["CARD.B"]

    assert stat.offered == 1
    assert stat.picked == 0
    assert stat.skipped == 1
    assert stat.wins_when_picked == 0
    assert stat.wins_when_skipped == 1

def test_card_choice_context_completely_skipped_reward():
    run = make_run(
        victory=False,
        card_rewards=[
            make_reward(
                offered_cards=["CARD.A", "CARD.B"],
                picked_cards=[],
            ),
        ],
    )

    stat = calculate_card_choice_context_statistics([run])["CARD.A"]["CARD.B"]

    assert stat.offered == 1
    assert stat.picked == 0
    assert stat.skipped == 1
    assert stat.wins_when_skipped == 0
    assert stat.skip_win_rate == 0.0