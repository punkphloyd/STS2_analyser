import json
from pathlib import Path

from parsers.run_parser import (
    parse_death_data,
    parse_encounter_data,
    parse_floor_reached,
    parse_neow_relic_choices,
    parse_run,
)


EXAMPLE_RUNFILES = Path("example_runfiles")


def test_parse_neow_bonus_relic():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    result = parse_run(path)

    assert result.neow_bonus_relic == "HEFTY_TABLET"
    assert len(result.neow_relic_choices) == 3
    assert result.neow_bonus_relic in result.neow_relic_choices


def test_parse_neow_bonus_relic_from_older_run():

    path = EXAMPLE_RUNFILES / "1780176025.run"

    result = parse_run(path)

    assert result.neow_bonus_relic == "NEOWS_BONES"
    assert len(result.neow_relic_choices) == 3
    assert result.neow_bonus_relic in result.neow_relic_choices


def test_parse_multiplayer_run():

    path = EXAMPLE_RUNFILES / "1778529252.run"

    result = parse_run(path)

    assert result.metadata.multiplayer is True

def test_parse_neow_relic_choices():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    choices, selected = parse_neow_relic_choices(data)

    assert len(choices) == 3
    assert selected == "HEFTY_TABLET"
    assert selected in choices


def test_parse_death_data():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_death_data(data)

    assert result is not None
    assert result.killed_by_encounter == (
        "ENCOUNTER.ENTOMANCER_ELITE"
    )
    assert result.killed_by_event == "NONE.NONE"

def test_parse_death_data_for_victory():

    path = EXAMPLE_RUNFILES / "1785229299.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_death_data(data)

    assert result is None

def test_parse_run_includes_death_data():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    result = parse_run(path)

    assert result.death_data is not None
    assert result.death_data.killed_by_encounter == (
        "ENCOUNTER.ENTOMANCER_ELITE"
    )


def test_parse_run_has_no_death_data_for_victory():

    path = EXAMPLE_RUNFILES / "1785229299.run"

    result = parse_run(path)

    assert result.death_data is None

def test_parse_run_includes_floor_reached_for_victory():

    path = EXAMPLE_RUNFILES / "1785229299.run"

    result = parse_run(path)

    assert result.floor_reached > 0

def test_parse_floor_reached():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_floor_reached(data)

    assert result == 31

def test_parse_successful_elite_encounter():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_encounter_data(data)

    encounter = get_encounter(
        result,
        "ENCOUNTER.PHANTASMAL_GARDENERS_ELITE",
    )

    assert encounter.encounter_type == "elite"
    assert encounter.act == 1
    assert encounter.floor == 9
    assert encounter.act_floor == 9
    assert encounter.turns_taken == 7
    assert encounter.damage_taken == 33
    assert encounter.current_hp == 18


def test_parse_successful_boss_encounter():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_encounter_data(data)

    boss = next(
        encounter
        for encounter in result
        if encounter.encounter
        == "ENCOUNTER.WATERFALL_GIANT_BOSS"
    )

    assert boss.encounter_type == "boss"
    assert boss.damage_taken == 60
    assert boss.current_hp == 17
    assert boss.max_hp == 80
    assert boss.hp_healed == 6
    assert boss.max_hp_gained == 0
    assert boss.max_hp_lost == 0


def test_parse_fatal_elite_encounter():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_encounter_data(data)

    entomancer = next(
        encounter
        for encounter in result
        if encounter.encounter
        == "ENCOUNTER.ENTOMANCER_ELITE"
    )

    assert entomancer.encounter_type == "elite"
    assert entomancer.damage_taken == 55
    assert entomancer.current_hp == 0
    assert entomancer.max_hp == 80
    assert entomancer.hp_healed == 0
    assert entomancer.max_hp_gained == 0
    assert entomancer.max_hp_lost == 0


def test_parse_run_includes_encounters():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    result = parse_run(path)

    assert len(result.encounters) > 0

    assert any(
        encounter.encounter
        == "ENCOUNTER.PHANTASMAL_GARDENERS_ELITE"
        for encounter in result.encounters
    )

    assert any(
        encounter.encounter
        == "ENCOUNTER.WATERFALL_GIANT_BOSS"
        for encounter in result.encounters
    )

    assert any(
        encounter.encounter
        == "ENCOUNTER.ENTOMANCER_ELITE"
        and encounter.current_hp == 0
        for encounter in result.encounters
    )

def test_parse_act_2_encounter_location():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_encounter_data(data)

    encounter = next(
        encounter
        for encounter in result
        if encounter.act == 2
    )

    assert encounter.act == 2
    assert encounter.floor > 18
    assert encounter.act_floor >= 1
    assert encounter.floor > encounter.act_floor

def test_parse_act_3_encounter_location():

    path = EXAMPLE_RUNFILES / "1780311404.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_encounter_data(data)

    encounter = next(
        encounter
        for encounter in result
        if encounter.act == 3
    )

    assert encounter.act == 3
    assert encounter.act_floor >= 1
    assert encounter.floor >= encounter.act_floor

def test_parse_normal_monster_encounter():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_encounter_data(data)

    monster = get_encounter(
        result,
        "ENCOUNTER.SLUDGE_SPINNER_WEAK",
    )

    assert monster.encounter_type == "monster"
    assert monster.act == 1
    assert monster.floor > 1
    assert monster.act_floor > 1
    assert monster.turns_taken == 3
    assert monster.damage_taken == 12

def test_parse_encounter_data_excludes_ancients():

    path = EXAMPLE_RUNFILES / "1785257698.run"

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    result = parse_encounter_data(data)

    assert all(
        encounter.encounter_type
        in {"monster", "elite", "boss"}
        for encounter in result
    )


def get_encounter(
    encounters,
    encounter_name,
):
    return next(
        encounter
        for encounter in encounters
        if encounter.encounter == encounter_name
    )