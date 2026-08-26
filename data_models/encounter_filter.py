from dataclasses import dataclass


@dataclass(slots=True)
class EncounterFilter:
    act: int | None = None
    encounter_type: str | None = None
    encounter_name: str | None = None