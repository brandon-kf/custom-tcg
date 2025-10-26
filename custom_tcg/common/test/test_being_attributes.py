"""Tests for beings in `custom_tcg.common.being`.

These verify that each being's factory `.create(player)` sets:
- correct name
- includes CardTypeDef.being in types
- expected classes on the card
- includes a BeingStats effect (without asserting specific values)
"""

from __future__ import annotations

import pytest

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.core.anon import Player
from custom_tcg.core.dimension import CardTypeDef


@pytest.fixture
def player() -> Player:
    """Minimal test player suitable for card creation."""
    return Player(
        session_object_id="test-player",
        name="Test Player",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )


# Table of (import_path, class_name, expected_classes)
BEINGS: list[tuple[str, str, list]] = [
    (
        "custom_tcg.common.being.aged_prophet",
        "AgedProphet",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.aimless_wanderer",
        "AimlessWanderer",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.apprentice_carpenter",
        "ApprenticeCarpenter",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.apprentice_smith",
        "ApprenticeSmith",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.desperate_shepherd",
        "DesperateShepherd",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.destructive_darryl",
        "DestructiveDarryl",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.early_architect",
        "EarlyArchitect",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.last_survivor",
        "LastSurvivor",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.peasant",
        "Peasant",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.questionable_butcher",
        "QuestionableButcher",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.resourceful_preacher",
        "ResourcefulPreacher",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.seamstress",
        "Seamstress",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.sheep",
        "Sheep",
        [CardClassDef.animal, CardClassDef.fluffy_animal],
    ),
    (
        "custom_tcg.common.being.skilled_hunter",
        "SkilledHunter",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.that_pebble_girl",
        "ThatPebbleGirl",
        [CardClassDef.human],
    ),
    (
        "custom_tcg.common.being.the_stewmaker",
        "TheStewmaker",
        [CardClassDef.human],
    ),
]


@pytest.mark.parametrize(
    ("module_path", "cls_name", "expected_classes"),
    BEINGS,
)
def test_being_create_sets_core_attributes(
    module_path: str,
    cls_name: str,
    expected_classes: list,
    player: Player,
) -> None:
    """Ensure each being's factory sets core attributes and base stats."""
    mod = __import__(module_path, fromlist=[cls_name])
    cls = getattr(mod, cls_name)

    # Create the card
    card = cls.create(player=player)

    # Name matches the class-level name
    assert card.name == cls.name

    # Type includes Being
    assert CardTypeDef.being in card.types

    # Classes include the expected entries (subset check)
    for klass in expected_classes:
        assert klass in card.classes

    # Has a BeingStats effect
    stats_effect = next(
        (e for e in card.effects if isinstance(e, BeingStats)),
        None,
    )
    assert stats_effect is not None, "Missing BeingStats effect"
