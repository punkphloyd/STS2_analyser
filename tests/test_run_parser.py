import json
from pathlib import Path

from parsers.run_parser import (
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