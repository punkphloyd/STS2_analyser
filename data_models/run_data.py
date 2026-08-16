from dataclasses import dataclass, field

from data_models.run_metadata import RunMetadata


@dataclass(slots=True)
class RunData:
    metadata: RunMetadata
    neow_bonus_relic: str | None = None
    neow_relic_choices: list[str] = field(default_factory=list)