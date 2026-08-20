from gui.formatters import format_encounter_name


def test_format_elite_encounter_name():

    assert (
        format_encounter_name(
            "ENCOUNTER.ENTOMANCER_ELITE"
        )
        == "Entomancer"
    )


def test_format_boss_encounter_name():

    assert (
        format_encounter_name(
            "ENCOUNTER.WATERFALL_GIANT_BOSS"
        )
        == "Waterfall Giant"
    )


def test_format_monster_encounter_name():

    assert (
        format_encounter_name(
            "ENCOUNTER.SOME_MONSTER"
        )
        == "Some"
    )


def test_format_multiword_encounter_name():

    assert (
        format_encounter_name(
            "ENCOUNTER.PHANTASMAL_GARDENERS_ELITE"
        )
        == "Phantasmal Gardeners"
    )


def test_format_encounter_without_prefix():

    assert (
        format_encounter_name(
            "ENTOMANCER_ELITE"
        )
        == "Entomancer"
    )