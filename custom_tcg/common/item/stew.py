"""Create Stew instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Stew(Card):
    """Create Stew instances."""

    name: str = "Stew"

    @classmethod
    def create(cls: type[Stew], player: IPlayer) -> Stew:
        """Create a Stew instance."""
        stew = Stew(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.food, CardClassDef.processed_food],
        )

        stew.actions.append(
            Play(card=stew, player=player),
        )

        stew.effects.append(
            ItemStats(
                name="Base stats",
                card=stew,
                heft=2,
                uniquity=1,
            ),
        )

        return stew
