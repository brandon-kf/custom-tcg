"""Create Cord instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Cord(Card):
    """Create Cord instances."""

    name: str = "Cord"

    @classmethod
    def create(cls: type[Cord], player: IPlayer) -> Cord:
        """Create a Cord instance."""
        cord = Cord(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.craft_material],
        )

        cord.actions.append(
            Play(card=cord, player=player),
        )

        cord.effects.append(
            ItemStats(
                name="Base stats",
                card=cord,
                heft=1,
                utility=2,
                uniquity=1,
            ),
        )

        return cord
