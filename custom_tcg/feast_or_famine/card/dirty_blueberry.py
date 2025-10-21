"""Create Dirty Blueberry instances."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.card_class_def import CardClassDef
from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.card.card import Card
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard, IPlayer


class DirtyBlueberry(Card):
    """Create Dirty Blueberry instances."""

    name: str = "Dirty Blueberry"

    @classmethod
    def create(cls: type[DirtyBlueberry], player: IPlayer) -> ICard:
        """Create a Dirty Blueberry instance."""
        dirty_blueberry: DirtyBlueberry = DirtyBlueberry(
            name=cls.name,
            player=player,
            types=[CardTypeDef.item],
            classes=[CardClassDef.food, CardClassDef.simple_food],
        )

        dirty_blueberry.actions.append(
            Play(card=dirty_blueberry, player=player),
        )

        dirty_blueberry.effects.append(
            ItemStats(
                name="Base stats",
                card=dirty_blueberry,
                heft=1,
            ),
        )

        return dirty_blueberry
