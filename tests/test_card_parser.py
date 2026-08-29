from parsers.card_parser import parse_card_data


def test_parse_fight_card_reward():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "monster",
                    "player_stats": [
                        {
                            "card_choices": [
                                {
                                    "card": {
                                        "id": "CARD.HAZE",
                                    },
                                    "was_picked": True,
                                },
                                {
                                    "card": {
                                        "id": "CARD.BLADE_DANCE",
                                    },
                                    "was_picked": False,
                                },
                                {
                                    "card": {
                                        "id": "CARD.POISONED_STAB",
                                    },
                                    "was_picked": False,
                                },
                            ],
                            "cards_gained": [
                                {
                                    "id": "CARD.HAZE",
                                },
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "model_id": (
                                "ENCOUNTER.FUZZY_WURM_CRAWLER_WEAK"
                            ),
                            "room_type": "monster",
                            "turns_taken": 4,
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert len(rewards) == 1

    reward = rewards[0]

    assert reward.source == "monster"
    assert reward.act == 1
    assert reward.floor == 1
    assert reward.act_floor == 1

    assert reward.offered_cards == [
        "CARD.HAZE",
        "CARD.BLADE_DANCE",
        "CARD.POISONED_STAB",
    ]

    assert reward.picked_cards == [
        "CARD.HAZE",
    ]

    assert len(acquisitions) == 1

    acquisition = acquisitions[0]

    assert acquisition.card == "CARD.HAZE"
    assert acquisition.source == "monster"
    assert acquisition.act == 1
    assert acquisition.floor == 1
    assert acquisition.act_floor == 1
    assert acquisition.upgraded is False

    assert upgrades == []
    assert transformations == []


def test_parse_skipped_fight_card_reward():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "monster",
                    "player_stats": [
                        {
                            "card_choices": [
                                {
                                    "card": {
                                        "id": "CARD.HAZE",
                                    },
                                    "was_picked": False,
                                },
                                {
                                    "card": {
                                        "id": "CARD.BLADE_DANCE",
                                    },
                                    "was_picked": False,
                                },
                                {
                                    "card": {
                                        "id": "CARD.POISONED_STAB",
                                    },
                                    "was_picked": False,
                                },
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "model_id": "ENCOUNTER.TEST",
                            "room_type": "monster",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert len(rewards) == 1

    reward = rewards[0]

    assert reward.offered_cards == [
        "CARD.HAZE",
        "CARD.BLADE_DANCE",
        "CARD.POISONED_STAB",
    ]

    assert reward.picked_cards == []

    assert acquisitions == []
    assert upgrades == []
    assert transformations == []


def test_parse_shop_card_purchase():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "shop",
                    "player_stats": [
                        {
                            "card_choices": [
                                {
                                    "card": {
                                        "id": "CARD.SLICE",
                                    },
                                    "was_picked": False,
                                },
                                {
                                    "card": {
                                        "id": "CARD.EXPERTISE",
                                    },
                                    "was_picked": False,
                                },
                                {
                                    "card": {
                                        "id": "CARD.BLUR",
                                    },
                                    "was_picked": False,
                                },
                            ],
                            "cards_gained": [
                                {
                                    "id": "CARD.DAGGER_SPRAY",
                                },
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "room_type": "shop",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert len(rewards) == 1

    reward = rewards[0]

    assert reward.source == "shop"

    assert reward.offered_cards == [
        "CARD.SLICE",
        "CARD.EXPERTISE",
        "CARD.BLUR",
        "CARD.DAGGER_SPRAY",
    ]

    assert reward.picked_cards == [
        "CARD.DAGGER_SPRAY",
    ]

    assert len(acquisitions) == 1

    assert acquisitions[0].card == "CARD.DAGGER_SPRAY"
    assert acquisitions[0].source == "shop"

    assert upgrades == []
    assert transformations == []


def test_parse_shop_multiple_card_purchases():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "shop",
                    "player_stats": [
                        {
                            "card_choices": [
                                {
                                    "card": {
                                        "id": "CARD.SLICE",
                                    },
                                    "was_picked": False,
                                },
                                {
                                    "card": {
                                        "id": "CARD.BLUR",
                                    },
                                    "was_picked": False,
                                },
                            ],
                            "cards_gained": [
                                {
                                    "id": "CARD.DAGGER_SPRAY",
                                },
                                {
                                    "id": "CARD.FOOTWORK",
                                },
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "room_type": "shop",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert len(rewards) == 1

    reward = rewards[0]

    assert reward.offered_cards == [
        "CARD.SLICE",
        "CARD.BLUR",
        "CARD.DAGGER_SPRAY",
        "CARD.FOOTWORK",
    ]

    assert reward.picked_cards == [
        "CARD.DAGGER_SPRAY",
        "CARD.FOOTWORK",
    ]

    assert [acquisition.card for acquisition in acquisitions] == [
        "CARD.DAGGER_SPRAY",
        "CARD.FOOTWORK",
    ]


def test_parse_pre_upgraded_card_acquisition():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "monster",
                    "player_stats": [
                        {
                            "card_choices": [
                                {
                                    "card": {
                                        "id": "CARD.PREDATOR",
                                        "current_upgrade_level": 1,
                                    },
                                    "was_picked": True,
                                },
                                {
                                    "card": {
                                        "id": "CARD.DEADLY_POISON",
                                    },
                                    "was_picked": False,
                                },
                            ],
                            "cards_gained": [
                                {
                                    "id": "CARD.PREDATOR",
                                    "current_upgrade_level": 1,
                                },
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "room_type": "monster",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert len(acquisitions) == 1

    acquisition = acquisitions[0]

    assert acquisition.card == "CARD.PREDATOR"
    assert acquisition.upgraded is True

    assert len(rewards) == 1
    assert rewards[0].picked_cards == [
        "CARD.PREDATOR",
    ]

    assert upgrades == []
    assert transformations == []


def test_parse_rest_site_card_upgrade():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "rest_site",
                    "player_stats": [
                        {
                            "upgraded_cards": [
                                "CARD.STRIKE",
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "room_type": "rest_site",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert rewards == []
    assert acquisitions == []

    assert len(upgrades) == 1

    upgrade = upgrades[0]

    assert upgrade.card == "CARD.STRIKE"
    assert upgrade.source == "rest_site"
    assert upgrade.act == 1
    assert upgrade.floor == 1
    assert upgrade.act_floor == 1

    assert transformations == []


def test_parse_event_card_upgrade():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "unknown",
                    "player_stats": [
                        {
                            "upgraded_cards": [
                                "CARD.DEFEND_SILENT",
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "model_id": "EVENT.DOORS_OF_LIGHT_AND_DARK",
                            "room_type": "event",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert rewards == []
    assert acquisitions == []

    assert len(upgrades) == 1

    upgrade = upgrades[0]

    assert upgrade.card == "CARD.DEFEND_SILENT"
    assert upgrade.source == "event"
    assert upgrade.act == 1
    assert upgrade.floor == 1
    assert upgrade.act_floor == 1

    assert transformations == []


def test_parse_duplicate_card_upgrades():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "unknown",
                    "player_stats": [
                        {
                            "upgraded_cards": [
                                "CARD.DEFEND_SILENT",
                                "CARD.DEFEND_SILENT",
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "model_id": "EVENT.DOORS_OF_LIGHT_AND_DARK",
                            "room_type": "event",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert rewards == []
    assert acquisitions == []

    assert len(upgrades) == 2

    assert upgrades[0].card == "CARD.DEFEND_SILENT"
    assert upgrades[1].card == "CARD.DEFEND_SILENT"

    assert transformations == []


def test_parse_card_transformation():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "unknown",
                    "player_stats": [
                        {
                            "cards_transformed": [
                                {
                                    "original_card": {
                                        "id": "CARD.DEFEND_SILENT",
                                        "floor_added_to_deck": 1,
                                    },
                                    "final_card": {
                                        "id": "CARD.TORIC_TOUGHNESS",
                                        "floor_added_to_deck": 7,
                                    },
                                },
                            ],
                        },
                    ],
                    "rooms": [
                        {
                            "model_id": "EVENT.WOOD_CARVINGS",
                            "room_type": "event",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert rewards == []
    assert acquisitions == []
    assert upgrades == []

    assert len(transformations) == 1

    transformation = transformations[0]

    assert transformation.original_card == (
        "CARD.DEFEND_SILENT"
    )

    assert transformation.final_card == (
        "CARD.TORIC_TOUGHNESS"
    )

    assert transformation.source == "event"
    assert transformation.act == 1
    assert transformation.floor == 1
    assert transformation.act_floor == 1


def test_ignore_map_points_without_card_activity():
    data = {
        "map_point_history": [
            [
                {
                    "map_point_type": "rest_site",
                    "player_stats": [
                        {
                            "current_hp": 50,
                        },
                    ],
                    "rooms": [
                        {
                            "room_type": "rest_site",
                        },
                    ],
                },
                {
                    "map_point_type": "monster",
                    "player_stats": [
                        {
                            "current_hp": 45,
                        },
                    ],
                    "rooms": [
                        {
                            "room_type": "monster",
                        },
                    ],
                },
            ],
        ],
    }

    rewards, acquisitions, upgrades, transformations = (
        parse_card_data(data)
    )

    assert rewards == []
    assert acquisitions == []
    assert upgrades == []
    assert transformations == []


def test_parse_empty_map_point_history():
    rewards, acquisitions, upgrades, transformations = (
        parse_card_data({})
    )

    assert rewards == []
    assert acquisitions == []
    assert upgrades == []
    assert transformations == []