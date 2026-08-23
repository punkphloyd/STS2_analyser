from dataclasses import dataclass


@dataclass(slots=True)
class RelicAcquisition:
    relic: str
    source: str
    act: int
    floor: int
    act_floor: int