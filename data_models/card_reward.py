from dataclasses import dataclass


@dataclass(slots=True)
class CardReward:
    source: str
    act: int
    floor: int
    act_floor: int
    offered_cards: list[str]
    picked_cards: list[str]