"""Create Trail instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Trail(Card):
    """Create Trail instances."""

    name: str = "Trail"

    @classmethod
    def create(cls: type[Trail], player: IPlayer) -> Trail:
        """Create a Trail instance."""
        trail = Trail(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.material, CardClassDef.base_material],
        )

        trail.actions.append(
            Play(card=trail, player=player),
        )

        trail.effects.append(
            ItemStats(
                name="Base stats",
                card=trail,
                heft=1000,
                utility=1,
                antiquity=1,
            ),
        )

        return trail
