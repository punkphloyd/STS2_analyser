from dataclasses import dataclass

from data_models.run_data import RunData


@dataclass(slots=True)
class CardCorrelationStatistics:
    """
    Statistics comparing runs with and without a particular card.
    """

    runs_with_card: int
    wins_with_card: int
    win_rate_with_card: float | None

    runs_without_card: int
    wins_without_card: int
    win_rate_without_card: float | None

    @property
    def win_rate_difference(self) -> float | None:
        if (
            self.win_rate_with_card is None
            or self.win_rate_without_card is None
        ):
            return None

        return (
            self.win_rate_with_card
            - self.win_rate_without_card
        )


@dataclass(slots=True)
class CardPickSkipCorrelationStatistics:
    """
    Statistics for the outcome of picking versus not picking a
    particular card when it is offered.

    Each offer of the card contributes one observation.

    A card is considered picked when it appears in picked_cards
    for that reward. Otherwise, the card is considered skipped.

    wins counts observations occurring in winning runs.
    """

    offered: int = 0

    picked: int = 0
    wins_when_picked: int = 0

    skipped: int = 0
    wins_when_skipped: int = 0

    @property
    def pick_win_rate(self) -> float | None:
        """Return the win rate for offers where the card was picked."""

        if self.picked == 0:
            return None

        return self.wins_when_picked / self.picked

    @property
    def skip_win_rate(self) -> float | None:
        """Return the win rate for offers where the card was skipped."""

        if self.skipped == 0:
            return None

        return self.wins_when_skipped / self.skipped

    @property
    def win_rate_difference(self) -> float | None:
        """
        Return pick win rate minus skip win rate.

        A positive value means picking the card is associated with
        a higher win rate than skipping it.
        """

        pick_rate = self.pick_win_rate
        skip_rate = self.skip_win_rate

        if pick_rate is None or skip_rate is None:
            return None

        return pick_rate - skip_rate


def calculate_card_correlation(
    card: str,
    runs: list[RunData],
) -> CardCorrelationStatistics:
    """
    Calculate the win-rate correlation for a card.

    Runs are divided into those containing at least one acquisition
    of the card and those containing none.
    """

    runs_with_card = 0
    wins_with_card = 0
    runs_without_card = 0
    wins_without_card = 0

    for run in runs:
        has_card = any(
            acquisition.card == card
            for acquisition in run.card_acquisitions
        )

        if has_card:
            runs_with_card += 1

            if run.metadata.victory:
                wins_with_card += 1
        else:
            runs_without_card += 1

            if run.metadata.victory:
                wins_without_card += 1

    win_rate_with_card = (
        wins_with_card / runs_with_card
        if runs_with_card > 0
        else None
    )

    win_rate_without_card = (
        wins_without_card / runs_without_card
        if runs_without_card > 0
        else None
    )

    return CardCorrelationStatistics(
        runs_with_card=runs_with_card,
        wins_with_card=wins_with_card,
        win_rate_with_card=win_rate_with_card,
        runs_without_card=runs_without_card,
        wins_without_card=wins_without_card,
        win_rate_without_card=win_rate_without_card,
    )


def calculate_all_card_correlations(
    runs: list[RunData],
) -> dict[str, CardCorrelationStatistics]:
    """
    Calculate acquisition/outcome correlations for every card
    appearing in the supplied runs.
    """

    cards = {
        acquisition.card
        for run in runs
        for acquisition in run.card_acquisitions
    }

    return {
        card: calculate_card_correlation(card, runs)
        for card in cards
    }


def calculate_card_pick_skip_correlations(
    runs: list[RunData],
) -> dict[str, CardPickSkipCorrelationStatistics]:
    """
    Calculate outcome statistics for picking versus skipping each
    offered card.

    Each time a card appears in offered_cards, it contributes one
    observation.

    If the card appears in picked_cards for that reward, the
    observation is classified as picked.

    Otherwise, the observation is classified as skipped.

    The outcome is determined by the result of the run containing
    the reward.
    """

    if not runs:
        return {}

    statistics: dict[
        str,
        CardPickSkipCorrelationStatistics,
    ] = {}

    for run in runs:
        for reward in run.card_rewards:
            picked_cards = set(reward.picked_cards)

            for card in reward.offered_cards:
                if card not in statistics:
                    statistics[card] = (
                        CardPickSkipCorrelationStatistics()
                    )

                stats = statistics[card]

                stats.offered += 1

                if card in picked_cards:
                    stats.picked += 1

                    if run.metadata.victory:
                        stats.wins_when_picked += 1
                else:
                    stats.skipped += 1

                    if run.metadata.victory:
                        stats.wins_when_skipped += 1

    return statistics