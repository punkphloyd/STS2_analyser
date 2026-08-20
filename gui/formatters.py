def format_encounter_name(encounter: str) -> str:
    """Convert an encounter ID into a human-readable name."""

    name = encounter

    if name.startswith("ENCOUNTER."):
        name = name.removeprefix("ENCOUNTER.")

    for suffix in (
        "_ELITE",
        "_BOSS",
        "_MONSTER",
    ):
        if name.endswith(suffix):
            name = name.removesuffix(suffix)
            break

    return name.replace("_", " ").title()