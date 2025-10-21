"""Create Metal instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Metal(Card):
    """Create Metal instances."""

    name: str = "Metal"

    @classmethod
    def create(cls: type[Metal], player: IPlayer) -> Metal:
        """Create a Metal instance."""
        metal = Metal(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.craft_material],
        )

        metal.actions.append(
            Play(card=metal, player=player),
        )

        metal.effects.append(
            ItemStats(
                name="Base stats",
                card=metal,
                heft=2,
                uniquity=1,
            ),
        )

        return metal
