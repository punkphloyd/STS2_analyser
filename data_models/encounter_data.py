from dataclasses import dataclass


@dataclass(slots=True)
class EncounterData:
    encounter: str
    encounter_type: str
    act: int
    floor: int
    act_floor: int
    turns_taken: int
    damage_taken: int
    current_hp: int
    max_hp: int
    hp_healed: int
    max_hp_gained: int
    max_hp_lost: int