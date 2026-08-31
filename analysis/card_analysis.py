from dataclasses import dataclass

from data_models.run_data import RunData
from analysis.card_state import reconstruct_card_states

@dataclass(slots=True)
class CardFinalCopyCountStatistics:
    card: str
    copy_count: int
    runs: int = 0
    wins: int = 0
    losses: int = 0

    @property
    def win_rate(self) -> float:
        if self.runs == 0:
            return 0.0

        return self.wins / self.runs

@dataclass(slots=True)
class CardChoiceStatistics:
    """Statistics for a card when offered as a card reward."""

    offered: int
    picks: int
    pick_rate: float
    wins: int
    win_rate: float | None


@dataclass(slots=True)
class CardStatistics:
    """Statistics for runs in which a card was acquired."""

    runs_acquired: int
    wins: int

    @property
    def win_rate(self) -> float | None:
        """Return the win rate for runs acquiring this card."""

        if self.runs_acquired == 0:
            return None

        return self.wins / self.runs_acquired


@dataclass(slots=True)
class CardSkipStatistics:
    """Statistics for skipped card rewards."""

    rewards: int
    skipped: int
    skip_rate: float
    winning_rewards: int
    winning_skips: int
    winning_skip_rate: float | None
    losing_rewards: int
    losing_skips: int
    losing_skip_rate: float | None


@dataclass(slots=True)
class CardAcquisitionSourceStatistics:
    """
    Statistics for a card acquired from a particular source.

    acquisitions counts individual card copies.

    runs_acquired counts distinct runs in which at least one
    copy of the card was acquired from this source.

    wins counts distinct winning runs in which at least one
    copy of the card was acquired from this source.
    """

    acquisitions: int
    runs_acquired: int
    wins: int

    @property
    def win_rate(self) -> float | None:
        """Return the win rate for runs acquiring this card."""

        if self.runs_acquired == 0:
            return None

        return self.wins / self.runs_acquired


@dataclass(slots=True)
class CardCopyCountStatistics:
    """
    Statistics for runs acquiring a particular number of copies
    of a card.

    runs counts distinct runs.

    wins counts winning runs.
    """

    runs: int
    wins: int

    @property
    def win_rate(self) -> float | None:
        """Return the win rate for this copy-count group."""

        if self.runs == 0:
            return None

        return self.wins / self.runs


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
    """
    Calculate acquisition and win statistics for cards.

    Each card is counted at most once per run. Multiple copies
    acquired during a single run therefore contribute one run
    to runs_acquired.
    """

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


def calculate_card_acquisition_source_statistics(
    runs: list[RunData],
) -> dict[
    str,
    dict[str, CardAcquisitionSourceStatistics],
]:
    """
    Calculate card acquisition statistics broken down by source.

    The result is keyed first by card ID and then by acquisition
    source.

    For each card/source combination:

    - acquisitions counts individual card copies.
    - runs_acquired counts distinct runs containing at least one
      acquisition of the card from that source.
    - wins counts distinct winning runs containing at least one
      acquisition of the card from that source.
    """

    if not runs:
        return {}

    acquisition_counts: dict[
        str,
        dict[str, int],
    ] = {}

    run_sets: dict[
        str,
        dict[str, set[int]],
    ] = {}

    win_counts: dict[
        str,
        dict[str, int],
    ] = {}

    for run_index, run in enumerate(runs):
        seen_in_run: set[tuple[str, str]] = set()

        for acquisition in run.card_acquisitions:
            card = acquisition.card
            source = acquisition.source

            acquisition_counts.setdefault(card, {})
            acquisition_counts[card][source] = (
                acquisition_counts[card].get(source, 0) + 1
            )

            run_sets.setdefault(card, {})
            run_sets[card].setdefault(source, set())
            run_sets[card][source].add(run_index)

            key = (card, source)

            if key in seen_in_run:
                continue

            seen_in_run.add(key)

            if run.metadata.victory:
                win_counts.setdefault(card, {})
                win_counts[card][source] = (
                    win_counts[card].get(source, 0) + 1
                )

    result: dict[
        str,
        dict[str, CardAcquisitionSourceStatistics],
    ] = {}

    for card, sources in acquisition_counts.items():
        result[card] = {}

        for source, acquisitions in sources.items():
            runs_acquired = len(
                run_sets[card][source]
            )

            wins = win_counts.get(
                card,
                {},
            ).get(source, 0)

            result[card][source] = (
                CardAcquisitionSourceStatistics(
                    acquisitions=acquisitions,
                    runs_acquired=runs_acquired,
                    wins=wins,
                )
            )

    return result


def calculate_card_copy_count_statistics(
    runs: list[RunData],
) -> dict[
    str,
    dict[int, CardCopyCountStatistics],
]:
    """
    Calculate win statistics for each number of copies of a card
    acquired during a run.

    Each run contributes at most one observation for each card.

    The copy count is the total number of acquisitions of that
    card during the run, regardless of acquisition source.

    The result is keyed first by card ID and then by the exact
    number of copies acquired.

    For example:

        {
            "CARD.CLOAK_AND_DAGGER": {
                1: CardCopyCountStatistics(...),
                2: CardCopyCountStatistics(...),
                3: CardCopyCountStatistics(...),
            }
        }
    """

    if not runs:
        return {}

    result: dict[
        str,
        dict[int, CardCopyCountStatistics],
    ] = {}

    for run in runs:
        copy_counts: dict[str, int] = {}

        for acquisition in run.card_acquisitions:
            card = acquisition.card
            copy_counts[card] = (
                copy_counts.get(card, 0) + 1
            )

        for card, copy_count in copy_counts.items():
            card_statistics = result.setdefault(
                card,
                {},
            )

            statistics = card_statistics.get(
                copy_count
            )

            if statistics is None:
                statistics = CardCopyCountStatistics(
                    runs=0,
                    wins=0,
                )
                card_statistics[copy_count] = statistics

            statistics.runs += 1

            if run.metadata.victory:
                statistics.wins += 1

    return result

def calculate_card_final_copy_count_statistics(
    runs: list[RunData],
) -> dict[str, dict[int, CardFinalCopyCountStatistics]]:
    """Calculate statistics for final card copy counts."""

    statistics: dict[
        str,
        dict[int, CardFinalCopyCountStatistics],
    ] = {}

    for run in runs:
        card_states = reconstruct_card_states(run)

        copy_counts: dict[str, int] = {}

        for card_state in card_states:
            copy_counts[card_state.card] = (
                copy_counts.get(card_state.card, 0) + 1
            )

        for card, copy_count in copy_counts.items():
            if card not in statistics:
                statistics[card] = {}

            if copy_count not in statistics[card]:
                statistics[card][copy_count] = (
                    CardFinalCopyCountStatistics(
                        card=card,
                        copy_count=copy_count,
                    )
                )

            result = statistics[card][copy_count]

            result.runs += 1

            if run.metadata.victory:
                result.wins += 1
            else:
                result.losses += 1

    return statistics