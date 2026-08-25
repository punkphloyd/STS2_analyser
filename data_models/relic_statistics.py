from dataclasses import dataclass


@dataclass(slots=True)
class RelicEncounterStatistics:
    fights: int
    wins: int
    win_rate: float

    average_damage: float
    median_damage: float
    minimum_damage: int
    maximum_damage: int

    average_turns: float
    minimum_turns: int
    maximum_turns: int

    average_damage_per_turn: float