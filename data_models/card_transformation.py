from dataclasses import dataclass


@dataclass(slots=True)
class CardTransformation:
    original_card: str
    final_card: str
    source: str
    act: int
    floor: int
    act_floor: int