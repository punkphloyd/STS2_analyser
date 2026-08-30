from dataclasses import dataclass

from data_models.run_data import RunData


@dataclass(slots=True)
class CardChoiceStatistics:
    offered: int
    picks: int
    pick_rate: float
    wins: int
    win_rate: float | None


@dataclass(slots=True)
class CardStatistics:
    runs_acquired: int
    wins: int

    @property
    def win_rate(self) -> float | None:
        if self.runs_acquired == 0:
            return None

        return self.wins / self.runs_acquired


@dataclass(slots=True)
class CardSkipStatistics:
    rewards: int
    skipped: int
    skip_rate: float
    winning_rewards: int
    winning_skips: int
    winning_skip_rate: float | None
    losing_rewards: int
    losing_skips: int
    losing_skip_rate: float | None


def calculate_card_choice_statistics(
    runs: list[RunData],
) -> dict[str, CardChoiceStatistics]:
    """Calculate card offer, pick, and win statistics."""

    if not runs:
        return {}

    offered_counts: dict[str, int] = {}
    pick_counts: dict[str, int] = {}
    win_counts: dict[str, int] = {}

    for run in runs:

        for reward in run.card_rewards:

            for card in reward.offered_cards:
                offered_counts[card] = (
                    offered_counts.get(card, 0) + 1
                )

            for card in reward.picked_cards:
                pick_counts[card] = (
                    pick_counts.get(card, 0) + 1
                )

                if run.metadata.victory:
                    win_counts[card] = (
                        win_counts.get(card, 0) + 1
                    )

    result: dict[str, CardChoiceStatistics] = {}

    for card, offered in offered_counts.items():

        picks = pick_counts.get(card, 0)
        wins = win_counts.get(card, 0)

        result[card] = CardChoiceStatistics(
            offered=offered,
            picks=picks,
            pick_rate=picks / offered,
            wins=wins,
            win_rate=(
                wins / picks
                if picks > 0
                else None
            ),
        )

    return result


def calculate_card_statistics(
    runs: list[RunData],
) -> dict[str, CardStatistics]:
    """Calculate acquisition and win statistics for cards."""

    if not runs:
        return {}

    acquisition_counts: dict[str, int] = {}
    win_counts: dict[str, int] = {}

    for run in runs:

        acquired_cards = {
            acquisition.card
            for acquisition in run.card_acquisitions
        }

        for card in acquired_cards:

            acquisition_counts[card] = (
                acquisition_counts.get(card, 0) + 1
            )

            if run.metadata.victory:
                win_counts[card] = (
                    win_counts.get(card, 0) + 1
                )

    result: dict[str, CardStatistics] = {}

    for card, runs_acquired in acquisition_counts.items():

        wins = win_counts.get(card, 0)

        result[card] = CardStatistics(
            runs_acquired=runs_acquired,
            wins=wins,
        )

    return result


def calculate_card_skip_statistics(
    runs: list[RunData],
) -> CardSkipStatistics:
    """Calculate overall card reward skip statistics."""

    if not runs:
        return CardSkipStatistics(
            rewards=0,
            skipped=0,
            skip_rate=0,
            winning_rewards=0,
            winning_skips=0,
            winning_skip_rate=None,
            losing_rewards=0,
            losing_skips=0,
            losing_skip_rate=None,
        )

    rewards = 0
    skipped = 0

    winning_rewards = 0
    winning_skips = 0

    losing_rewards = 0
    losing_skips = 0

    for run in runs:

        for reward in run.card_rewards:

            rewards += 1

            was_skipped = not reward.picked_cards

            if was_skipped:
                skipped += 1

            if run.metadata.victory:
                winning_rewards += 1

                if was_skipped:
                    winning_skips += 1

            else:
                losing_rewards += 1

                if was_skipped:
                    losing_skips += 1

    return CardSkipStatistics(
        rewards=rewards,
        skipped=skipped,
        skip_rate=(
            skipped / rewards
            if rewards > 0
            else 0
        ),
        winning_rewards=winning_rewards,
        winning_skips=winning_skips,
        winning_skip_rate=(
            winning_skips / winning_rewards
            if winning_rewards > 0
            else None
        ),
        losing_rewards=losing_rewards,
        losing_skips=losing_skips,
        losing_skip_rate=(
            losing_skips / losing_rewards
            if losing_rewards > 0
            else None
        ),
    )