"""Create Pebble instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Pebble(Card):
    """Create Pebble instances."""

    name: str = "Pebble"

    @classmethod
    def create(cls: type[Pebble], player: IPlayer) -> Pebble:
        """Create a Pebble instance."""
        pebble = Pebble(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        pebble.actions.append(
            Play(card=pebble, player=player),
        )

        pebble.effects.append(
            ItemStats(
                name="Base stats",
                card=pebble,
                heft=1,
                antiquity=1,
            ),
        )

        return pebble
