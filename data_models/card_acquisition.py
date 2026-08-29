from dataclasses import dataclass


@dataclass(slots=True)
class CardAcquisition:
    card: str
    source: str
    act: int
    floor: int
    act_floor: int
    upgraded: bool = False