from collections.abc import Iterable
from dataclasses import dataclass

from data_models.run_data import RunData


@dataclass
class CardAcquisitionTimingStatistics:
    card: str
    winning_runs: int = 0
    losing_runs: int = 0
    total_winning_acquisition_floors: int = 0
    total_losing_acquisition_floors: int = 0

    @property
    def average_winning_acquisition_floor(self) -> float | None:
        if self.winning_runs == 0:
            return None

        return (
            self.total_winning_acquisition_floors
            / self.winning_runs
        )

    @property
    def average_losing_acquisition_floor(self) -> float | None:
        if self.losing_runs == 0:
            return None

        return (
            self.total_losing_acquisition_floors
            / self.losing_runs
        )

    @property
    def average_acquisition_floor_difference(self) -> float | None:
        winning = self.average_winning_acquisition_floor
        losing = self.average_losing_acquisition_floor

        if winning is None or losing is None:
            return None

        return winning - losing


@dataclass(slots=True)
class CardChoiceTimingStatistics:
    offered: int = 0
    picked: int = 0
    skipped: int = 0
    wins_when_picked: int = 0
    wins_when_skipped: int = 0

    @property
    def pick_rate(self) -> float | None:
        if self.offered == 0:
            return None

        return self.picked / self.offered

    @property
    def skip_rate(self) -> float | None:
        if self.offered == 0:
            return None

        return self.skipped / self.offered

    @property
    def pick_win_rate(self) -> float | None:
        if self.picked == 0:
            return None

        return self.wins_when_picked / self.picked

    @property
    def skip_win_rate(self) -> float | None:
        if self.skipped == 0:
            return None

        return self.wins_when_skipped / self.skipped

    @property
    def win_rate_difference(self) -> float | None:
        pick_win_rate = self.pick_win_rate
        skip_win_rate = self.skip_win_rate

        if pick_win_rate is None or skip_win_rate is None:
            return None

        return pick_win_rate - skip_win_rate


def calculate_card_acquisition_timing_statistics(
    runs: Iterable[RunData],
) -> dict[str, CardAcquisitionTimingStatistics]:
    statistics: dict[str, CardAcquisitionTimingStatistics] = {}

    for run in runs:
        for acquisition in run.card_acquisitions:
            if acquisition.card not in statistics:
                statistics[acquisition.card] = CardAcquisitionTimingStatistics(
                    card=acquisition.card
                )

            stat = statistics[acquisition.card]

            if run.metadata.victory:
                stat.winning_runs += 1
                stat.total_winning_acquisition_floors += acquisition.floor
            else:
                stat.losing_runs += 1
                stat.total_losing_acquisition_floors += acquisition.floor

    return statistics


def calculate_card_choice_timing_statistics(
    runs: Iterable[RunData],
) -> dict[str, dict[int, CardChoiceTimingStatistics]]:
    statistics: dict[str, dict[int, CardChoiceTimingStatistics]] = {}

    for run in runs:
        for reward in run.card_rewards:
            offered_cards = list(dict.fromkeys(reward.offered_cards))
            picked_cards = set(reward.picked_cards)

            for card in offered_cards:
                if card not in statistics:
                    statistics[card] = {}

                if reward.act not in statistics[card]:
                    statistics[card][reward.act] = CardChoiceTimingStatistics()

                stat = statistics[card][reward.act]
                stat.offered += 1

                if card in picked_cards:
                    stat.picked += 1

                    if run.metadata.victory:
                        stat.wins_when_picked += 1
                else:
                    stat.skipped += 1

                    if run.metadata.victory:
                        stat.wins_when_skipped += 1

    return statistics