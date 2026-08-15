import json

from parsers.metadata_parser import parse_metadata


def test_parse_metadata_extracts_game_version_and_game_mode(tmp_path):

    run_data = {
        "start_time": 1754000000,
        "ascension": 5,
        "win": True,
        "build_id": "v0.107.1",
        "game_mode": "daily",
        "players": [
            {
                "character": "CHARACTER.IRONCLAD"
            }
        ]
    }

    run_file = tmp_path / "test.run"

    with run_file.open("w", encoding="utf-8") as file:
        json.dump(run_data, file)

    result = parse_metadata(run_file)

    assert result.game_version == "v0.107.1"
    assert result.game_mode == "daily"
    assert result.multiplayer is False

def test_parse_metadata_detects_multiplayer(tmp_path):

    run_data = {
        "start_time": 1754000000,
        "ascension": 5,
        "win": True,
        "build_id": "v0.107.1",
        "game_mode": "standard",
        "players": [
            {
                "character": "CHARACTER.IRONCLAD",
                "deck": [],
            },
            {
                "character": "CHARACTER.SILENT",
                "deck": [],
            },
        ],
    }

    run_file = tmp_path / "multiplayer.run"

    with run_file.open("w", encoding="utf-8") as file:
        json.dump(run_data, file)

    result = parse_metadata(run_file)

    assert result.multiplayer is True