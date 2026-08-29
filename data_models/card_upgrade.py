from dataclasses import dataclass


@dataclass(slots=True)
class CardUpgrade:
    card: str
    source: str
    act: int
    floor: int
    act_floor: int