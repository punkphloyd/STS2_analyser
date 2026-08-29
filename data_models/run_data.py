from dataclasses import dataclass, field

from data_models.death_data import DeathData
from data_models.encounter_data import EncounterData
from data_models.run_metadata import RunMetadata
from data_models.relic_data import RelicAcquisition
from data_models.card_acquisition import CardAcquisition
from data_models.card_reward import CardReward
from data_models.card_transformation import CardTransformation
from data_models.card_upgrade import CardUpgrade

@dataclass(slots=True)
class RunData:
    metadata: RunMetadata
    floor_reached: int
    relic_acquisitions: list[RelicAcquisition] = field(default_factory=list)
    neow_bonus_relic: str | None = None
    neow_relic_choices: list[str] = field(default_factory=list)
    death_data: DeathData | None = None
    encounters: list[EncounterData] = field(default_factory=list)
    card_rewards: list[CardReward] = field(default_factory=list)
    card_acquisitions: list[CardAcquisition] = field(default_factory=list)
    card_upgrades: list[CardUpgrade] = field(default_factory=list)
    card_transformations: list[CardTransformation] = field(default_factory=list)


