import json
from pathlib import Path

from parsers.run_parser import (
    parse_death_data,
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