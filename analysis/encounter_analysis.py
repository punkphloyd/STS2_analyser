from data_models.encounter_data import EncounterData
from data_models.relic_data import RelicAcquisition
from data_models.run_data import RunData


def acquisition_precedes_encounter(
    acquisition: RelicAcquisition,
    encounter: EncounterData,
) -> bool:
    """Return whether an acquisition occurred before an encounter."""

    return acquisition.floor < encounter.floor


def relic_present_at_encounter(
    relic: str,
    run: RunData,
    encounter: EncounterData,
) -> bool:
    """Return whether a relic was acquired before an encounter."""

    return any(
        acquisition.relic == relic
        and acquisition_precedes_encounter(
            acquisition,
            encounter,
        )
        for acquisition in run.relic_acquisitions
    )