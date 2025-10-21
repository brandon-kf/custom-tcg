"""Create Stone instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Stone(Card):
    """Create Stone instances."""

    name: str = "Stone"

    @classmethod
    def create(cls: type[Stone], player: IPlayer) -> Stone:
        """Create a Stone instance."""
        stone = Stone(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        stone.actions.append(
            Play(card=stone, player=player),
        )

        stone.effects.append(
            ItemStats(
                name="Base stats",
                card=stone,
                heft=1,
                antiquity=1,
            ),
        )

        # TODO: This should also be smeltable into an ore.  # noqa: E501, FIX002, TD002, TD003

        return stone
