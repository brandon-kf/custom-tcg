"""Tests for items in `custom_tcg.common.item`.

Verifies that each item's factory `.create(player)` sets:
- correct name
- includes CardTypeDef.item in types
- expected classes on the card
- includes an ItemStats effect (without asserting specific values)
"""

from __future__ import annotations

import pytest

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.anon import Player


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
ITEMS: list[tuple[str, str, list]] = [
    (
        "custom_tcg.common.item.ball_of_wool",
        "BallOfWool",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.bundle_of_wool",
        "BundleOfWool",
        [CardClassDef.material, CardClassDef.bulk_material],
    ),
    (
        "custom_tcg.common.item.cloth",
        "Cloth",
        [CardClassDef.material, CardClassDef.craft_material],
    ),
    (
        "custom_tcg.common.item.cord",
        "Cord",
        [CardClassDef.material, CardClassDef.craft_material],
    ),
    (
        "custom_tcg.common.item.extra_rations",
        "ExtraRations",
        [CardClassDef.food, CardClassDef.simple_food],
    ),
    (
        "custom_tcg.common.item.fire",
        "Fire",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.flint",
        "Flint",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.metal",
        "Metal",
        [CardClassDef.material, CardClassDef.craft_material],
    ),
    (
        "custom_tcg.common.item.pebble",
        "Pebble",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.pelt",
        "Pelt",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.pile_of_rocks",
        "PileOfRocks",
        [CardClassDef.material, CardClassDef.bulk_material],
    ),
    (
        "custom_tcg.common.item.pile_of_wood",
        "PileOfWood",
        [CardClassDef.material, CardClassDef.bulk_material],
    ),
    (
        "custom_tcg.common.item.stew",
        "Stew",
        [CardClassDef.food, CardClassDef.processed_food],
    ),
    (
        "custom_tcg.common.item.stick",
        "Stick",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.stone",
        "Stone",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.stone_path",
        "StonePath",
        [CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.trail",
        "Trail",
        [CardClassDef.material, CardClassDef.base_material],
    ),
    (
        "custom_tcg.common.item.wood_structure",
        "WoodStructure",
        [CardClassDef.material, CardClassDef.craft_material],
    ),
]


@pytest.mark.parametrize(("module_path", "cls_name", "expected_classes"), ITEMS)
def test_item_create_sets_core_attributes(
    module_path: str,
    cls_name: str,
    expected_classes: list,
    player: Player,
) -> None:
    """Ensure each item's factory sets core attributes and base stats."""
    mod = __import__(module_path, fromlist=[cls_name])
    cls = getattr(mod, cls_name)

    # Create the card
    card = cls.create(player=player)

    # Name matches the class-level name
    assert card.name == cls.name

    # Type includes Item
    assert CardTypeDef.item in card.types

    # Classes include the expected entries (subset check)
    for klass in expected_classes:
        assert klass in card.classes

    # Has an ItemStats effect
    stats_effect = next(
        (e for e in card.effects if isinstance(e, ItemStats)),
        None,
    )
    assert stats_effect is not None, "Missing ItemStats effect"
