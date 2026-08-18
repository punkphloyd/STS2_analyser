from dataclasses import dataclass


@dataclass(slots=True)
class DeathData:

    killed_by_encounter: str | None
    killed_by_event: str | None