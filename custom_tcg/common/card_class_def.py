"""Common card class definitions."""

from __future__ import annotations

from custom_tcg.common.card_type_def import CardTypeDef as CardTypeCommonDef
from custom_tcg.core.dimension import CardClass, CardTypeDef


class CardClassDef:
    """Dimensions of card classes."""

    rest = CardClass(
        name="rest",
        type_parents=[CardTypeDef.process],
        class_parents=[],
    )
    travel = CardClass(
        name="travel",
        type_parents=[CardTypeDef.process],
        class_parents=[],
    )
    attack = CardClass(
        name="attack",
        type_parents=[CardTypeDef.process],
        class_parents=[],
    )
    trade = CardClass(
        name="trade",
        type_parents=[CardTypeDef.process],
        class_parents=[],
    )

    human = CardClass(
        name="human",
        type_parents=[CardTypeDef.being],
        class_parents=[],
    )

    material = CardClass(
        name="material",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[],
    )
    base_material = CardClass(
        name="base material",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[material],
    )
    bulk_material = CardClass(
        name="bulk material",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[material],
    )
    craft_material = CardClass(
        name="craft material",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[material],
    )

    animal = CardClass(
        name="animal",
        type_parents=[CardTypeDef.being],
        class_parents=[],
    )
    fluffy_animal = CardClass(
        name="fluffy animal",
        type_parents=[CardTypeDef.being],
        class_parents=[animal],
    )

    food = CardClass(
        name="food",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[],
    )
    simple_food = CardClass(
        name="simple food",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[food],
    )
    processed_food = CardClass(
        name="processed food",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[food],
    )
    prepared_food = CardClass(
        name="prepared food",
        type_parents=[CardTypeCommonDef.item],
        class_parents=[food],
    )
