from dataclasses import dataclass, field

from data_models.death_data import DeathData
from data_models.encounter_data import EncounterData
from data_models.run_metadata import RunMetadata
from data_models.relic_data import RelicAcquisition

@dataclass(slots=True)
class RunData:
    metadata: RunMetadata
    floor_reached: int
    relic_acquisitions: list[RelicAcquisition]
    neow_bonus_relic: str | None = None
    neow_relic_choices: list[str] = field(default_factory=list)
    death_data: DeathData | None = None
    encounters: list[EncounterData] = field(default_factory=list)

